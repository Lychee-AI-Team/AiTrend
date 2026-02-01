# AiTrend Skill v0.1.1

> 🚀 멀티소스 AI 트렌드 수집기 - **누구나 사용할 수 있는 AI 위클리**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 기능

- 🔥 **멀티소스 수집**: Twitter, Product Hunt, HackerNews, GitHub, Brave Search, Reddit
- 🤖 **AI 요약**: Gemini 3 Flash Preview 지능형 분석
- 👥 **사용자 친화적**: 일반인도 바로 사용할 수 있는 도구
- 📝 **대화형 스타일**: 친구와 대화하듯 자연스러운 표현
- 🚫 **제로 의존성**: Python 표준 라이브러리만, 바로 사용 가능
- 🌐 **다국어 지원**: 5개 이상 언어 지원 (AI 요약 출력만)
- 🎯 **AI 자동 설치**: [SKILL.md](SKILL.md)로 AI가 자체 설치

## 🚀 빠른 시작

### 🎯 방법 1: AI에게 자동 설치 요청 (권장)

**AI에게 다음과 같이 말하세요:**

> "https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md 를 읽고 AiTrend Skill을 설치해주세요"

AI가 자동으로:
1. 저장소를 올바른 위치에 클론
2. 필요한 API 키 확인 및 요청 (Gemini만 필요)
3. 실행하여 첫 번째 콘텐츠 생성
4. 추가 데이터 소스 설정 확인

**제로 설정 시작** - Gemini API 키 하나로 실행 가능!

---

### 💻 방법 2: 수동 설치

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# .env 파일 편집
python3 -m src
```

## 🌐 언어 설정

`config/config.json` 편집:

```json
{
  "language": "ko",
  "sources": { ... },
  "summarizer": { ... }
}
```

지원 언어: `zh` (중국어), `en` (영어), `ja` (일본어), `ko` (한국어), `es` (스페인어)

기본값: `zh` (간체 중국어)

**참고**: 데이터 수집은 언어에 독립적입니다. 최종 AI 요약 출력만 언어 설정을 반영합니다.

## 📄 라이선스

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
