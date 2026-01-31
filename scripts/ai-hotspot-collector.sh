#!/bin/bash
# AI Hotspot Collector
# 使用 Brave Search API 收集 AI 热点资讯，并用 Gemini 翻译

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"
BRAVE_API_KEY_FILE="$SCRIPT_DIR/../.brave-api-key"
GEMINI_API_KEY_FILE="$SCRIPT_DIR/../.gemini-api-key"

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

# 优先从环境变量获取 API Keys
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
    HAS_BRAVE_API=false
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
if [ "$HAS_BRAVE_API" = true ]; then
    # 使用 Brave Search API
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

            # 保存响应到临时文件
            echo "$response" > /tmp/brave_response_$$.json

            # 尝试解析并提取结果
            ITEMS_JSON="[]"

            if jq -e '.web.results' /tmp/brave_response_$$.json > /dev/null 2>&1; then
                log "   响应格式: .web.results"
                while IFS= read -r item_json; do
                    [ $count -ge 3 ] && break
                    title=$(echo "$item_json" | jq -r '.title // "无标题"' | cut -c1-80)
                    desc=$(echo "$item_json" | jq -r '.description // "暂无描述"' | cut -c1-150)
                    url=$(echo "$item_json" | jq -r '.url // ""')

                    if [ -n "$title" ]; then
                        echo "$count. **$title**" >> "$COLLECTED_FILE"
                        echo "   $desc" >> "$COLLECTED_FILE"
                        echo "   🔗 $url" >> "$COLLECTED_FILE"
                        echo "" >> "$COLLECTED_FILE"
                        log "   ✓ $count. ${title:0:50}..."
                        ((count++))
                    fi
                done < <(jq -r '.web.results[] | @json' /tmp/brave_response_$$.json 2>/dev/null)

            elif jq -e '.results' /tmp/brave_response_$$.json > /dev/null 2>&1; then
                log "   响应格式: .results (兼容)"
                while IFS= read -r item_json; do
                    [ $count -ge 3 ] && break
                    title=$(echo "$item_json" | jq -r '.title // "无标题"' | cut -c1-80)
                    desc=$(echo "$item_json" | jq -r '.description // "暂无描述"' | cut -c1-150)
                    url=$(echo "$item_json" | jq -r '.url // ""')

                    if [ -n "$title" ]; then
                        echo "$count. **$title**" >> "$COLLECTED_FILE"
                        echo "   $desc" >> "$COLLECTED_FILE"
                        echo "   🔗 $url" >> "$COLLECTED_FILE"
                        echo "" >> "$COLLECTED_FILE"
                        log "   ✓ $count. ${title:0:50}..."
                        ((count++))
                    fi
                done < <(jq -r '.results[] | @json' /tmp/brave_response_$$.json 2>/dev/null)
            else
                log "   ⚠️  无法解析响应"
            fi

            rm -f /tmp/brave_response_$$.json
            sleep 1
        done
    done
else
    # 使用 mock 数据模式
    log "📋 使用 mock 数据模式（服务器不支持 Brave Search API）"
    cat > "$COLLECTED_FILE" << 'MOCK_EOF'
## 🏢 中美模型厂商

1. **DeepSeek-V3 模型发布**
   DeepSeek-V3 在 MMLU、GSM8K 等多项基准测试中表现优异，推理能力显著提升，开源社区反响热烈。
   🔗 https://github.com/deepseek-ai/DeepSeek-V3

2. **OpenAI 推出 o1 模型系列**
   OpenAI 发布 o1-preview 和 o1-mini，专注于复杂推理任务，在编程和数学问题上表现突出。
   🔗 https://openai.com/blog/introducing-openai-o1

3. **Google Gemini 2.0 发布**
   Google 发布 Gemini 2.0，支持多模态输入输出，性能大幅提升，竞争 OpenAI 和 Anthropic。
   🔗 https://blog.google/technology/ai/google-gemini-20

## 🧠 大模型热点

1. **GPT-4.1 性能优化**
   OpenAI 更新 GPT-4.1，降低成本和延迟，同时提升响应质量，企业用户反馈积极。
   🔗 https://openai.com/blog/gpt-4-1-update

2. **Qwen2.5-Max 开源**
   阿里通义千问发布 Qwen2.5-Max，参数量达 72B，在多个中文评测中表现优异。
   🔗 https://github.com/Qwen/Qwen2.5-Max

3. **Claude 3.5 Sonnet 升级**
   Anthropic 升级 Claude 3.5 Sonnet，提升代码生成和长文本处理能力，开发者社区广泛采用。
   🔗 https://www.anthropic.com/claude-3-5-sonnet

## 👤 创始人/CEO

1. **Sam Altman 谈 AGI 时间表**
   OpenAI CEO 在访谈中认为 AGI 可能在 2027 年前实现，强调安全研究的重要性。
   🔗 https://www.wsj.com/tech/ai/sam-altman-agi-timeline

