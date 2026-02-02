<h1 align="center">AiTrend Skill v0.2.0</h1>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20WSL-lightgrey.svg?style=flat-square" alt="Platform">
</p>

<p align="center">
  <b>🚀 멀티소스 AI 트렌드 수집기 - 멀티채널 지원</b>
</p>

<p align="center">
  <a href="#-퀵-스타트">퀵 스타트</a> •
  <a href="#-기능">기능</a> •
  <a href="#-설정">설정</a> •
  <a href="#-채널-설정">채널</a> •
  <a href="#-다국어">다국어</a>
</p>

---

## 🌍 다국어 문서

<p align="center">
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## ✨ 기능

- 🔥 **멀티소스 수집**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- 📢 **멀티채널 발송**: Discord, Feishu, Telegram, Console
- 🌐 **다국어 지원**: 중국어, 영어, 일본어, 한국어, 스페인어
- 🔄 **중복 제거**: 24시간 슬라이딩 윈도우
- ⚡ **제로 설정**: Tavily Key만 필요

---

## 🚀 퀵 스타트

### 1️⃣ 리포지토리 클론

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2️⃣ 환경 변수 설정

```bash
cp .env.example .env
# .env를 편집하여 TAVILY_API_KEY 추가
```

### 3️⃣ 발송 채널 설정

```bash
cp config/config.example.json config/config.json
# config/config.json을 편집하여 필요한 채널 활성화
```

### 4️⃣ 실행

```bash
python3 -m src
```

---

## 🔧 설정

### 기본 설정

`config/config.json`을 편집:

```json
{
  "language": "ko",
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

## 📢 채널 설정

AiTrend는 여러 출력 채널을 지원합니다. 여러 채널을 동시에 활성화할 수 있습니다:

### Console (기본)

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

**Channel ID 가져오기:**
1. Discord 설정 → 고급 → 개발자 모드 활성화
2. 채널 우클릭 → 채널 ID 복사

### Feishu (비서)

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

### 멀티채널 발송

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

## ⏰ 스케줄링

### OpenClaw Cron

```bash
# 매일 아침 9:00 자동 실행
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

## 📊 데이터 소스

| 소스 | API Key 필요 | 설명 |
|------|--------------|------|
| Tavily | ✅ 필요 | AI 네이티브 검색 엔진 |
| HackerNews | ❌ 불필요 | 개발자 커뮤니티 |
| GitHub | ❌ 불필요 | 트렌딩 AI 프로젝트 |
| Reddit | ❌ 불필요 | AI 커뮤니티 토론 |
| Twitter/X | ⚠️ 옵션 | 바이럴 콘텐츠 |
| Product Hunt | ⚠️ 옵션 | 신제품 출시 |

---

## 🌍 다국어 지원

| 언어 | 코드 | 상태 |
|------|------|--------|
| 중국어 간체 | zh | ✅ |
| 영어 | en | ✅ |
| 일본어 | ja | ✅ |
| 한국어 | ko | ✅ |
| 스페인어 | es | ✅ |

`config/config.json`의 `language` 필드를 변경하여 언어를 전환합니다.

---

## 📁 프로젝트 구조

```
AiTrend/
├── src/
│   ├── __main__.py              # 진입점
│   ├── core/
│   │   ├── config_loader.py     # 설정 로더
│   │   ├── sender.py            # 채널 발송
│   │   └── deduplicator.py      # 중복 제거
│   └── sources/                 # 데이터 소스 구현
├── config/
│   ├── config.example.json      # 설정 예시
│   └── config.json              # 사용자 설정
├── .env.example                 # 환경 변수 예시
├── .env                         # 사용자 환경 변수
└── README.md
```

---

## 📝 전체 설정 예시

```json
{
  "language": "ko",
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

## 📄 라이선스

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
