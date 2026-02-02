<h1 align="center">AiTrend Skill v0.2.0</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<p align="center">
  <b>🚀 多源 AI 热点资讯收集器 - 支持多渠道推送</b>
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-功能特性">功能特性</a> •
  <a href="#-配置说明">配置说明</a> •
  <a href="#-渠道配置">渠道配置</a> •
  <a href="#-多语言支持">多语言</a>
</p>

---

## 🌍 多语言文档

<p align="center">
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## 📸 效果展示

![AiTrend 信息效果](ScreenShot_2026-02-01_235825_945.png)

*AI 热点资讯自动收集并推送到 Discord/飞书的效果*

---

## ✨ 功能特性

- 🔥 **多源挖掘**：Tavily、HackerNews、GitHub、Reddit、Twitter、Product Hunt
- 📢 **多渠道推送**：Discord、飞书、Telegram、Console
- 🌐 **多语言支持**：中、英、日、韩、西
- 🔄 **智能去重**：24小时滑动窗口，自动过滤重复内容
- ⚡ **零配置启动**：仅需 Tavily Key

---

## 🚀 快速开始

### 1️⃣ 克隆仓库

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2️⃣ 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 TAVILY_API_KEY
```

### 3️⃣ 配置发送渠道

```bash
cp config/config.example.json config/config.json
# 编辑 config/config.json，启用你想要的渠道
```

### 4️⃣ 运行

```bash
python3 -m src
```

---

## 🔧 配置说明

### 基础配置

编辑 `config/config.json`：

```json
{
  "language": "zh",
  "sources": {
    "tavily": {
      "enabled": true,
      "api_key": "${TAVILY_API_KEY}"
    },
    "hackernews": { "enabled": true },
    "reddit": { "enabled": true },
    "github_trending": { "enabled": true }
  },
  "channels": {
    "console": { "enabled": true }
  }
}
```

---

## 📢 渠道配置

AiTrend 支持多种输出渠道，可以同时启用多个：

### Console（默认）

```json
"channels": {
  "console": {
    "enabled": true
  }
}
```

### Discord

```json
"channels": {
  "discord": {
    "enabled": true,
    "channel_id": "1467767285044346933"
  }
}
```

**获取 Channel ID：**
1. Discord 设置 → 高级 → 开启开发者模式
2. 右键频道 → 复制频道 ID

### Discord 论坛 (Forum)

```json
"channels": {
  "discord_forum": {
    "enabled": true,
    "channel_id": "1467789796087824475"
  }
}
```

**特点：**
- 每天自动创建一个新帖子（Thread）
- 帖子标题包含日期，如 "🔥 AI 热点 02-03"
- 适合长期归档和追溯历史热点

### 飞书 (Feishu)

```json
"channels": {
  "feishu": {
    "enabled": true,
    "chat_id": "oc_9a3c218325fd2cfa42f2a8f6fe03ac02"
  }
}
```

**获取 Chat ID：**
- 飞书群设置 → 群机器人 → 查看群 ID

### Telegram

```json
"channels": {
  "telegram": {
    "enabled": true,
    "chat_id": "-1001234567890"
  }
}
```

**获取 Chat ID：**
- 使用 @userinfobot 或查看群组 URL

### 多渠道同时推送

```json
"channels": {
  "console": { "enabled": true },
  "discord": {
    "enabled": true,
    "channel_id": "YOUR_DISCORD_CHANNEL_ID"
  },
  "feishu": {
    "enabled": true,
    "chat_id": "YOUR_FEISHU_CHAT_ID"
  }
}
```

---

## ⏰ 定时任务

### OpenClaw Cron

```bash
# 每天早上 9:00 自动运行
openclaw cron add \
  --name "aitrend-daily" \
  --schedule "0 9 * * *" \
  --command "python3 -m src" \
  --cwd "~/.openclaw/workspace/AiTrend"
```

### Linux Cron

```bash
0 9 * * * cd /path/to/AiTrend && python3 -m src
```

---

## 📊 数据源

| 数据源 | 需要 API Key | 说明 |
|--------|--------------|------|
| Tavily | ✅ 必需 | AI 原生搜索引擎 |
| HackerNews | ❌ 否 | 开发者社区热门 |
| GitHub | ❌ 否 | Trending AI 项目 |
| Reddit | ❌ 否 | AI 社区讨论 |
| Twitter/X | ⚠️ 可选 | Viral 内容 |
| Product Hunt | ⚠️ 可选 | 新产品发布 |

---

## 🌍 多语言支持

| 语言 | 代码 | 状态 |
|------|------|------|
| 简体中文 | zh | ✅ |
| English | en | ✅ |
| 日本語 | ja | ✅ |
| 한국어 | ko | ✅ |
| Español | es | ✅ |

修改 `config/config.json` 中的 `language` 字段即可切换。

---

## 📁 项目结构

```
AiTrend/
├── src/
│   ├── __main__.py              # 程序入口
│   ├── core/
│   │   ├── config_loader.py     # 配置加载
│   │   ├── sender.py            # 渠道发送器
│   │   └── deduplicator.py      # 去重器
│   └── sources/                 # 数据源实现
├── config/
│   ├── config.example.json      # 配置示例
│   └── config.json              # 用户配置（需创建）
├── .env.example                 # 环境变量示例
├── .env                         # 用户环境变量（需创建）
└── README.md
```

---

## 📝 配置示例（完整版）

```json
{
  "language": "zh",
  "sources": {
    "reddit": { "enabled": true },
    "hackernews": { "enabled": true },
    "github_trending": {
      "enabled": true,
      "languages": ["python", "typescript", "rust", "go"]
    },
    "tavily": {
      "enabled": true,
      "api_key": "${TAVILY_API_KEY}",
      "queries": [
        "latest AI tools launch 2026",
        "new AI models released this week"
      ]
    }
  },
  "channels": {
    "console": { "enabled": true },
    "discord": {
      "enabled": true,
      "channel_id": "1467767285044346933"
    }
  }
}
```

---

## 📄 许可证

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend  
**作者**: 屁屁虾🦞
