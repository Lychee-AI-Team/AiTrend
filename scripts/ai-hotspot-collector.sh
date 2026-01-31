#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"
BRAVE_API_KEY_FILE="$SCRIPT_DIR/../.brave-api-key"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $*" | tee -a "$LOG_FILE"
}

# 检查必要的工具
command -v jq >/dev/null 2>&1 || { log "❌ 错误: jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "❌ 错误: curl 未安装"; exit 1; }

# 优先从环境变量获取 Brave API Key (GitHub Actions)
if [ -n "$BRAVE_API_KEY" ]; then
    log "✅ 使用环境变量中的 Brave API Key"
elif [ -f "$BRAVE_API_KEY_FILE" ]; then
    BRAVE_API_KEY=$(cat "$BRAVE_API_KEY_FILE" | tr -d '\n')
    export BRAVE_API_KEY
    log "✅ 使用本地文件中的 Brave API Key"
else
    log "❌ 错误: 无法获取 Brave API Key (环境变量或文件)"
    exit 1
fi

log "🔥 开始收集 AI 热点资讯..."

# 定义搜索类别
SEARCH_CATEGORIES=(
    "🏢 中美模型厂商|OpenAI|Anthropic|Google|Meta|DeepSeek"
    "🧠 大模型热点|GPT-4|Claude|DeepSeek|Qwen|ChatGLM"
    "👤 创始人/CEO|Sam Altman|Dario Amodei|李开复"
    "🤖 最热 Agent|AI agent|Claude Code|LangGraph"
)

# 生成报告
BEIJING_TIME=$(TZ='Asia/Shanghai' date '+%Y年%m月%d日 %H:%M')
REPORT_FILE="$SCRIPT_DIR/hotspot-report-$(date +%Y%m%d-%H%M%S).md"

{
    echo "🔥 AI 热点资讯"
    echo ""
    echo "时间: $BEIJING_TIME (北京时间)"
    echo ""
} > "$REPORT_FILE"

# 遍历所有类别
for category_line in "${SEARCH_CATEGORIES[@]}"; do
    IFS='|' read -r category_name rest <<< "$category_line"
    queries="$rest"
    
    log "📂 正在搜索: $category_name"
    echo "$category_name" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    count=1
    for query in $queries; do
        [ $count -gt 5 ] && break
        log "   搜索关键词: $query"

        # 调用 Brave Search API
        response=$(timeout 10 curl -s "https://api.search.brave.com/res/v1/web/search?q=$query&count=3&freshness=pt" \
            -H "Accept: application/json" \
            -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true

        # 检查响应
        if [ -z "$response" ]; then
            log "   ⚠️  API 请求超时或无响应"
            continue
        fi

        # 提取搜索结果
        if echo "$response" | jq -e '.web.results' > /dev/null 2>&1; then
            echo "$response" | jq -r '.web.results[] | "\(.title // "无标题") - \(.description // "暂无描述") 🔗 \(.url)"' 2>/dev/null | \
            while IFS= read -r line; do
                if [ -n "$line" ]; then
                    echo "$count. $line" >> "$REPORT_FILE"
                    log "   ✓ $count. ${line:0:80}..."
                    ((count++))
                    [ $count -gt 5 ] && break
                fi
            done
        else
            log "   ⚠️  API 响应格式错误或无结果"
        fi

        sleep 1
    done

    echo "" >> "$REPORT_FILE"
done

{
    echo "---"
    echo "*资讯来源: Brave Search | 数据收集时间: $(date '+%Y-%m-%d')*"
} >> "$REPORT_FILE"

log "📊 报告已生成: $REPORT_FILE"

# 如果设置了 WEBHOOK_URL，发送到 webhook
if [ -n "$WEBHOOK_URL" ]; then
    log "📡 正在发送到 webhook: $WEBHOOK_URL"

    # 临时关闭 set-e，防止 webhook 失败导致脚本退出
    set +e

    webhook_response=$(timeout 10 curl -s -w '\nHTTP_CODE:%{http_code}' \
        -X POST "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"title\":\"🔥 AI 热点资讯\",\"text\":\"$(cat "$REPORT_FILE" | jq -Rs .)\"}" 2>&1)

    CURL_EXIT_CODE=$?

    # 重新启用 set-e
    set -e

    http_code=$(echo "$webhook_response" | grep -o 'HTTP_CODE:[0-9]*' 2>/dev/null | cut -d: -f2 || echo "000")

    if [ "$CURL_EXIT_CODE" -eq 0 ] && [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
        log "✅ Webhook 发送成功 (HTTP $http_code)"
    else
        log "⚠️  Webhook 发送失败 (CURL_EXIT_CODE=$CURL_EXIT_CODE, HTTP=$http_code)"
        log "⚠️  请检查 WEBHOOK_URL 是否正确且服务器可访问"
    fi
else
    log "⚠️  WEBHOOK_URL 未设置，跳过发送"
fi

log "✅ 脚本执行完成"
