#!/bin/bash
# AI Hotspot Collector - 修复飞书 API 调用

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

command -v jq >/dev/null 2>&1 || { log "jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "curl 未安装"; exit 1; }

FEISHU_APP_ID="${FEISHU_APP_ID:-}"
FEISHU_SECRET_KEY="${FEISHU_SECRET_KEY:-}"
FEISHU_GROUP_ID="${FEISHU_GROUP_ID:-}"

log "FEISHU_APP_ID: ${FEISHU_APP_ID:0:10}..."
log "FEISHU_GROUP_ID: $FEISHU_GROUP_ID"

get_token() {
    log "获取 tenant_access_token..."
    local resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")
    
    log "auth resp: $resp"
    
    # 检查是否有效 JSON
    if ! echo "$resp" | jq -e . >/dev/null 2>&1; then
        log "获取 token 失败: 非 JSON 响应"
        return 1
    fi
    
    local code=$(echo "$resp" | jq -r '.code')
    if [ "$code" != "0" ]; then
        log "获取 token 失败: $(echo "$resp" | jq -r '.msg')"
        return 1
    fi
    
    echo "$resp" | jq -r '.tenant_access_token'
}

get_chat_id() {
    local token="$1"
    log "获取 chat_id..."
    
    local resp=$(curl -s "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50" \
        -H "Authorization: Bearer $token")
    
    log "chats resp: $resp"
    
    if ! echo "$resp" | jq -e . >/dev/null 2>&1; then
        log "获取 chats 失败: 非 JSON"
        echo "$FEISHU_GROUP_ID"
        return
    fi
    
    echo "$resp" | jq -r ".data.items[] | select(.chat_id == \"$FEISHU_GROUP_ID\") | .chat_id" 2>/dev/null | head -1
}

send_feishu() {
    local token="$1"
    local chat_id="$2"
    local content="$3"
    
    log "发送消息到 chat_id: $chat_id"
    log "content length: ${#content}"
    
    # 准备内容（转义 JSON）
    local escaped_content=$(echo "$content" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g' | tr '\n' ' ')
    
    local data="{\"receive_id\": \"$chat_id\", \"msg_type\": \"text\", \"content\": \"{\\\"text\\\": \\\"$escaped_content\\\"}\"}"
    
    log "request data: $data"
    
    local resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    log "send resp: $resp"
    echo "$resp"
}

log "开始收集 AI 热点资讯..."

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
## 中美模型厂商

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
    gemini --model gemini-2.5-flash "翻译成中文，保持格式，简洁专业，1000字以内：$(cat "$COLLECTED_FILE")" 2>&1 | tee "$TRANSLATED"
    REPORT_FILE="$TRANSLATED"
else
    log "跳过翻译"
    REPORT_FILE="$COLLECTED_FILE"
fi

if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_SECRET_KEY" ] && [ -n "$FEISHU_GROUP_ID" ]; then
    log "发送到飞书..."
    
    token=$(get_token) || { log "获取 token 失败"; exit 1; }
    chat_id=$(get_chat_id "$token") || { log "获取 chat_id 失败"; exit 1; }
    
    content=$(cat "$REPORT_FILE")
    result=$(send_feishu "$token" "$chat_id" "$content")
    
    if echo "$result" | jq -e '.code == 0' > /dev/null 2>&1; then
        log "发送成功！"
    else
        log "发送失败: $(echo "$result" | jq -r '.msg // "unknown error"')"
    fi
else
    log "飞书参数未配置"
fi

rm -f "$COLLECTED_FILE" "$TRANSLATED" 2>/dev/null || true
log "完成"
