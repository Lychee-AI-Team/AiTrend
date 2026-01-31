#!/bin/bash
# AI Hotspot Collector - 使用 open_id 替代 chat_id

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

log "=== 配置检查 ==="
log "FEISHU_GROUP_ID: $FEISHU_GROUP_ID"

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
    gemini --model gemini-2.5-flash "翻译成中文，保持格式，简洁专业，800字以内：$(cat "$COLLECTED_FILE")" 2>&1 | tee "$TRANSLATED"
    REPORT_FILE="$TRANSLATED"
else
    log "跳过翻译"
    REPORT_FILE="$COLLECTED_FILE"
fi

log "=== 发送到飞书 ==="

if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_SECRET_KEY" ] && [ -n "$FEISHU_GROUP_ID" ]; then
    log "步骤1: 获取 tenant_access_token..."
    resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")
    log "auth: ${resp:0:60}..."
    
    token=$(echo "$resp" | jq -r '.tenant_access_token')
    if [ "$(echo "$resp" | jq -r '.code')" != "0" ]; then
        log "获取 token 失败"
        exit 1
    fi
    log "获取 token 成功"
    
    log "步骤2: 获取群聊的 open_id..."
    chats_resp=$(curl -s "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50" \
        -H "Authorization: Bearer $token")
    log "chats: ${chats_resp:0:100}..."
    
    # 查找群聊并获取 open_id
    open_id=$(echo "$chats_resp" | jq -r ".data.items[] | select(.chat_id == \"$FEISHU_GROUP_ID\") | .open_id" 2>/dev/null | head -1)
    
    if [ -z "$open_id" ] || [ "$open_id" = "null" ]; then
        log "未找到群聊 open_id，使用 chat_id 发送"
        open_id="$FEISHU_GROUP_ID"
        id_type="chat_id"
    else
        log "找到 open_id: ${open_id:0:20}..."
        id_type="open_id"
    fi
    
    log "步骤3: 发送消息 (id_type: $id_type)..."
    content=$(cat "$REPORT_FILE")
    
    json_data=$(jq -n \
        --arg rid "$open_id" \
        --arg type "$id_type" \
        --arg msgtype "text" \
        --arg txt "$content" \
        '{
            receive_id: $rid,
            receive_id_type: $type,
            msg_type: $msgtype,
            content: ($txt | tojson)
        }')
    
    msg_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$json_data")
    
    log "响应: $msg_resp"
    
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
