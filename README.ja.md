# AiTrend v0.3.0

🔥 **AIホットトピック発見エンジン** - AI製品ニュースを自動収集・公開

<p align="center">
  <a href="https://github.com/Lychee-AI-Team/AiTrend/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Lychee-AI-Team/AiTrend/ci.yml?branch=main&style=flat-square" alt="CI">
  </a>
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

## ✨ 特徴

- 🧩 **モジュール化設計** - 情報源と出力チャンネルを自由に組み合わせ
- 🤖 **AIコンテンツ生成** - Geminiを使用して高品質な日本語紹介を自動生成
- 📊 **複数データソース対応** - GitHub、Product Hunt、HackerNews、Reddit、Tavily
- 📢 **複数チャンネル公開** - Discord、Telegram、Feishu
- 🔄 **自動重複排除** - 24時間スライディングウィンドウで重複防止

## 🚀 クイックスタート

### 方法1：手動インストール

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
cp .env.example .env
nano .env

# 実行
python3 -m src.hourly
```

### 方法2：Dockerデプロイ

```bash
docker-compose up -d
```

### 設定要件

必要な環境変数（`.env`ファイル）：
- `GEMINI_API_KEY` - Gemini APIキー
- `DISCORD_WEBHOOK_URL` - Discord Webhook URL

オプション：
- `PRODUCTHUNT_TOKEN` - Product Hunt APIトークン
- `TAVILY_API_KEY` - Tavily APIキー

## 📁 プロジェクト構成

```
AiTrend/
├── src/                    # コアコード
│   ├── __main__.py        # モジュールエントリ
│   ├── hourly.py          # メイン実行ロジック
│   ├── llm_content_generator.py  # LLMコンテンツ生成
│   ├── sources/           # データソースモジュール
│   │   ├── base.py
│   │   ├── github_trending.py
│   │   ├── producthunt.py
│   │   ├── reddit.py
│   │   ├── tavily.py
│   │   ├── hackernews.py
│   │   └── twitter.py
│   └── core/              # コアサービス
│       ├── config_loader.py
│       ├── deduplicator.py
│       └── webhook_sender.py
├── publishers/            # 公開モジュール
│   ├── base.py
│   ├── forum_publisher.py
│   └── text_publisher.py
├── tests/                 # テストディレクトリ
├── config/                # 設定ファイル
│   ├── config.json
│   └── config.example.yaml
├── docs/                  # ドキュメント
├── scripts/               # ユーティリティスクリプト
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── skill.yaml
```

## 📄 ドキュメント

- [APIキー設定ガイド](docs/API_KEY_SETUP.md)
- [開発ガイド](docs/DEVELOPMENT_GUIDE.md)
- [トラブルシューティング](docs/TROUBLESHOOTING.md)
- [貢献ガイド](CONTRIBUTING.md)

## 🔧 サポートチャンネル

| チャンネル | 状態 | 説明 |
|------|------|------|
| Discord Forum | ✅ サポート済 | 自動で毎日のトピック投稿を作成 |
| Discord Text | ✅ サポート済 | テキストチャンネルに送信 |
| Telegram | 🚧 開発中 | 近日サポート予定 |
| Feishu | 🚧 開発中 | 近日サポート予定 |

## 📊 データソース

| データソース | APIキー | 説明 |
|--------|---------|------|
| GitHub Trending | オプション | 人気AIプロジェクト |
| Product Hunt | オプション | 新製品リリース |
| HackerNews | 不要 | 開発者コミュニティのホットトピック |
| Reddit | 不要 | AIコミュニティ議論 |
| Tavily | オプション | AI検索 |

## 🤝 貢献

あらゆる形の貢献を歓迎します！[貢献ガイド](CONTRIBUTING.md)をご覧ください。

## 📜 ライセンス

[MIT License](LICENSE)
