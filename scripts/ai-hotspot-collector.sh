#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯，并用 Gemini 翻译

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"
BRAVE_API_KEY_FILE="$SCRIPT_DIR/../.brave-api-key"
GEMINI_API_KEY_FILE="$SCRIPT_DIR/../.gemini-api-key"

# 日志函数 - 直接输出到文件和 stdout，避免 tee 导致的问题
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local msg="[$timestamp] $*"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

# 检查必要的工具
command -v jq >/dev/null 2>&1 || { log "❌ 错误: jq 未安装"; exit 1; }
command -v curl >/dev/null 2>&1 || { log "❌ 错误: curl 未安装"; exit 1; }
command -v gemini >/dev/null 2>&1 || { log "❌ 错误: gemini CLI 未安装"; exit 1; }

# 优先从环境变量获取 API Keys (GitHub Actions)
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

if [ -n "$GEMINI_API_KEY" ]; then
    log "✅ 使用环境变量中的 Gemini API Key"
elif [ -f "$GEMINI_API_KEY_FILE" ]; then
    GEMINI_API_KEY=$(cat "$GEMINI_API_KEY_FILE" | tr -d '\n')
    export GEMINI_API_KEY
    log "✅ 使用本地文件中的 Gemini API Key"
else
    log "⚠️  警告: 未找到 Gemini API Key，将跳过翻译"
fi

log "🔥 开始收集 AI 热点资讯..."

# 定义搜索类别
SEARCH_CATEGORIES=(
    "🏢 中美模型厂商|OpenAI|Anthropic|Google|Meta|DeepSeek"
    "🧠 大模型热点|GPT-4|Claude|DeepSeek|Qwen|ChatGLM"
    "👤 创始人/CEO|Sam Altman|Dario Amodei|李开复"
    "🤖 最热 Agent|AI agent|Claude Code|LangGraph"
)

# 临时文件存储收集到的内容
COLLECTED_FILE="/tmp/hotspot-collected-$$.txt"

