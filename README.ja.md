# AiTrend v0.3.0

🔥 **AIホットスポット発見エンジン** - AI製品ニュースを自動収集・発信

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

<p align="center">
  <b>🌍 多言語ドキュメント</b> |
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ 機能

- 🧩 **モジュール設計** - 情報源と出力チャネルを自由に組み合わせ
- 🤖 **AIコンテンツ生成** - Geminiを使用して高品質な説明を自動生成
- 📊 **マルチソース対応** - GitHub、Product Hunt、HackerNews、Reddit、Tavily
- 📢 **マルチチャネル配信** - Discord、Telegram、Feishu
- 🔄 **自動重複排除** - 24時間スライディングウィンドウで重複防止

## 🚀 クイックスタート

### 方法1：ワンクリックインストール

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
./install.sh
```

### 方法2：Dockerデプロイ

```bash
docker-compose up -d
```

### 設定

```bash
# 1. APIキーを設定
nano .env.keys

# 必須：
# - GEMINI_API_KEY
# - DISCORD_WEBHOOK_URL

# 2. 設定を編集
nano config/config.yaml

# 3. 実行
python3 -m src.hourly
```

## 📁 プロジェクト構成

```
AiTrend/
├── src/              # コアコード
│   ├── sources/      # データソースモジュール
│   ├── core/         # コア機能
│   └── hourly.py     # メインエントリ
├── config/           # 設定ファイル
├── docs/             # ドキュメント
├── install.sh        # インストールスクリプト
├── Dockerfile        # Dockerイメージ
└── skill.yaml        # OpenClaw Skill記述
```

## 📄 ドキュメント

- [APIキー設定ガイド](docs/API_KEY_SETUP.md)
- [開発ガイド](docs/DEVELOPMENT_GUIDE.md)
- [トラブルシューティング](docs/TROUBLESHOOTING.md)
- [クイックリファレンス](docs/QUICK_REFERENCE.md)

## 🔧 対応チャネル

| チャネル | 状態 | 説明 |
|----------|------|------|
| Discord Forum | ✅ 対応済 | 毎日のスレッドを自動作成 |
| Discord Text | ✅ 対応済 | テキストチャネルに送信 |
| Telegram | 🚧 開発中 | 近日公開 |
| Feishu | 🚧 開発中 | 近日公開 |

## 📊 データソース

| ソース | APIキー | 説明 |
|--------|---------|------|
| GitHub Trending | 任意 | 人気のAIプロジェクト |
| Product Hunt | 任意 | 新製品リリース |
| HackerNews | 不要 | 開発者コミュニティの注目トピック |
| Reddit | 不要 | AIコミュニティの議論 |
| Tavily | 任意 | AI検索 |

## 📜 ライセンス

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