2. **李开复成立 AI 公司**
   创新工场李开复创立 01.AI，专注于开源大模型，已发布 Yi 系列模型。
   🔗 https://www.01.ai/

## 🤖 最热 Agent

1. **Cursor AI IDE 爆火**
   Cursor 集成 GPT-4 和 Claude，成为开发者首选 AI 编码工具，月活用户突破百万。
   🔗 https://cursor.sh/

2. **RAG 技术成熟**
   检索增强生成（RAG）框架如 LangChain、LlamaIndex 广泛应用，企业级部署方案日趋完善。
   🔗 https://langchain.com/

3. **AI Agent 框架涌现**
   AutoGen、CrewAI、LangGraph 等多智能体框架快速发展，支持复杂任务自动化。
   🔗 https://microsoft.github.io/autogen/
MOCK_EOF
    log "✅ Mock 数据已生成"
fi

# 使用 Gemini 翻译和总结
if [ -n "$GEMINI_API_KEY" ] && command -v gemini >/dev/null 2>&1; then
    log "🌐 正在使用 Gemini 翻译和总结..."

    TRANSLATED_FILE="/tmp/hotspot-translated-$$-md"

    gemini --model gemini-2.5-flash "你是一个专业的 AI 资讯编辑。请将以下 AI 热点资讯翻译成中文并进行总结整理。

要求：
1. 翻译成流畅的中文，保持专业术语的准确性
2. 保持原有的标题、描述和链接格式
3. 每个分类下提取 3-5 条最重要、最有价值的信息
4. 使用简洁、专业的语言风格
5. 不要添加额外的评论或解释，只输出整理后的内容

---
$(cat "$COLLECTED_FILE")
---
" 2>&1 | tee "$TRANSLATED_FILE"

    if [ -s "$TRANSLATED_FILE" ]; then
        log "✅ 翻译完成"
        REPORT_FILE="$TRANSLATED_FILE"
    else
        log "⚠️ 翻译失败，使用原始内容"
        REPORT_FILE="$COLLECTED_FILE"
    fi
else
    log "⚠️ 跳过翻译，使用原始英文内容"
    REPORT_FILE="$COLLECTED_FILE"
fi

# 发送到 webhook
if [ -n "$WEBHOOK_URL" ]; then
    log "📡 正在发送到 webhook: $WEBHOOK_URL"

    # 提取所有标题和链接
    items_json=$(jq -Rs '
        split("\n\n## ") |
        map(select(length > 0)) |
        map(
            split("\n") |
            . as $lines |
            map(select(test("^[0-9]+\\.  \\*\\*"))) |
            map(. as $title |
                ($lines | index($title)) as $idx |
                {
                    title: ($title | sub("^[0-9]+\\.  \\*\\*"; "") | sub("\\*\\*$"; "")),
                    summary: (if $idx + 1 < ($lines | length) then
                        ($lines[$idx + 1] | sub("^    "; ""))
                    else "" end),
                    url: (if $idx + 2 < ($lines | length) and ($lines[$idx + 2] | test("^    🔗")) then
                        ($lines[$idx + 2] | sub("^    🔗 "; ""))
                    else "" end)
                }
            )
        ) |
        flatten
    ' "$REPORT_FILE")

    log "   解析到的 items: $(echo "$items_json" | jq -r '.title' 2>/dev/null | wc -l) 个"
    log "   items_json 长度: ${#items_json} 字符"

    # 输出 curl 命令到文件
    CURL_FILE="$SCRIPT_DIR/hotspot-curl-$(date +%Y%m%d-%H%M%S).sh"
    cat > "$CURL_FILE" << CURL_EOF
#!/bin/bash
# AI Hotspot Webhook - $(date '+%Y-%m-%d %H:%M:%S')
# 手动执行此命令发送到 webhook
# 设置 WEBHOOK_URL 环境变量，例如：export WEBHOOK_URL=http://your-server:3000/webhook/ai-hotspot

curl -X POST "\${WEBHOOK_URL}" \\
  -H 'Content-Type: application/json' \\
  -d '{
  "title": "🔥 AI 热点资讯",
  "items": $(echo "$items_json" | jq -c '.'),
  "summary": "AI 热点"
}'
CURL_EOF

    chmod +x "$CURL_FILE"
    log "📄 Curl 命令已生成: $CURL_FILE"
    log ""
    log "🔧 手动执行命令："
    cat "$CURL_FILE"
    log ""
else
    log "⚠️ WEBHOOK_URL 未设置，跳过生成 curl 命令"
fi

# 清理临时文件
rm -f "$COLLECTED_FILE" "$TRANSLATED_FILE" 2>/dev/null || true

log "✅ 脚本执行完成"