# 收集所有搜索结果
collect_results() {
    for category_line in "${SEARCH_CATEGORIES[@]}"; do
        IFS='|' read -r category_name rest <<< "$category_line"
        queries="$rest"

        log "📂 正在搜索: $category_name"
        echo "" >> "$COLLECTED_FILE"
        echo "## $category_name" >> "$COLLECTED_FILE"

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

            # 提取搜索结果 - 先保存到临时文件，避免管道问题
            echo "$response" > /tmp/brave_response_$$.json

            # 检查响应格式
            if jq -e '.web.results' /tmp/brave_response_$$.json > /dev/null 2>&1; then
                log "   响应格式: .web.results"
                # 将结果保存到临时文件
                jq -r '.web.results[] | {
                    title: (.title // "无标题"),
                    description: (.description // "暂无描述"),
                    url: (.url // "")
                }' /tmp/brave_response_$$.json >> /tmp/hotspot_items_$$.json
            elif jq -e '.results' /tmp/brave_response_$$.json > /dev/null 2>&1; then
                log "   响应格式: .results (兼容格式）"
                jq -r '.results[] | {
                    title: (.title // "无标题"),
                    description: (.description // "暂无描述"),
                    url: (.url // "")
                }' /tmp/brave_response_$$.json >> /tmp/hotspot_items_$$.json
            else
                log "   ⚠️ 未知响应格式，保存原始响应"
                # 保存原始文本以防 JSON 解析失败
                echo "[]}" > /tmp/hotspot_items_$$.json
            fi

                count=0
                while IFS= read -r title_desc; do
                    [ $count -ge 3 ] && break
                    if [ -n "$title_desc" ]; then
                        title=$(echo "$title_desc" | jq -r '.title' | cut -c1-80)
                        desc=$(echo "$title_desc" | jq -r '.description' | cut -c1-150)
                        url=$(echo "$title_desc" | jq -r '.url')
                        echo "$count. **$title**" >> "$COLLECTED_FILE"
                        echo "   $desc" >> "$COLLECTED_FILE"
                        echo "   🔗 $url" >> "$COLLECTED_FILE"
                        echo "" >> "$COLLECTED_FILE"
                        log "   ✓ $count. ${title:0:50}..."
                        ((count++))
                    fi
                done < /tmp/hotspot_items_$$.json

                rm -f /tmp/hotspot_items_$$.json
            else
                log "   ⚠️  API 响应格式错误或无结果"
            fi

            rm -f /tmp/brave_response_$$.json
            sleep 1
        done
    done
}

# 收集原始英文内容
log "📋 收集原始内容..."
collect_results

# 使用 Gemini 翻译和总结
if [ -n "$GEMINI_API_KEY" ]; then
    log "🌐 正在使用 Gemini 翻译和总结..."
    
    TRANSLATED_FILE="/tmp/hotspot-translated-$$.md"
    
    # 使用 Gemini 翻译
    gemini --model gemini-2.5-flash "请将以下 AI 热点资讯翻译成中文，保持原有的标题、描述和链接格式。使用简洁、专业的语言风格。不要添加额外的评论或解释。

---
$(cat "$COLLECTED_FILE")
---" 2>&1 | tee "$TRANSLATED_FILE"
    
    if [ -s "$TRANSLATED_FILE" ]; then
        log "✅ 翻译完成"
        REPORT_FILE="$TRANSLATED_FILE"
    else
        log "⚠️  翻译失败，使用原始内容"
        REPORT_FILE="$COLLECTED_FILE"
    fi
else
    log "⚠️  跳过翻译，使用原始英文内容"
    REPORT_FILE="$COLLECTED_FILE"
fi

# 如果设置了 WEBHOOK_URL，发送到 webhook
if [ -n "$WEBHOOK_URL" ]; then
    log "📡 正在发送到 webhook: $WEBHOOK_URL"

    # 临时关闭 set -e，防止 webhook 失败导致脚本退出
    set +e

    # 将报告内容转换为 JSON 格式
    # 提取所有标题和链接
    items_json=$(jq -Rs 'split("\n\n## ") | 
        map(
            split("\n") | 
            map(select(length > 0)) |
            map(
                if test("^[0-9]+\\. \\*\\*\\*") then
                    {
                        title: (sub("^[0-9]+\\. \\*\\*\\*"; "") | sub("\\*\\*$"; "")),
                        summary: (.[1:] // ""),
                        url: (if .[1:] then
                            (.[1:] | scan("🔗 (.*)")[0] // "")
                        else "" end)
                    }
                else empty end
            ) | .[]
        ) | .[]' "$REPORT_FILE")

    webhook_response=$(timeout 10 curl -s -w '\nHTTP_CODE:%{http_code}' \
        -X POST "$WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"title\":\"🔥 AI 热点资讯\",\"items\":$items_json,\"summary\":\"AI 热点\"}" 2>&1)

    CURL_EXIT_CODE=$?

    # 重新启用 set -e
    set -e

    http_code=$(echo "$webhook_response" | grep -o 'HTTP_CODE:[0-9]*' 2>/dev/null | cut -d: -f2 || echo "000")

    if [ "$CURL_EXIT_CODE" -eq 0 ] && { [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; }; then
        log "✅ Webhook 发送成功 (HTTP $http_code)"
    else
        log "⚠️  Webhook 发送失败 (CURL_EXIT_CODE=$CURL_EXIT_CODE, HTTP=$http_code)"
        log "⚠️  请检查 WEBHOOK_URL 是否正确且服务器可访问"
    fi
else
    log "⚠️  WEBHOOK_URL 未设置，跳过发送"
fi

# 清理临时文件
rm -f "$COLLECTED_FILE" "$TRANSLATED_FILE" 2>/dev/null || true

log "✅ 脚本执行完成"
