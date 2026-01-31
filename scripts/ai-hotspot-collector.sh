#!/bin/bash
# AI Hotspot Collector - 修复发送

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."
CONFIG_FILE="$REPO_DIR/config.yaml"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

command -v jq >/dev/null 2>&1 || { log "jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "curl 未安装"; exit 1; }

# 读取配置
if [ -f "$CONFIG_FILE" ]; then
    log "读取配置文件: $CONFIG_FILE"
else
    log "配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# Mock 数据
COLLECTED_FILE="/tmp/hotspot-$$.txt"
cat > "$COLLECTED_FILE" << 'MOCK'
🏢 中美模型厂商

1. DeepSeek-V3 模型发布
   DeepSeek-V3 在多项基准测试中表现优异，推理能力显著提升，开源社区反响热烈
   https://github.com/deepseek-ai/DeepSeek-V3

2. OpenAI o1 模型系列发布
   OpenAI 专注于复杂推理任务，在编程和数学问题上表现突出
   https://openai.com

🧠 大模型热点

1. GPT-4.1 性能优化
   OpenAI 更新 GPT-4.1，降低成本和延迟，提升响应质量
   https://openai.com
MOCK

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
    log "获取 token 成功: ${token:0:10}..."
    
    log "步骤2: 发送消息到群聊..."
    
    # 读取内容并转义
    content_raw=$(cat "$COLLECTED_FILE")
    content_json=$(echo "$content_raw" | jq -Rs 'sub("\n"; "\\n") | sub("\""; "\\\"")')
    
    log "内容长度: ${#content_json} 字符"
    
    # 构建 JSON
    json_data="{\"receive_id\": \"$FEISHU_GROUP_ID\", \"msg_type\": \"text\", \"content\": {\"text\": $content_json}}"
    
    log "发送请求..."
    
    msg_resp=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    http_code=$(echo "$msg_resp" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$msg_resp" | grep -v "HTTP_CODE:")
    
    log "HTTP 状态码: $http_code"
    log "响应体: $body"
    
    if [ "$http_code" = "200" ] || [ "$(echo "$body" | jq -r '.code')" = "0" ]; then
        log "发送成功！✅"
    else
        log "发送失败"
    fi
else
    log "飞书参数未配置"
fi

rm -f "$COLLECTED_FILE" 2>/dev/null || true
log "=== 完成 ==="
