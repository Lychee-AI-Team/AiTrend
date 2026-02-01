# AiTrend Skill v0.1.1

> 🚀 멀티소스 AI 트렌드 수집기 - **누구나 사용할 수 있는 AI 위클리**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 주요 기능

### 🔥 멀티소스 수집
- **6개 데이터 소스**: Tavily, HackerNews, GitHub, Reddit, Twitter, Product Hunt
- **AI 네이티브 검색**: LLM용으로 설계된 Tavily, 전체 콘텐츠 반환
- **실시간 핫스팟**: 소셜 미디어 모니터링
- **제로 설정 시작**: Tavily Key만 필요

### 🔄 스마트 중복 제거
- **24시간 슬라이딩 윈도우**: 동일한 콘텐츠는 반복되지 않음
- **URL 중복 제거**: 자동으로 중복 링크 필터링
- **영구 메모리**: 전송된 콘텐츠의 로컬 추적
- **강제 10개 항목**: 출력당 최소 10개 제품

### 🤖 OpenClaw 통합
- **OpenClaw 의존**: 메시지 라우팅, 스케줄링, LLM 요약
- **순수 데이터 수집**: 마이닝에 집중, 전송/요약은 OpenClaw에 위임
- **멀티채널**: OpenClaw를 통해 모든 플랫폼으로 전송
- **자동 일정**: 매일 09:00 자동 전송

### 🌐 다국어 지원
- **5개 언어**: 중국어, 영어, 일본어, 한국어, 스페인어
- **원클릭 전환**: 설정에서 출력 언어 변경
- **스마트 적응**: 데이터 수집은 언어에 독립적
- **자세한 설명**: 제품당 200자 이상

## 🚀 빠른 시작

### 🎯 방법 1: AI에게 자동 설치 요청 (권장)

**AI에게 다음과 같이 말하세요:**

> "https://github.com/Lychee-AI-Team/AiTrend/blob/main/SKILL.md 를 읽고 AiTrend Skill을 설치해주세요"

AI가 자동으로:
1. 저장소를 올바른 위치에 클론
2. 필요한 API 키 확인 및 요청 (Tavily만 필요)
3. 실행하여 데이터 수집
4. OpenClaw LLM을 통해 대화형 요약 생성
5. 지정된 플랫폼에 전송

**제로 설정 시작** - Tavily API 키 하나로 실행 가능!

---

### 💻 방법 2: 수동 설치

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
cp .env.example .env
# .env 파일 편집
python3 -m src
```

## 📊 데이터 소스

| 소스 | 타입 | API Key 필요 | 설명 |
|------|------|--------------|------|
| Tavily | AI 검색 | ✅ 필수 | AI 네이티브 검색, 전체 콘텐츠 반환 |
| HackerNews | 개발자 커뮤니티 | ❌ 아니오 | Show HN 및 인기 토론 |
| GitHub | 오픈 소스 | ❌ 아니오 | 트렌드 AI 프로젝트 |
| Reddit | 커뮤니티 | ❌ 아니오 | SideProject 등 |
| Twitter/X | 실시간 | ⚠️ 옵션 | Viral 콘텐츠 및 토론 |
| Product Hunt | 신제품 | ⚠️ 옵션 | 매일 신제품 출시 |

## 🌐 언어 설정

`config/config.json` 편집:

```json
{
  "language": "ko",
  "sources": { ... },
  "summarizer": { ... }
}
```

지원: `zh` (중국어), `en` (영어), `ja` (일본어), `ko` (한국어), `es` (스페인어)

기본값: `zh` (간체 중국어)

**참고**: 데이터 수집은 언어에 독립적입니다. 최종 AI 요약 출력만 언어 설정을 반영합니다.

## 📄 라이선스

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
