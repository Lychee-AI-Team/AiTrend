#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯，并发送到飞书

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"
BRAVE_API_KEY_FILE="$SCRIPT_DIR/../.brave-api-key"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local msg="[$timestamp] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# 检查必要的工具
command -v jq >/dev/null 2>&1 || { log "❌ 错误: jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "❌ 错误: curl 未安装"; exit 1; }

# 获取 API Keys
HAS_BRAVE_API=false
if [ -n "$BRAVE_API_KEY" ]; then
    log "✅ 使用环境变量中的 Brave API Key"
    HAS_BRAVE_API=true
elif [ -f "$BRAVE_API_KEY_FILE" ]; then
    BRAVE_API_KEY=$(cat "$BRAVE_API_KEY_FILE" | tr -d '\n')
    export BRAVE_API_KEY
    log "✅ 使用本地文件中的 Brave API Key"
    HAS_BRAVE_API=true
else
    log "⚠️  未找到 Brave API Key，将使用 mock 数据模式"
fi

# 获取 Webhook URL
WEBHOOK_URL="${WEBHOOK_URL:-}"
if [ -z "$WEBHOOK_URL" ]; then
    log "⚠️  WEBHOOK_URL 未设置"
fi

log "🔥 开始收集 AI 热点资讯..."

# 尝试从配置文件读取搜索类别
SEARCH_CATEGORIES=()
if [ -f "$CONFIG_FILE" ] && command -v yq >/dev/null 2>&1; then
    log "📖 从 config.yaml 读取分类配置"

    # 使用 yq 读取每个分类
    while IFS= read -r name; do
        icon=$(yq eval ".CATEGORIES[] | select(.name == \"$name\") | .icon" "$CONFIG_FILE" 2>/dev/null)
        keywords_str=$(yq eval ".CATEGORIES[] | select(.name == \"$name\") | .keywords | join(\"|\")" "$CONFIG_FILE" 2>/dev/null)

        if [ -n "$keywords_str" ]; then
            SEARCH_CATEGORIES+=("${icon} ${name}|${keywords_str}")
            log "   分类: ${icon} ${name}"
        fi
    done < <(yq eval '.CATEGORIES[].name' "$CONFIG_FILE" 2>/dev/null)
fi

# 如果配置文件读取失败，使用默认类别
if [ ${#SEARCH_CATEGORIES[@]} -eq 0 ]; then
    log "⚠️  使用默认搜索类别"
    SEARCH_CATEGORIES=(
        "🤖 中美模型厂商|OpenAI|Anthropic|Google Gemini|DeepSeek|Meta AI"
        "🧠 大模型热点|GPT-4|Claude 3|Qwen|ChatGLM|LLM reasoning"
        "🔧 AI Agent|AI Agent|Claude Code|LangGraph|AutoGPT|CrewAI"
        "🛠️ AI 应用工具|ChatGPT|GitHub Copilot|Cursor IDE|AI coding"
        "📰 AI 行业新闻|AI news 2026|artificial intelligence|AI technology"
        "⚖️ AI 安全与监管|AI safety|AI regulation|AI ethics"
    )
fi

# 收集结果
declare -a ALL_ITEMS=()
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ "$HAS_BRAVE_API" = true ]; then
    # 使用 Brave Search API
    for category_line in "${SEARCH_CATEGORIES[@]}"; do
        IFS='|' read -r category_name rest <<< "$category_line"
        queries="$rest"

        log "📂 正在搜索: $category_name"

        count=1
        for query in $queries; do
            [ $count -gt 3 ] && break
            log "   搜索关键词: $query"

            # 调用 Brave Search API
            response=$(timeout 10 curl -s "https://api.search.brave.com/res/v1/web/search?q=$query&count=3&freshness=pt" \
                -H "Accept: application/json" \
                -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true

            if [ -z "$response" ]; then
                log "   ⚠️  API 请求超时"
                continue
            fi

            # 解析结果
            while IFS= read -r item_json; do
                [ $count -gt 3 ] && break
                title=$(echo "$item_json" | jq -r '.title // "无标题"' | cut -c1-100)
                desc=$(echo "$item_json" | jq -r '.description // "暂无描述"' | cut -c1-150)
                url=$(echo "$item_json" | jq -r '.url // ""')

                if [ -n "$title" ] && [ "$title" != "null" ]; then
                    ALL_ITEMS+=("{\"title\":\"$title\",\"summary\":\"$desc\",\"url\":\"$url\",\"category\":\"$category_name\"}")
                    log "   ✓ ${title:0:40}..."
                    ((count++))
                fi
            done < <(jq -r '.web.results[] // .results[] | @json' 2>/dev/null <<< "$response" || echo "")

            sleep 1
        done
    done
else
    # Mock 数据模式
    log "📋 使用 mock 数据模式"
    ALL_ITEMS+=("{\"title\":\"DeepSeek-V3 发布\",\"summary\":\"DeepSeek-V3 在多项基准测试中表现优异\",\"url\":\"https://github.com/deepseek-ai\",\"category\":\"🤖 中美模型厂商\"}")
    ALL_ITEMS+=("{\"title\":\"OpenAI o1 模型系列\",\"summary\":\"专注于复杂推理任务\",\"url\":\"https://openai.com\",\"category\":\"🤖 中美模型厂商\"}")
    ALL_ITEMS+=("{\"title\":\"Cursor AI IDE 爆火\",\"summary\":\"集成 GPT-4 和 Claude 的开发者工具\",\"url\":\"https://cursor.sh\",\"category\":\"🔧 AI Agent\"}")
fi

# 发送到 webhook
if [ -n "$WEBHOOK_URL" ]; then
    log "📡 正在发送到 webhook..."

    # 构建 JSON
    ITEMS_JSON=$(IFS=,; echo "${ALL_ITEMS[*]}")
    ITEMS_JSON="[$ITEMS_JSON]"

    PAYLOAD=$(cat <<EOF
{
  "title": "AI 热点资讯",
  "summary": "AI 行业热点汇总",
  "items": $ITEMS_JSON,
  "timestamp": "$TIMESTAMP"
}
EOF
)

    log "   发送数据: ${#PAYLOAD} 字符"

    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")

    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | grep -v "HTTP_CODE:")

    log "   HTTP 状态码: $http_code"
    log "   响应: $body"

    if [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
        log "✅ 发送成功！共 ${#ALL_ITEMS[@]} 条"
    else
        log "⚠️  发送失败，状态码: $http_code"
    fi
else
    log "⚠️  WEBHOOK_URL 未设置，跳过发送"
    log "   收集到 ${#ALL_ITEMS[@]} 条数据"
fi

log "✅ 脚本执行完成"
