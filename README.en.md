# AiTrend Skill v0.1.0

> 🚀 Multi-source AI Trend Collector - **AI Weekly for Everyone**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg)]()

## ✨ Features

- 🔥 **Multi-source Mining**: Twitter, Product Hunt, HackerNews, GitHub, Brave Search, Reddit
- 🤖 **AI Summary**: Gemini 3 Flash Preview intelligent analysis
- 👥 **User-friendly**: Tools that ordinary people can use immediately
- 📝 **Conversational Style**: Natural chat-like expression
- 🚫 **Zero Dependencies**: Pure Python standard library, works out of the box
- 🌐 **Multi-language**: Support for 5+ languages (content summary only)
- 🎯 **AI Auto-install**: Provide [SKILL.md](SKILL.md) for AI self-installation

## 🚀 Quick Start

### 🎯 Method 1: Let AI Install Automatically (Recommended)

**Just tell your AI:**

> "Please read https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md and install AiTrend Skill according to the instructions"

Your AI will automatically:
1. Clone the repository to the correct location
2. Check and request necessary API Keys (only Gemini required)
3. Run and generate the first content
4. Ask if you want to configure more data sources

**Zero-config startup** - Only one Gemini API Key needed to run!

---

### 💻 Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend

# Configure API Keys
cp .env.example .env
# Edit .env file with your API Keys

# Run
python3 -m src
```

## 📋 API Keys Configuration

Create `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (for more data sources)
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CT0=your_twitter_ct0
PRODUCTHUNT_TOKEN=your_producthunt_token
BRAVE_API_KEY=your_brave_api_key
```

## 🌐 Language Configuration

Edit `config/config.json`:

```json
{
  "language": "en",
  "sources": { ... },
  "summarizer": { ... }
}
```

Supported languages: `zh` (Chinese), `en` (English), `ja` (Japanese), `ko` (Korean), `es` (Spanish)

Default: `zh` (Simplified Chinese)

**Note**: Data collection is language-agnostic. Only the final AI summary output respects the language setting.

## 📊 Data Sources

| Source | Type | API Key Required |
|--------|------|------------------|
| HackerNews | Developer Community | No |
| Reddit | Community Discussion | No |
| GitHub | Open Source Projects | No |
| Twitter/X | Real-time Content | Yes |
| Product Hunt | New Products | Yes |
| Brave Search | Web Search | Yes |

## 📄 License

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
