# AiTrend Skill v0.1.0

> 🚀 多源 AI 热点资讯收集器 - **普通人也能用的 AI 周报**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg)]()

## ✨ 特性

- 🔥 **多源挖掘**：Twitter、Product Hunt、HackerNews、GitHub、Brave Search
- 🤖 **AI 总结**：Gemini 2.5 Flash 智能分析
- 👥 **亲民视角**：普通人马上就能用的工具
- 📝 **口语化表达**：像朋友聊天一样自然
- 🚫 **零依赖**：纯 Python 标准库，开箱即用
- 🎯 **AI 自动安装**：提供 [SKILL.md](SKILL.md)，让你的 AI 自主完成安装

## 🚀 快速开始

### 🎯 方式一：让 AI 自动安装（推荐）

**只需对你的 AI 说：**

> "请阅读 https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md 并按照指引安装 AiTrend Skill"

你的 AI 会自动：
1. 克隆仓库到正确位置
2. 检查并请求必要的 API Key（仅需 Gemini）
3. 运行并生成第一条内容
4. 询问是否需要配置更多数据源

**零配置启动** - 只需一个 Gemini API Key 即可运行！

---

### 💻 方式二：手动安装

#### 1. 安装到 OpenClaw

```bash
# 进入 OpenClaw workspace
cd ~/.openclaw/workspace

# 克隆 Skill
git clone https://github.com/Lychee-AI-Team/AiTrend.git

# 安装依赖（如需）
cd AiTrend
```

#### 2. 配置 API Keys

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

#### 3. 运行

```bash
# 直接运行
python3 -m src

# 或通过 OpenClaw 调用
openclaw run-skill AiTrend
```

### 方式二：独立运行

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# 编辑 .env 填入 API Key
python3 -m src
```

## 📋 环境变量配置

创建 `.env` 文件，配置以下变量：

```bash
# Brave Search API
# 获取地址: https://api.search.brave.com/
BRAVE_API_KEY=your_brave_api_key

# Google Gemini API
# 获取地址: https://ai.google.dev/
GEMINI_API_KEY=your_gemini_api_key

# GitHub Personal Access Token
# 获取地址: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token

# Product Hunt API Token
# 获取地址: https://www.producthunt.com/v2/oauth/applications
PRODUCTHUNT_TOKEN=your_producthunt_token

