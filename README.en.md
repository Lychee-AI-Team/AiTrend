# AiTrend v0.3.0

🔥 **AI Hotspot Discovery Engine** - Automatically collect and publish AI product news

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

<p align="center">
  <b>🌍 Multi-language Docs</b> |
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ Features

- 🧩 **Modular Design** - Combine data sources and output channels freely
- 🤖 **AI Content Generation** - Use Gemini to auto-generate high-quality descriptions
- 📊 **Multi-source Support** - GitHub, Product Hunt, HackerNews, Reddit, Tavily
- 📢 **Multi-channel Publishing** - Discord, Telegram, Feishu
- 🔄 **Auto Deduplication** - 24-hour sliding window prevents duplicates

## 🚀 Quick Start

### Option 1: One-click Install

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
./install.sh
```

### Option 2: Docker Deploy

```bash
docker-compose up -d
```

### Configuration

```bash
# 1. Configure API Keys
nano .env.keys

# Required:
# - GEMINI_API_KEY
# - DISCORD_WEBHOOK_URL

# 2. Edit config
nano config/config.yaml

# 3. Run
python3 -m src.hourly
```

## 📁 Project Structure

```
AiTrend/
├── src/              # Core code
│   ├── sources/      # Data source modules
│   ├── core/         # Core functionality
│   └── hourly.py     # Main entry
├── config/           # Configuration files
├── docs/             # Documentation
├── install.sh        # Install script
├── Dockerfile        # Docker image
└── skill.yaml        # OpenClaw Skill description
```

## 📄 Documentation

- [API Key Setup Guide](docs/API_KEY_SETUP.md)
- [Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Quick Reference](docs/QUICK_REFERENCE.md)

## 🔧 Supported Channels

| Channel | Status | Description |
|---------|--------|-------------|
| Discord Forum | ✅ Supported | Auto-create daily threads |
| Discord Text | ✅ Supported | Send to text channel |
| Telegram | 🚧 In Progress | Coming soon |
| Feishu | 🚧 In Progress | Coming soon |

## 📊 Data Sources

| Source | API Key | Description |
|--------|---------|-------------|
| GitHub Trending | Optional | Trending AI projects |
| Product Hunt | Optional | New product launches |
| HackerNews | Not needed | Developer community hotspots |
| Reddit | Not needed | AI community discussions |
| Tavily | Optional | AI search |

## 📜 License

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
