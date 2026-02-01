#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯，用 Gemini 总结翻译后发送到飞书

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.yaml"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

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
command -v gemini >/dev/null 2>&1 || { log "⚠️  警告: gemini CLI 未安装，将跳过翻译"; }

# 获取 API Keys
HAS_BRAVE_API=false
if [ -n "$BRAVE_API_KEY" ]; then
    log "✅ 使用环境变量中的 Brave API Key"
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

# 读取搜索类别
SEARCH_CATEGORIES=()
if [ -f "$CONFIG_FILE" ]; then
    log "📖 从 config.yaml 读取分类配置"

    current_name=""
    current_icon=""
    keywords=""

    while IFS= read -r line; do
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*name:[[:space:]]*\"([^\"]+)\" ]]; then
            if [ -n "$current_name" ] && [ -n "$keywords" ]; then
                SEARCH_CATEGORIES+=("${current_icon} ${current_name}|${keywords}")
            fi
            current_name="${BASH_REMATCH[1]}"
            current_icon=""
            keywords=""
        elif [[ "$line" =~ ^[[:space:]]*icon:[[:space:]]*\"([^\"]+)\" ]]; then
            current_icon="${BASH_REMATCH[1]}"
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

    if [ -n "$current_name" ] && [ -n "$keywords" ]; then
        SEARCH_CATEGORIES+=("${current_icon} ${current_name}|${keywords}")
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
declare -a RAW_ITEMS=()
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

if [ "$HAS_BRAVE_API" = true ]; then
    for category_line in "${SEARCH_CATEGORIES[@]}"; do
        IFS='|' read -r category_name rest <<< "$category_line"
        queries="$rest"

        log "📂 正在搜索: $category_name"

        count=1
        for query in $queries; do
            [ $count -gt 2 ] && break
            log "   搜索关键词: $query"

            response=$(timeout 10 curl -s "https://api.search.brave.com/res/v1/web/search?q=$query&count=3&freshness=pt" \
                -H "Accept: application/json" \
                -H "X-Subscription-Token: $BRAVE_API_KEY" 2>&1) || true

            if [ -z "$response" ]; then
                continue
            fi

            while IFS= read -r item_json; do
                [ $count -gt 2 ] && break
                title=$(echo "$item_json" | jq -r '.title // ""' | cut -c1-100)
                desc=$(echo "$item_json" | jq -r '.description // ""' | cut -c1-200)
                url=$(echo "$item_json" | jq -r '.url // ""')

                if [ -n "$title" ] && [ "$title" != "null" ]; then
                    RAW_ITEMS+=("{\"title\":\"$title\",\"description\":\"$desc\",\"url\":\"$url\",\"category\":\"$category_name\"}")
                    log "   ✓ ${title:0:40}..."
                    ((count++))
                fi
            done < <(jq -r '.web.results[] // .results[] | @json' 2>/dev/null <<< "$response" || echo "")

            sleep 1
        done
    done
else
    log "📋 使用 mock 数据模式"
    RAW_ITEMS+=("{\"title\":\"DeepSeek-V3 发布\",\"description\":\"DeepSeek-V3 在多项基准测试中表现优异\",\"url\":\"https://github.com/deepseek-ai\",\"category\":\"🤖 中美模型厂商\"}")
    RAW_ITEMS+=("{\"title\":\"OpenAI o1 模型系列\",\"description\":\"专注于复杂推理任务\",\"url\":\"https://openai.com\",\"category\":\"🤖 中美模型厂商\"}")
fi

log "📊 收集到 ${#RAW_ITEMS[@]} 条原始数据"

# 构建 JSON 数据供 Gemini 处理
ITEMS_JSON=$(printf '%s\n' "${RAW_ITEMS[@]}" | jq -s '.')

# 使用 Gemini 翻译和总结
SUMMARY_FILE="$SCRIPT_DIR/summary-output.txt"
FINAL_CONTENT=""

if command -v gemini >/dev/null 2>&1 && [ -n "$GEMINI_API_KEY" ]; then
    log "🌐 正在使用 Gemini 翻译和总结..."

    # 将 JSON 转换为易于阅读的格式
    TEMP_INPUT=$(mktemp)
    echo "$ITEMS_JSON" > "$TEMP_INPUT"

    gemini --model gemini-2.5-flash "你是一个专业的 AI 资讯编辑。请将以下 AI 热点资讯进行总结和翻译。

要求：
1. 将每条资讯翻译成简洁的中文
2. 每个分类下提取最重要的 2-3 条
3. 保持原有链接
4. 输出格式要求：
   - 不要使用 markdown 格式
   - 不要使用 **粗体** 或其他 markdown 语法
   - 不要使用 \\n 表示换行，直接使用换行
   - 不要使用 HTML 标签如 <strong>
   - 每条资讯格式：序号. 标题（来源）- 摘要
   - 分类标题使用 emoji 前缀
   - 最后标注信息来源

输出示例：
🔥 AI 热点资讯 - [日期]

🤖 中美模型厂商
1. OpenAI 发布新模型（来源）- 简短的描述
2. DeepSeek 新版本发布（来源）- 简短的描述

🧠 大模型热点
1. Claude 3 新功能（来源）- 简短的描述

---
数据：
$(cat "$TEMP_INPUT")
---
" 2>&1 | tee "$SUMMARY_FILE"

    # 读取 Gemini 输出
    if [ -s "$SUMMARY_FILE" ]; then
        FINAL_CONTENT=$(cat "$SUMMARY_FILE")
        log "✅ Gemini 处理完成"
    else
        FINAL_CONTENT="（Gemini 处理失败）\n\n$ITEMS_JSON"
    fi

    rm -f "$TEMP_INPUT"
else
    log "⚠️  跳过 Gemini 处理"
    FINAL_CONTENT="（未使用 Gemini 翻译）\n\n原始数据：\n$ITEMS_JSON"
fi

# 在 GitHub Actions 步骤摘要中输出
if [ -n "$GITHUB_STEP_SUMMARY" ]; then
    echo "## 🔥 AI 热点资讯" >> "$GITHUB_STEP_SUMMARY"
    echo "**时间**: $TIMESTAMP" >> "$GITHUB_STEP_SUMMARY"
    echo "**数据来源**: Brave Search" >> "$GITHUB_STEP_SUMMARY"
    echo "" >> "$GITHUB_STEP_SUMMARY"
    echo "$FINAL_CONTENT" >> "$GITHUB_STEP_SUMMARY"
    echo "" >> "$GITHUB_STEP_SUMMARY"
    echo "---" >> "$GITHUB_STEP_SUMMARY"
    echo "*共收集 ${#RAW_ITEMS[@]} 条资讯*" >> "$GITHUB_STEP_SUMMARY"
fi

# 发送到飞书
if [ "$HAS_FEISHU" = true ]; then
    log "📱 正在发送消息到飞书..."

    # 获取 token
    token_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")

    token_code=$(echo "$token_resp" | grep -o '"code":[0-9]*' | cut -d: -f2)
    if [ "$token_code" != "0" ]; then
        log "❌ 获取飞书 token 失败"
    else
        token=$(echo "$token_resp" | grep -o '"tenant_access_token":"[^"]*"' | sed 's/"tenant_access_token":"//' | sed 's/"$//')

        # 使用 Python 发送消息
        chmod +x scripts/send-feishu.py
        python3 scripts/send-feishu.py "$FEISHU_APP_ID" "$FEISHU_SECRET_KEY" "$FEISHU_GROUP_ID" "$FINAL_CONTENT"
    fi
else
    log "⚠️  飞书配置不完整，跳过发送"
    log "   内容预览:\n$FINAL_CONTENT"
fi

log "✅ 脚本执行完成"
