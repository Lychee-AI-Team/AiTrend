#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯，并发送到飞书

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"
BRAVE_API_KEY_FILE="$SCRIPT_DIR/../.bravi-api-key"

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

# 获取飞书配置
FEISHU_APP_ID="${FEISHU_APP_ID:-}"
FEISHU_SECRET_KEY="${FEISHU_SECRET_KEY:-}"
FEISHU_GROUP_ID="${FEISHU_GROUP_ID:-}"
HAS_FEISHU=false
if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_SECRET_KEY" ] && [ -n "$FEISHU_GROUP_ID" ]; then
    HAS_FEISHU=true
    log "✅ 飞书配置已就绪"
else
    log "⚠️  飞书配置不完整"
fi

log "🔥 开始收集 AI 热点资讯..."

# 尝试从配置文件读取搜索类别
SEARCH_CATEGORIES=()
if [ -f "$CONFIG_FILE" ] && command -v yq >/dev/null 2>&1; then
    log "📖 从 config.yaml 读取分类配置"

    # 使用 grep+sed 解析 YAML（更可靠）
    current_name=""
    current_icon=""
    keywords=""

    while IFS= read -r line; do
        # 检测新分类开始
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*\"([^\"]+)\" ]]; then
            # 保存上一个分类
            if [ -n "$current_name" ] && [ -n "$keywords" ]; then
                SEARCH_CATEGORIES+=("${current_icon} ${current_name}|${keywords}")
                log "   分类: ${current_icon} ${current_name} (${keywords})"
            fi
            current_name="${BASH_REMATCH[1]}"
            current_icon=""
            keywords=""
        # 检测 icon
        elif [[ "$line" =~ ^[[:space:]]*icon:[[:space:]]*\"([^\"]+)\" ]]; then
            current_icon="${BASH_REMATCH[1]}"
        # 检测 keyword - 更宽松的匹配
        elif [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\"([^\"]+)\" ]]; then
            keyword="${BASH_REMATCH[1]}"
            if [ -n "$keyword" ]; then
                if [ -z "$keywords" ]; then
                    keywords="$keyword"
                else
                    keywords="$keywords|$keyword"
                fi
            fi
        fi
    done < "$CONFIG_FILE"

    # 保存最后一个分类
    if [ -n "$current_name" ] && [ -n "$keywords" ]; then
        SEARCH_CATEGORIES+=("${current_icon} ${current_name}|${keywords}")
        log "   分类: ${current_icon} ${current_name} (${keywords})"
    fi
fi

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
    for category_line in "${SEARCH_CATEGORIES[@]}"; do
        IFS='|' read -r category_name rest <<< "$category_line"
        queries="$rest"

        log "📂 正在搜索: $category_name"

        count=1
        for query in $queries; do
            [ $count -gt 3 ] && break
            log "   搜索关键词: $query"

            response=$(timeout 10 curl -s "https://api.search.brave.com/res/v1/web/search?q=$query&count=3&freshness=pt" \
                -H "Accept: application/json" \
                -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true

            if [ -z "$response" ]; then
                log "   ⚠️  API 请求超时"
                continue
            fi

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
    log "📋 使用 mock 数据模式"
    ALL_ITEMS+=("{\"title\":\"DeepSeek-V3 发布\",\"summary\":\"DeepSeek-V3 在多项基准测试中表现优异，推理能力显著提升\",\"url\":\"https://github.com/deepseek-ai\",\"category\":\"🤖 中美模型厂商\"}")
    ALL_ITEMS+=("{\"title\":\"OpenAI o1 模型系列\",\"summary\":\"专注于复杂推理任务，在编程和数学问题上表现突出\",\"url\":\"https://openai.com\",\"category\":\"🤖 中美模型厂商\"}")
    ALL_ITEMS+=("{\"title\":\"Claude 3.5 Sonnet 升级\",\"summary\":\"提升代码生成和长文本处理能力\",\"url\":\"https://www.anthropic.com\",\"category\":\"🧠 大模型热点\"}")
    ALL_ITEMS+=("{\"title\":\"Cursor AI IDE 爆火\",\"summary\":\"集成 GPT-4 和 Claude 的开发者工具，月活用户突破百万\",\"url\":\"https://cursor.sh\",\"category\":\"🔧 AI Agent\"}")
    ALL_ITEMS+=("{\"title\":\"Qwen2.5-Max 开源\",\"summary\":\"阿里通义千问发布新模型，在中文评测中表现优异\",\"url\":\"https://github.com/Qwen/Qwen2.5-Max\",\"category\":\"🧠 大模型热点\"}")
    ALL_ITEMS+=("{\"title\":\"Google Gemini 2.0 发布\",\"summary\":\"支持多模态输入输出，性能大幅提升\",\"url\":\"https://blog.google/technology/ai/google-gemini-20\",\"category\":\"🤖 中美模型厂商\"}")
fi

# 按分类组织数据
log "📊 整理数据，共 ${#ALL_ITEMS[@]} 条..."

declare -A CATEGORY_ITEMS
for item in "${ALL_ITEMS[@]}"; do
    # 使用 grep + sed 提取，避免 jq 解析问题
    category=$(echo "$item" | grep -o '"category":"[^"]*"' | sed 's/"category":"//' | sed 's/"$//')
    if [ -n "$category" ]; then
        CATEGORY_ITEMS["$category"]+="|$item"
    fi
done

# 构建消息内容
MESSAGE="🔥 AI 热点资讯\n"
MESSAGE+="📅 $TIMESTAMP\n\n"

for cat in "${!CATEGORY_ITEMS[@]}"; do
    MESSAGE+="$cat\n"
    items_str="${CATEGORY_ITEMS[$cat]#|}"
    IFS='|' read -ra items <<< "$items_str"
    idx=1
    for item in "${items[@]}"; do
        title=$(echo "$item" | grep -o '"title":"[^"]*"' | sed 's/"title":"//' | sed 's/"$//')
        summary=$(echo "$item" | grep -o '"summary":"[^"]*"' | sed 's/"summary":"//' | sed 's/"$//')
        url=$(echo "$item" | grep -o '"url":"[^"]*"' | sed 's/"url":"//' | sed 's/"$//')

        MESSAGE+="$idx. $title\n"
        if [ -n "$summary" ] && [ "$summary" != "null" ]; then
            summary_short=$(echo "$summary" | cut -c1-60)
            MESSAGE+="   $summary_short"
            if [ ${#summary} -gt 60 ]; then
                MESSAGE+="..."
            fi
            MESSAGE+="\n"
        fi
        if [ -n "$url" ] && [ "$url" != "null" ]; then
            MESSAGE+="   🔗 $url\n"
        fi
        MESSAGE+="\n"
        ((idx++))
    done
done

MESSAGE+="共 ${#ALL_ITEMS[@]} 条 AI 热点资讯"

log "消息长度: ${#MESSAGE} 字符"

# 发送到飞书
if [ "$HAS_FEISHU" = true ]; then
    log "📱 正在发送消息到飞书..."

    # 获取 token
    token_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")

    token_code=$(echo "$token_resp" | grep -o '"code":[0-9]*' | cut -d: -f2)
    if [ "$token_code" != "0" ]; then
        token_msg=$(echo "$token_resp" | grep -o '"msg":"[^"]*"' | sed 's/"msg":"//' | sed 's/"$//')
        log "❌ 获取飞书 token 失败: $token_msg"
    else
        token=$(echo "$token_resp" | grep -o '"tenant_access_token":"[^"]*"' | sed 's/"tenant_access_token":"//' | sed 's/"$//')
        log "✅ 获取 token 成功"

        # 使用 Python 脚本发送消息（避免 bash JSON 转义问题）
        chmod +x scripts/send-feishu.py
        python3 scripts/send-feishu.py "$FEISHU_APP_ID" "$FEISHU_SECRET_KEY" "$FEISHU_GROUP_ID" "$MESSAGE"

        http_code=$(echo "$msg_resp" | grep "HTTP_CODE:" | cut -d: -f2 | tr -d '\r')
        body=$(echo "$msg_resp" | grep -v "HTTP_CODE:" | tr -d '\r')

        log "   HTTP 状态码: $http_code"

        msg_code=$(echo "$body" | grep -o '"code":[0-9]*' | cut -d: -f2)
        if [ "$http_code" = "200" ] || [ "$msg_code" = "0" ]; then
            log "✅ 发送成功！"
        else
            msg_error=$(echo "$body" | grep -o '"msg":"[^"]*"' | sed 's/"msg":"//' | sed 's/"$//')
            log "❌ 发送失败: $msg_error"
        fi
    fi
else
    log "⚠️  飞书配置不完整，跳过发送"
    log "   消息预览:\n$MESSAGE"
fi

log "✅ 脚本执行完成"