# Twitter/X Cookie (用于 bird CLI)
# 获取方式: 登录 Twitter 后从浏览器开发者工具复制
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CT0=your_twitter_ct0
```

## 📊 数据源

| 数据源 | 内容类型 | 状态 |
|--------|----------|------|
| Twitter/X | 正在讨论的 viral 内容 | ✅ |
| Product Hunt | 今天刚上线的新产品 | ✅ |
| HackerNews | 开发者社区关注的内容 | ✅ |
| GitHub | 开源 AI 项目 | ✅ |
| Brave Search | 全网热点 | ✅ |
| Reddit | AI 社区讨论 | ⚠️ (需解决反爬) |

## 🎯 内容特点

### 挖掘方法

**❌ 不是：** 关键词搜索 → 找到旧闻
**✅ 而是：** 社交媒体监控 → 发现正在发生的内容

### 内容筛选

**❌ 不是：** 只看 star 数 → 永远是老项目
**✅ 而是：** AI 理解创新点 → 发现真正有价值的新工具

### 内容呈现

**❌ 不是：** "一句话说清：XXX"
**✅ 而是：** "这周我发现了一个超酷的 XXX，它其实就是..."

## 📁 项目结构

```
AiTrend/
├── src/
│   ├── __main__.py              # 程序入口
│   ├── core/
│   │   ├── collector.py         # 核心收集器
│   │   └── validator.py         # 自验证器
│   ├── sources/
│   │   ├── base.py              # 数据源基类
│   │   ├── brave_search.py      # Brave 搜索
│   │   ├── github_trending.py   # GitHub Trending
│   │   ├── reddit.py            # Reddit 监控
│   │   ├── hackernews.py        # HackerNews 监控
│   │   ├── producthunt.py       # Product Hunt 监控
│   │   ├── twitter.py           # Twitter 监控
│   │   └── __init__.py          # 数据源工厂
│   └── utils/
│       └── __init__.py          # 环境变量加载
├── config/
│   └── config.json              # 配置文件
├── .env.example                 # 环境变量示例
├── requirements.txt             # 依赖列表（空，纯标准库）
├── README.md                    # 项目说明
├── AGENT.md                     # 开发经验总结
└── LICENSE                      # 许可证
```

## 🔧 OpenClaw Skill 配置

### 配置文件路径

OpenClaw Skill 配置文件位于 `config/config.json`：

```json
{
  "sources": {
    "reddit": { "enabled": true },
    "hackernews": { "enabled": true },
    "producthunt": {
      "enabled": true,
      "api_key": "${PRODUCTHUNT_TOKEN}"
    },
    "twitter": {
      "enabled": true,
      "auth_token": "${TWITTER_AUTH_TOKEN}",
      "ct0": "${TWITTER_CT0}"
    },
    "github_trending": {
      "enabled": true,
      "languages": ["python", "typescript", "rust", "go"]
    },
    "brave_search": {
      "enabled": true,
      "api_key": "${BRAVE_API_KEY}",
      "queries": [
        "AI工具 实测 使用体验 评测",
        "大模型对比 用户测试 真实体验"
      ]
    }
  },
  "summarizer": {
    "enabled": true,
    "provider": "gemini",
    "model": "gemini-3-flash-preview",
    "api_key": "${GEMINI_API_KEY}"
  }
}
```

### 定时任务（可选）

在 OpenClaw 中配置定时运行：

```bash
# 添加定时任务（每周一 9:00）
openclaw cron add \
  --name "aitrend-weekly" \
  --schedule "0 9 * * 1" \
  --command "python3 -m src" \
  --cwd "~/.openclaw/workspace/AiTrend"
```

## ⚙️ 配置说明

编辑 `config/config.json`：

```json
{
  "sources": {
    "twitter": { "enabled": true },
    "producthunt": { "enabled": true, "api_key": "${PRODUCTHUNT_TOKEN}" },
    "hackernews": { "enabled": true },
    "github_trending": { "enabled": true },
    "brave_search": { "enabled": true, "api_key": "${BRAVE_API_KEY}" }
  },
  "summarizer": {
    "enabled": true,
    "provider": "gemini",
    "model": "gemini-2.5-flash",
    "api_key": "${GEMINI_API_KEY}"
  }
}
```

## 🧪 测试

```bash
# 运行基础测试
python3 -m pytest tests/ -v

# 手动测试
python3 -m src
```

## 📝 开发标准

### 核心原则

1. **纯标准库**：不使用 pip 依赖
2. **零系统权限**：不调用 sudo
3. **实用主义**：普通人马上能用
4. **口语化表达**：像朋友聊天

### 代码规范

- 使用 `http.client` 进行 HTTP 请求
- 使用 `dataclasses` 替代 pydantic
- 使用 `json` 替代 yaml
- 使用正则表达式替代 BeautifulSoup

## 📅 更新日志

### v0.1.0 (2026-02-01)

- ✨ 多数据源挖掘（Twitter、Product Hunt、HackerNews、GitHub、Brave）
- ✨ Gemini AI 智能总结
- ✨ 亲民内容生成（口语化、场景化）
- ✨ 纯标准库实现（零依赖）
- ✨ 环境变量管理

## 🎯 使用场景

- **AI 博主**：获取每周值得分享的 AI 新工具
- **产品经理**：发现新兴的 AI 产品和趋势
- **普通用户**：了解普通人能用的 AI 工具
- **开发者**：发现开源 AI 项目和灵感

## 🤝 贡献

欢迎提交 PR 和 Issue！

## 📄 许可证

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend  
**作者**: 屁屁虾🦞  
**KOL**: 大师
