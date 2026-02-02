<h1 align="center">AiTrend Skill v0.2.0</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<p align="center">
  <b>🚀 マルチソースAIトレンドコレクター - マルチチャンネル対応</b>
</p>

<p align="center">
  <a href="#-クイックスタート">クイックスタート</a> •
  <a href="#-機能">機能</a> •
  <a href="#-設定">設定</a> •
  <a href="#-チャンネル設定">チャンネル</a> •
  <a href="#-多言語">多言語</a>
</p>

---

## 🌍 多言語ドキュメント

<p align="center">
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ 機能

- 🔥 **マルチソース収集**: Tavily、HackerNews、GitHub、Reddit、Twitter、Product Hunt
- 📢 **マルチチャンネル配信**: Discord、Feishu、Telegram、Console
- 🌐 **多言語対応**: 中国語、英語、日本語、韓国語、スペイン語
- 🔄 **重複排除**: 24時間スライディングウィンドウ
- ⚡ **ゼロ設定**: Tavily Keyのみ必要

---

## 🚀 クイックスタート

### 1️⃣ リポジトリをクローン

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2️⃣ 環境変数を設定

```bash
cp .env.example .env
# .envを編集し、TAVILY_API_KEYを追加
```

### 3️⃣ 配信チャンネルを設定

```bash
cp config/config.example.json config/config.json
# config/config.jsonを編集し、必要なチャンネルを有効化
```

### 4️⃣ 実行

```bash
python3 -m src
```

---

## 🔧 設定

### 基本設定

`config/config.json`を編集：

```json
{
  "language": "ja",
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

## 📢 チャンネル設定

AiTrendは複数の出力チャンネルをサポートしています。複数のチャンネルを同時に有効にできます：

### Console（デフォルト）

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

**Channel IDの取得方法：**
1. Discord設定 → 詳細設定 → 開発者モードをオン
2. チャンネルを右クリック → チャンネルIDをコピー

### Feishu（飛書）

```json
"channels": {
  "feishu": {
    "enabled": true,
    "chat_id": "oc_9a3c218325fd2cfa42f2a8f6fe03ac02"
  }
}
```

### Telegram

```json
"channels": {
  "telegram": {
    "enabled": true,
    "chat_id": "-1001234567890"
  }
}
```

### マルチチャンネル配信

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

## ⏰ スケジューリング

### OpenClaw Cron

```bash
# 毎朝9:00に自動実行
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

## 📊 データソース

| ソース | API Key 必要 | 説明 |
|--------|--------------|------|
| Tavily | ✅ 必要 | AIネイティブ検索エンジン |
| HackerNews | ❌ 不要 | 開発者コミュニティ |
| GitHub | ❌ 不要 | トレンドAIプロジェクト |
| Reddit | ❌ 不要 | AIコミュニティ議論 |
| Twitter/X | ⚠️ オプション | バイラルコンテンツ |
| Product Hunt | ⚠️ オプション | 新製品リリース |

---

## 🌍 多言語対応

| 言語 | コード | 状態 |
|------|--------|------|
| 簡体中国語 | zh | ✅ |
| 英語 | en | ✅ |
| 日本語 | ja | ✅ |
| 韓国語 | ko | ✅ |
| スペイン語 | es | ✅ |

`config/config.json`の`language`フィールドを変更して言語を切り替えます。

---

## 📁 プロジェクト構成

```
AiTrend/
├── src/
│   ├── __main__.py              # エントリーポイント
│   ├── core/
│   │   ├── config_loader.py     # 設定ローダー
│   │   ├── sender.py            # チャンネル送信
│   │   └── deduplicator.py      # 重複排除
│   └── sources/                 # データソース実装
├── config/
│   ├── config.example.json      # 設定例
│   └── config.json              # ユーザー設定
├── .env.example                 # 環境変数例
├── .env                         # ユーザー環境変数
└── README.md
```

---

## 📝 完全な設定例

```json
{
  "language": "ja",
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

## 📄 ライセンス

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
