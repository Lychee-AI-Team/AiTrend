# AiTrend Skill v0.1.1

> 🚀 マルチソースAIトレンドコレクター - **誰もが使えるAIウィークリー**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 機能

- 🔥 **マルチソース収集**: Twitter、Product Hunt、HackerNews、GitHub、Brave Search、Reddit
- 🤖 **AI要約**: Gemini 3 Flash Preview インテリジェント分析
- 👥 **ユーザーフレンドリー**: 誰でもすぐに使えるツール
- 📝 **会話的スタイル**: 友達と話すような自然な表現
- 🚫 **ゼロ依存**: Python標準ライブラリのみ、すぐに使える
- 🌐 **多言語対応**: 5言語以上対応（AI要約出力のみ）
- 🎯 **AI自動インストール**: [SKILL.md](SKILL.md)でAIが自己インストール

## 🚀 クイックスタート

### 🎯 方法1: AIに自動インストールさせる（推奨）

**AIにこう伝えてください:**

> 「https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md を読んで、AiTrend Skillをインストールしてください」

AIが自動的に：
1. リポジトリを正しい場所にクローン
2. 必要なAPIキーを確認・要求（Geminiのみ必要）
3. 実行して最初のコンテンツを生成
4. 追加のデータソース設定を確認

**ゼロコンフィグ起動** - Gemini APIキー1つで実行可能！

---

### 💻 方法2: 手動インストール

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# .envファイルを編集
python3 -m src
```

## 🌐 言語設定

`config/config.json`を編集:

```json
{
  "language": "ja",
  "sources": { ... },
  "summarizer": { ... }
}
```

対応言語: `zh` (中国語)、`en` (英語)、`ja` (日本語)、`ko` (韓国語)、`es` (スペイン語)

デフォルト: `zh` (簡体字中国語)

**注意**: データ収集は言語に依存しません。最終的なAI要約出力のみが言語設定を反映します。

## 📄 ライセンス

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
