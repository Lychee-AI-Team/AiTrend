# AiTrend Skill v0.1.1

> 🚀 マルチソースAIトレンドコレクター - **誰もが使えるAIウィークリー**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 主な機能

### 🔥 マルチソース収集
- **6つのデータソース**: Tavily、HackerNews、GitHub、Reddit、Twitter、Product Hunt
- **AIネイティブ検索**: LLM向けに設計されたTavily、完全なコンテンツを返す
- **リアルタイムホットスポット**: ソーシャルメディア監視
- **ゼロコンフィグ起動**: Tavily Keyのみ必要

### 🔄 スマート重複排除
- **24時間スライディングウィンドウ**: 同じコンテンツは繰り返されない
- **URL重複排除**: 自動的に重複リンクをフィルタリング
- **永続的メモリ**: 送信済みコンテンツのローカル追跡
- **強制10項目**: 出力あたり最小10製品

### 🤖 OpenClaw統合
- **OpenClawに依存**: メッセージルーティング、スケジューリング、LLM要約
- **純粋なデータ収集**: マイニングに集中、送信/要約はOpenClawへ
- **マルチチャンネル**: OpenClaw経由で任意のプラットフォームへ送信
- **自動スケジュール**: 毎日09:00に自動配信

### 🌐 多言語サポート
- **5言語**: 中国語、英語、日本語、韓国語、スペイン語
- **ワンクリック切り替え**: 設定で出力言語を変更
- **スマート適応**: データ収集は言語に依存しない
- **詳細な説明**: 製品あたり200文字以上

## 🚀 クイックスタート

### 🎯 方法1: AIに自動インストールさせる（推奨）

**AIにこう伝えてください:**

> 「https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md を読んで、AiTrend Skillをインストールしてください」

AIが自動的に：
1. リポジトリを正しい場所にクローン
2. 必要なAPIキーを確認・要求（Tavilyのみ）
3. 実行してデータを収集
4. OpenClaw LLM経由で会話的な要約を生成
5. 指定のプラットフォームに送信

**ゼロコンフィグ起動** - Tavily APIキー1つで実行可能！

---

### 💻 方法2: 手動インストール

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# .envファイルを編集
python3 -m src
```

## 📊 データソース

| ソース | タイプ | API Key必要 | 説明 |
|--------|--------|-------------|------|
| Tavily | AI検索 | ✅ 必須 | AIネイティブ検索、完全なコンテンツを返す |
| HackerNews | 開発者コミュニティ | ❌ いいえ | Show HNと人気の議論 |
| GitHub | オープンソース | ❌ いいえ | トレンドAIプロジェクト |
| Reddit | コミュニティ | ❌ いいえ | SideProjectなど |
| Twitter/X | リアルタイム | ⚠️ オプション | Viralコンテンツと議論 |
| Product Hunt | 新製品 | ⚠️ オプション | 毎日の新発売 |

## 🌐 言語設定

`config/config.json`を編集:

```json
{
  "language": "ja",
  "sources": { ... },
  "summarizer": { ... }
}
```

対応: `zh` (中国語)、`en` (英語)、`ja` (日本語)、`ko` (韓国語)、`es` (スペイン語)

デフォルト: `zh` (簡体字中国語)

**注意**: データ収集は言語に依存しません。最終的なAI要約出力のみが言語設定を反映します。

## 📄 ライセンス

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
