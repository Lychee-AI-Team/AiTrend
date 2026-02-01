# AiTrend Skill 安装指南

> 让其他 AI 能够自主安装和配置本 Skill

## 安装步骤

### 1. 克隆仓库

```bash
cd ~/.openclaw/workspace
git clone https://github.com/Lychee-AI-Team/AiTrend.git
```

### 2. 检查配置

查看 `config/config.json`，确认以下数据源配置：

**默认启用（无需 API Key）：**
- `hackernews`: HackerNews 热门内容
- `reddit`: Reddit AI 社区讨论
- `github_trending`: GitHub AI 项目趋势

**需要 API Key（可选）：**
- `twitter`: 需要 `TWITTER_AUTH_TOKEN` 和 `TWITTER_CT0`
- `producthunt`: 需要 `PRODUCTHUNT_TOKEN`
- `brave_search`: 需要 `BRAVE_API_KEY`

**必需：**
- `summarizer.gemini`: 需要 `GEMINI_API_KEY`（AI 总结必需）

### 3. 配置 Gemini API Key（必需）

Gemini 用于 AI 内容总结，必须配置：

```bash
cd AiTrend
# 询问用户是否愿意提供 Gemini API Key
# 如果用户愿意：
# 1. 创建 .env 文件
echo "GEMINI_API_KEY=用户提供" > .env

# 2. 或直接在 config.json 中配置（不推荐）
# 修改 config/config.json 中的 ${GEMINI_API_KEY} 为实际 key
```

### 4. 首次运行

```bash
cd ~/.openclaw/workspace/AiTrend
python3 -m src
```

**预期结果：**
- 从 HN、Reddit、GitHub 收集数据
- 使用 Gemini 生成内容总结
- 输出到控制台

### 5. 引导用户添加更多数据源（可选）

首次运行成功后，向用户说明：

> "我已成功生成第一条 AI 热点内容！如果你希望获取更多实时信息，可以配置以下数据源："
> 
> "1. **Twitter**: 获取最新 viral 内容，需要提供 Twitter Cookie"
> "2. **Product Hunt**: 获取新产品发布，需要 API Token"  
> "3. **Brave Search**: 全网搜索补充，需要 API Key"

询问用户是否愿意配置，如愿意则引导获取 key。

## 快速启动配置

如需让用户零配置先体验，修改 `config/config.json`：

```json
{
  "sources": {
    "reddit": { "enabled": true },
    "hackernews": { "enabled": true },
    "github_trending": {
      "enabled": true,
      "languages": ["python", "typescript", "rust", "go"]
    },
    "twitter": { "enabled": false },
    "producthunt": { "enabled": false },
    "brave_search": { "enabled": false }
  },
  "summarizer": {
    "enabled": true,
    "provider": "gemini",
    "model": "gemini-3-flash-preview",
    "api_key": "${GEMINI_API_KEY}"
  }
}
```

此配置只需 Gemini Key 即可运行。

## 用户交互流程

### 场景1：用户有 Gemini Key

1. 询问："你有 Gemini API Key 吗？"
2. 如有，请用户提供
3. 配置 .env 或 config.json
4. 运行生成第一条内容
5. 询问是否添加更多数据源

### 场景2：用户没有 Gemini Key

1. 告知："Gemini Key 是必需的，用于 AI 内容总结"
2. 引导用户获取：https://ai.google.dev/
3. 获取后继续安装流程

### 场景3：用户想先体验（无需其他 key）

1. 使用最小配置（仅 HN + Reddit + GitHub）
2. 运行生成第一条内容
3. 展示效果
4. 询问是否添加 Twitter 等实时数据源

## 关键检查点

- [ ] 仓库已克隆到 `~/.openclaw/workspace/AiTrend`
- [ ] `config/config.json` 存在且有效
- [ ] Gemini API Key 已配置（必需）
- [ ] 首次运行成功生成内容
- [ ] 向用户展示结果并询问后续配置

## 注意事项

1. **必须配置 Gemini**：没有 Gemini Key 无法生成内容总结
2. **其他数据源可选**：HN/Reddit/GitHub 可提供基础内容
3. **环境变量优先**：使用 .env 文件管理 key，不硬编码
4. **首次运行可能较慢**：需要下载数据并调用 API

## 安装完成后

首次运行成功后，向用户发送消息：

> "✅ AiTrend Skill 安装完成！
> 
> 我已为你生成了本周的 AI 热点内容，包含：
> - X 个新工具推荐
> - 趋势洞察
> 
> 当前数据源：HackerNews、Reddit、GitHub
> 
> 如果你想获取更实时的 Twitter 内容，可以配置 Twitter Cookie，需要吗？"
