#!/bin/bash
# AI Hotspot Collector - 完整功能版

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

FEISHU_APP_ID="${FEISHU_APP_ID:-}"
FEISHU_SECRET_KEY="${FEISHU_SECRET_KEY:-}"
FEISHU_GROUP_ID="${FEISHU_GROUP_ID:-}"

log "=== 收集 AI 热点资讯 ==="

SEARCH_CATEGORIES=(
    "中美模型厂商|OpenAI|Anthropic|Google|DeepSeek"
    "大模型热点|GPT|Claude|DeepSeek|Qwen"
    "创始人动态|Sam Altman|李开复"
    "Agent动态|Claude Code|LangGraph"
)

COLLECTED_FILE="/tmp/hotspot-$$.txt"
echo "" > "$COLLECTED_FILE"

if [ -n "$BRAVE_API_KEY" ]; then
    log "使用 Brave Search API"
    for cat in "${SEARCH_CATEGORIES[@]}"; do
        IFS='|' read -r name queries <<< "$cat"
        log "搜索: $name"
        echo "" >> "$COLLECTED_FILE"
        echo "## $name" >> "$COLLECTED_FILE"
        count=1
        for q in $queries; do
            [ $count -gt 3 ] && break
            resp=$(timeout 15 curl -s "https://api.search.brave.com/res/v1/web/search?q=$q&count=5&freshness=pm" \
                -H "Accept: application/json" \
                -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true
            if echo "$resp" | jq -e '.web.results' > /dev/null 2>&1; then
                while IFS= read -r item; do
                    [ $count -gt 3 ] && break
                    title=$(echo "$item" | jq -r '.title' | cut -c1-80)
                    desc=$(echo "$item" | jq -r '.description' | cut -c1-200)
                    url=$(echo "$item" | jq -r '.url')
                    [ -n "$title" ] && [ "$title" != "null" ] && {
                        echo "$count. **$title**" >> "$COLLECTED_FILE"
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
    done
else
    log "使用 mock 数据"
    cat > "$COLLECTED_FILE" << 'MOCK'
## AI 热点资讯

1. **DeepSeek-V3 发布**
   DeepSeek-V3 在多项基准测试中表现优异。
   https://github.com/deepseek-ai/DeepSeek-V3

2. **OpenAI o1 模型发布**
   OpenAI 发布 o1 系列，专注复杂推理。
   https://openai.com
MOCK
fi

if [ -n "$GEMINI_API_KEY" ] && command -v gemini >/dev/null 2>&1; then
    log "使用 Gemini 翻译..."
    TRANSLATED="/tmp/translated-$$.txt"
    gemini --model gemini-2.5-flash "翻译成中文，保持格式，简洁专业：$(cat "$COLLECTED_FILE")" 2>&1 | tee "$TRANSLATED"
    REPORT_FILE="$TRANSLATED"
else
    REPORT_FILE="$COLLECTED_FILE"
fi

log "=== 发送到飞书群聊 ==="

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
    content=$(cat "$REPORT_FILE")
    
    msg_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"receive_id\": \"$FEISHU_GROUP_ID\",
            \"msg_type\": \"text\",
            \"content\": \"{\\\"text\\\": $(echo "$content" | jq -Rs .)}\"
        }")
    
    log "响应: $(echo "$msg_resp" | jq -r '.msg')"
    
    if [ "$(echo "$msg_resp" | jq -r '.code')" = "0" ]; then
        log "发送成功！✅"
    else
        log "发送失败: $(echo "$msg_resp" | jq -r '.msg')"
    fi
else
    log "飞书参数未配置"
fi

rm -f "$COLLECTED_FILE" "$TRANSLATED" 2>/dev/null || true
log "=== 完成 ==="
