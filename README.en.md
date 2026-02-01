# AiTrend Skill v0.1.1

> 🚀 Multi-source AI Trend Collector - **AI Weekly for Everyone**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg)]()

## ✨ Features

### 🔥 Multi-source Mining
- **6 Data Sources**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- **AI-Native Search**: Tavily designed for LLMs, returns full content
- **Real-time Hotspots**: Social media monitoring for trending content
- **Zero-config Startup**: Only Tavily Key required

### 🔄 Smart Deduplication
- **24-hour Sliding Window**: Same content won't repeat
- **URL Deduplication**: Automatically filters duplicate links
- **Persistent Memory**: Local tracking of sent content
- **Force 10 Items**: Minimum 10 products per output

### 🤖 OpenClaw Integration
- **Depends on OpenClaw**: Message routing, scheduling, LLM summarization
- **Pure Data Collection**: Focus on mining, not sending/summarizing
- **Multi-channel**: Send to any platform via OpenClaw
- **Auto Schedule**: Daily delivery at 09:00

### 🌐 Multi-language Support
- **5 Languages**: Chinese, English, Japanese, Korean, Spanish
- **One-click Switch**: Change output language in config
- **Smart Adaptation**: Data collection language-agnostic
- **Detailed Descriptions**: 200+ words per product

## 🚀 Quick Start

### 🎯 Method 1: Let AI Install Automatically (Recommended)

**Just tell your AI:**

> "Please read https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md and install AiTrend Skill"

Your AI will automatically:
1. Clone the repository to the correct location
2. Check and request necessary API Key (Tavily only)
3. Run and collect data
4. Generate conversational summary via OpenClaw LLM
5. Send to your preferred platform

**Zero-config startup** - Only one Tavily API Key needed!

---

### 💻 Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend

# Configure API Keys
cp .env.example .env
# Edit .env file with your Tavily API Key

# Run
python3 -m src
```

## 📋 API Keys Configuration

Create `.env` file:

```bash
# Required (AI-native search engine)
TAVILY_API_KEY=your_tavily_api_key

# Optional (enhanced data sources)
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CT0=your_twitter_ct0
PRODUCTHUNT_TOKEN=your_producthunt_token
```

## 📊 Data Sources

| Source | Type | API Key Required | Description |
|--------|------|------------------|-------------|
| Tavily | AI Search | ✅ Required | AI-native search, returns full content |
| HackerNews | Developer Community | ❌ No | Show HN and trending discussions |
| GitHub | Open Source | ❌ No | Trending AI projects |
| Reddit | Community | ❌ No | SideProject and more |
| Twitter/X | Real-time | ⚠️ Optional | Viral content and discussions |
| Product Hunt | New Products | ⚠️ Optional | Daily new launches |

**Default Enabled**: Tavily + HackerNews + GitHub + Reddit

## 🌐 Language Configuration

Edit `config/config.json`:

```json
{
  "language": "en",
  "sources": { ... },
  "summarizer": { ... }
}
```

Supported: `zh` (Chinese), `en` (English), `ja` (Japanese), `ko` (Korean), `es` (Spanish)

Default: `zh` (Simplified Chinese)

**Note**: Data collection is language-agnostic. Only the final AI summary output respects the language setting.

## ⏰ Scheduling

```bash
# Daily at 09:00
openclaw cron add \
  --name "aitrend-daily" \
  --schedule "0 9 * * *" \
  --command "python3 -m src" \
  --cwd "~/.openclaw/workspace/AiTrend"
```

### Trigger Commands

Send any of these to trigger immediately:
- "Latest AI hotspots"
- "AI hotspots"
- "Hot news"

## 📄 License

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
