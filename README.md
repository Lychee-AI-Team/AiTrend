# AiTrend - AI 热点资讯收集器

> 自动收集 AI 行业热点资讯，翻译整理并推送到飞书群聊

## 📖 项目简介

AiTrend 是一个自动化的 AI 行业资讯收集工具，通过 GitHub Actions 定期抓取最新 AI 热点，使用 Gemini AI 进行翻译和总结整理，最终通过 webhook 推送到飞书群聊。

## ✨ 主要功能

- 🔍 **智能搜索**: 使用 Brave Search API 收集 AI 热点资讯
- 🌐 **自动翻译**: 集成 Gemini 2.5 Flash 进行专业翻译和总结
- 📊 **多维度分类**: 覆盖中美模型厂商、大模型热点、创始人动态、AI Agent 等多个领域
- ⏰ **定时推送**: 每天自动推送 3 次（13:00、21:00、05:00 CST）
- 🚀 **GitHub Actions**: 完全在云端运行，无需本地服务器资源

## 🏗️ 架构设计

```
┌─────────────────┐
│  GitHub Actions │
│  (定时触发)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Brave Search API               │
│ ────────────────────           │
│ • 搜索 AI 热点资讯             │
│ • 获取最新动态                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Gemini 2.5 Flash                │
│ ────────────────────           │
│ • 翻译成中文                   │
│ • 总结整理内容                 │
│ • 提炼关键信息                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Webhook 服务器                  │
│ ────────────────────           │
│ • 接收数据                     │
│ • 格式化处理                   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 飞书群聊                        │
│ ────────────────────           │
│ • 推送 AI 热点                 │
│ • 团队共享资讯                 │
└─────────────────────────────────┘
```

## 📂 项目结构

```
AiTrend/
├── .github/
│   └── workflows/
│       └── ai-hotspot.yml      # GitHub Actions 工作流
├── scripts/
│   ├── ai-hotspot-collector.sh # AI 热点收集脚本
│   └── collect-news.js         # AI News 收集脚本
├── webhook-server/              # Webhook 服务器代码
│   ├── index.js
│   └── package.json
└── README.md
```

## 🚀 快速开始

### 1. 配置 GitHub Secrets

在仓库设置中添加以下 Secrets：

| Secret 名称 | 说明 | 获取方式 |
|-------------|------|----------|
| `WEBHOOK_URL` | 你的服务器 webhook 地址 | 部署 webhook 服务器后获取 |
| `BRAVE_API_KEY` | Brave Search API Key | [Brave Search API](https://brave.com/search/api/) |
| `GEMINI_API_KEY` | Gemini API Key | [Google AI Studio](https://makersuite.google.com/app/apikey) |

### 2. 部署 Webhook 服务器

```bash
cd webhook-server
npm install
node index.js
```

服务器将监听 `http://your-server:3000`

### 3. 手动触发

在 GitHub Actions 页面选择 "AI Hotspot Collector" workflow，点击 "Run workflow"

## 📡 Webhook 端点

### 端点列表

- `/webhook/ai-hotspot` - AI Hotspot 收集
- `/webhook/ai-news` - AI News 收集
- `/webhook/github` - GitHub 事件
- `/health` - 健康检查

### 数据格式

AI Hotspot Webhook 接收 JSON 格式数据：

```json
{
  "title": "🔥 AI 热点资讯",
  "items": [
    {
      "title": "DeepSeek-V3 模型发布",
      "summary": "DeepSeek-V3 在 MMLU、GSM8K 等多项基准测试中表现优异",
      "url": "https://github.com/deepseek-ai/DeepSeek-V3"
    }
  ],
  "summary": "AI 热点"
}
```

## 📅 定时任务

| 时区 | 时间 | 说明 |
|------|------|------|
| UTC | 05:00 | 亚洲工作时间 |
| UTC | 13:00 | 欧洲工作时间 |
| UTC | 21:00 | 美洲工作时间 |

## 🔧 环境配置

### GitHub Actions 环境
- ✅ Brave Search API 可用
- ✅ Gemini CLI 预安装
- ✅ 完整的翻译功能

### 本地服务器环境
- ⚠️ Brave Search API 不可用（网络限制）
- ✅ 使用 mock 数据模式
- ✅ Webhook 服务器正常运行

## 📊 收集分类

### 🏢 中美模型厂商
- OpenAI, Anthropic, Google, Meta, DeepSeek
- 关注最新模型发布、性能更新

### 🧠 大模型热点
- GPT-4, Claude, DeepSeek, Qwen, ChatGLM
- 关注基准测试、开源发布

### 👤 创始人/CEO
- Sam Altman, Dario Amodei, 李开复
- 关注访谈、观点分享

### 🤖 最热 Agent
- AI agent, Claude Code, LangGraph
- 关注框架发布、工具更新

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**组织**: Lychee-AI-Team  
**仓库**: https://github.com/Lychee-AI-Team/AiTrend
