<h1 align="center">AiTrend Skill v0.2.0</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<p align="center">
  <b>🚀 Multi-source AI Trend Collector - Multi-channel Support</b>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-channel-setup">Channels</a> •
  <a href="#-multi-language">Languages</a>
</p>

---

## 🌍 Multi-language Docs

<p align="center">
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ Features

- 🔥 **Multi-source Mining**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- 📢 **Multi-channel Push**: Discord, Feishu, Telegram, Console
- 🌐 **Multi-language**: Chinese, English, Japanese, Korean, Spanish
- 🔄 **Smart Deduplication**: 24-hour sliding window
- ⚡ **Zero-config**: Only Tavily Key required

---

## 🚀 Quick Start

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2️⃣ Configure Environment Variables

```bash
cp .env.example .env
# Edit .env, add your TAVILY_API_KEY
```

### 3️⃣ Configure Output Channels

```bash
cp config/config.example.json config/config.json
# Edit config/config.json, enable your desired channels
```

### 4️⃣ Run

```bash
python3 -m src
```

---

## 🔧 Configuration

### Basic Configuration

Edit `config/config.json`:

```json
{
  "language": "en",
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

## 📢 Channel Configuration

AiTrend supports multiple output channels. You can enable multiple channels simultaneously:

### Console (Default)

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

**Get Channel ID:**
1. Discord Settings → Advanced → Enable Developer Mode
2. Right-click channel → Copy Channel ID

### Discord Forum

```json
"channels": {
  "discord_forum": {
    "enabled": true,
    "channel_id": "1467789796087824475"
  }
}
```

**Features:**
- Automatically creates a new thread daily
- Thread title includes date, e.g., "🔥 AI Hotspots 02-03"
- Great for archiving and historical reference

### Feishu

```json
"channels": {
  "feishu": {
    "enabled": true,
    "chat_id": "oc_9a3c218325fd2cfa42f2a8f6fe03ac02"
  }
}
```

**Get Chat ID:**
- Feishu Group Settings → Group Bot → View Group ID

### Telegram

```json
"channels": {
  "telegram": {
    "enabled": true,
    "chat_id": "-1001234567890"
  }
}
```

**Get Chat ID:**
- Use @userinfobot or check group URL

### Multi-channel Push

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

## ⏰ Scheduling

### OpenClaw Cron

```bash
# Daily at 09:00
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

## 📊 Data Sources

| Source | API Key Required | Description |
|--------|------------------|-------------|
| Tavily | ✅ Required | AI-native search engine |
| HackerNews | ❌ No | Developer community |
| GitHub | ❌ No | Trending AI projects |
| Reddit | ❌ No | AI community discussions |
| Twitter/X | ⚠️ Optional | Viral content |
| Product Hunt | ⚠️ Optional | New product launches |

---

## 🌍 Multi-language Support

| Language | Code | Status |
|----------|------|--------|
| Simplified Chinese | zh | ✅ |
| English | en | ✅ |
| Japanese | ja | ✅ |
| Korean | ko | ✅ |
| Spanish | es | ✅ |

Change the `language` field in `config/config.json` to switch languages.

---

## 📁 Project Structure

```
AiTrend/
├── src/
│   ├── __main__.py              # Entry point
│   ├── core/
│   │   ├── config_loader.py     # Config loader
│   │   ├── sender.py            # Channel sender
│   │   └── deduplicator.py      # Deduplicator
│   └── sources/                 # Data source implementations
├── config/
│   ├── config.example.json      # Config example
│   └── config.json              # User config (create this)
├── .env.example                 # Environment example
├── .env                         # User environment (create this)
└── README.md
```

---

## 📝 Full Configuration Example

```json
{
  "language": "en",
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

## 📄 License

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
