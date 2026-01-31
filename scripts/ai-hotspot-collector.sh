#!/bin/bash
# AI Hotspot Collector - 修复配置文件路径

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# 检查必要工具
command -v jq >/dev/null 2>&1 || { log "jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "curl 未安装"; exit 1; }

# 修复路径问题 - 直接使用绝对路径
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$REPO_DIR/config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    log "读取配置文件: $CONFIG_FILE"
else
    log "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 获取 Brave API Key
BRAVE_API_KEY="${BRAVE_API_KEY:-}"
if [ -n "$BRAVE_API_KEY" ]; then
    HAS_BRAVE_API=true
    log "使用环境变量 Brave API Key"
else
    HAS_BRAVE_API=false
    log "Brave API Key 未配置，使用 mock 数据"
fi

log "=== 开始收集 AI 热点资讯 ==="

COLLECTED_FILE="/tmp/hotspot-$$.txt"
echo "" > "$COLLECTED_FILE"

if [ "$HAS_BRAVE_API" = true ]; then
    log "使用 Brave Search API"
    
    # 解析配置文件中的分类
    python3 << PYTHON_EOF
import yaml

with open('/home/runner/work/AiTrend/AiTrend/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for cat in config.get('CATEGORIES', []):
    name = cat.get('name', '')
    icon = cat.get('icon', '')
    keywords = ' '.join(cat.get('keywords', []))
    print(f"{icon} {name}|{keywords}")
PYTHON_EOF
    
    while IFS='|' read -r icon_name keywords; do
        IFS=' ' read -r icon name <<< "$icon_name"
        [ -z "$name" ] && continue
        
        log "搜索: $icon $name"
        echo "" >> "$COLLECTED_FILE"
        echo "$icon $name" >> "$COLLECTED_FILE"
        
        count=1
        for q in $keywords; do
            [ $count -gt 3 ] && break
            resp=$(timeout 15 curl -s "https://api.search.brave.com/res/v1/web/search?q=$q&count=3&freshness=pm" \
                -H "Accept: application/json" \
                -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true
            
            if echo "$resp" | jq -e '.web.results' > /dev/null 2>&1; then
                while IFS= read -r item; do
                    [ $count -gt 3 ] && break
                    title=$(echo "$item" | jq -r '.title' | cut -c1-80)
                    desc=$(echo "$item" | jq -r '.description' | cut -c1-200)
                    url=$(echo "$item" | jq -r '.url')
                    [ -n "$title" ] && [ "$title" != "null" ] && {
                        echo "$count. $title" >> "$COLLECTED_FILE"
                        echo "   $desc" >> "$COLLECTED_FILE"
                        echo "   $url" >> "$COLLECTED_FILE"
                        echo "" >> "$COLLECTED_FILE"
                        log "OK ${title:0:50}..."
                        ((count++))
                    }
                done < <(echo "$resp" | jq -r '.web.results[] | @json' 2>/dev/null)
            fi
            sleep 1
        done
    done < <(python3 << 'PYTHON_EOF'
import yaml

with open('/home/runner/work/AiTrend/AiTrend/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

for cat in config.get('CATEGORIES', []):
    name = cat.get('name', '')
    icon = cat.get('icon', '')
    keywords = ' '.join(cat.get('keywords', []))
    print(f"{icon} {name}|{keywords}")
PYTHON_EOF
)
else
    log "使用 mock 数据"
    cat > "$COLLECTED_FILE" << 'MOCK'
🏢 中美模型厂商

1. DeepSeek-V3 模型发布
   DeepSeek-V3 在多项基准测试中表现优异，推理能力显著提升
   https://github.com/deepseek-ai/DeepSeek-V3

2. OpenAI o1 模型系列发布
   OpenAI 专注于复杂推理任务，在编程和数学问题上表现突出
   https://openai.com

🧠 大模型热点

1. GPT-4.1 性能优化
   OpenAI 更新 GPT-4.1，降低成本和延迟，提升响应质量
   https://openai.com

2. Claude 3.5 Sonnet 升级
   Anthropic 提升代码生成和长文本处理能力
   https://www.anthropic.com
MOCK
fi

log "=== 发送到飞书群聊 ==="

FEISHU_APP_ID="${FEISHU_APP_ID:-}"
FEISHU_SECRET_KEY="${FEISHU_SECRET_KEY:-}"
FEISHU_GROUP_ID="${FEISHU_GROUP_ID:-}"

if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_SECRET_KEY" ] && [ -n "$FEISHU_GROUP_ID" ]; then
    log "步骤1: 获取 tenant_access_token..."
    resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")
    
    if [ "$(echo "$resp" | jq -r '.code')" != "0" ]; then
        log "获取 token 失败: $(echo "$resp" | jq -r '.msg')"
        exit 1
    fi
    token=$(echo "$resp" | jq -r '.tenant_access_token')
    log "获取 token 成功"
    
    log "步骤2: 发送消息到群聊..."
    content=$(cat "$COLLECTED_FILE")
    
    msg_resp=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"receive_id\": \"$FEISHU_GROUP_ID\",
            \"msg_type\": \"text\",
            \"content\": \"{\\\"text\\\": $(echo "$content" | jq -Rs .)}\"
        }")
    
    http_code=$(echo "$msg_resp" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$msg_resp" | grep -v "HTTP_CODE:")
    
    log "HTTP 状态码: $http_code"
    
    if [ "$http_code" = "200" ] || [ "$(echo "$body" | jq -r '.code')" = "0" ]; then
        log "发送成功！✅"
    else
        log "发送失败: $(echo "$body" | jq -r '.msg')"
    fi
else
    log "飞书参数未配置"
fi

rm -f "$COLLECTED_FILE" 2>/dev/null || true
log "=== 完成 ==="
