# AiTrend v0.3.0

🔥 **AI 핫스팟 발견 엔진** - AI 제품 뉴스를 자동 수집 및 발신

<p align="center">
  <a href="https://github.com/Lychee-AI-Team/AiTrend/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Lychee-AI-Team/AiTrend/ci.yml?branch=main&style=flat-square" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

<p align="center">
  <b>🌍 다국어 문서</b> |
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## 📸 스크린샷

<table>
  <tr>
    <td width="50%" align="center">
      <a href="IMG_1034.PNG">
        <img src="IMG_1034.PNG" width="100%" alt="Discord Forum 미리보기1"/>
      </a>
    </td>
    <td width="50%" align="center">
      <a href="IMG_1035.PNG">
        <img src="IMG_1035.PNG" width="100%" alt="Discord Forum 미리보기2"/>
      </a>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="IMG_1036.PNG">
        <img src="IMG_1036.PNG" width="100%" alt="Discord Forum 미리보기3"/>
      </a>
    </td>
    <td width="50%" align="center">
      <a href="IMG_1037.PNG">
        <img src="IMG_1037.PNG" width="100%" alt="Discord Forum 미리보기4"/>
      </a>
    </td>
  </tr>
</table>

<sub align="center">썸네일을 클릭하여 확대 보기</sub>

---

## ✨ 기능

- 🧩 **모듈식 설계** - 정보원과 출력 채널을 자유롭게 조합
- 🤖 **AI 콘텐츠 생성** - Gemini를 사용하여 고품질 설명 자동 생성
- 📊 **멀티소스 지원** - GitHub, Product Hunt, HackerNews, Reddit, Tavily
- 📢 **멀티채널 발송** - Discord, Telegram, Feishu
- 🔄 **자동 중복 제거** - 24시간 슬라이딩 윈도우로 중복 방지

## 🚀 퀵 스타트

### 방법1: 원클릭 설치

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
./install.sh
```

### 방법2: Docker 배포

```bash
docker-compose up -d
```

### 설정

```bash
# 1. API 키 설정
nano .env.keys

# 필수:
# - GEMINI_API_KEY
# - DISCORD_WEBHOOK_URL

# 2. 설정 편집
nano config/config.yaml

# 3. 실행
python3 -m src.hourly
```

## 📁 프로젝트 구조

```
AiTrend/
├── src/              # 코어 코드
│   ├── sources/      # 데이터 소스 모듈
│   ├── core/         # 코어 기능
│   └── hourly.py     # 메인 엔트리
├── config/           # 설정 파일
├── docs/             # 문서
├── scripts/          # 유틸리티 스크립트
├── install.sh        # 설치 스크립트
├── Dockerfile        # Docker 이미지
└── skill.yaml        # OpenClaw Skill 설명
```

## 📄 문서

- [API 키 설정 가이드](docs/API_KEY_SETUP.md)
- [개발 가이드](docs/DEVELOPMENT_GUIDE.md)
- [문제 해결](docs/TROUBLESHOOTING.md)
- [퀵 레퍼런스](docs/QUICK_REFERENCE.md)
- [기여 가이드](CONTRIBUTING.md)

## 🔧 지원 채널

| 채널 | 상태 | 설명 |
|------|------|------|
| Discord Forum | ✅ 지원됨 | 매일 스레드 자동 생성 |
| Discord Text | ✅ 지원됨 | 텍스트 채널로 전송 |
| Telegram | 🚧 개발 중 | 곧 출시 |
| Feishu | 🚧 개발 중 | 곧 출시 |

## 📊 데이터 소스

| 소스 | API 키 | 설명 |
|------|--------|------|
| GitHub Trending | 선택사항 | 인기 AI 프로젝트 |
| Product Hunt | 선택사항 | 신제품 출시 |
| HackerNews | 불필요 | 개발자 커뮤니티 핫토픽 |
| Reddit | 불필요 | AI 커뮤니티 토론 |
| Tavily | 선택사항 | AI 검색 |

## 🤝 기여

모든 형태의 기여를 환영합니다! [기여 가이드](CONTRIBUTING.md)를 확인해 주세요.

## 📜 라이선스

[MIT License](LICENSE)

## 🙏 감사의 말

이 프로젝트에 기여해 주신 모든 분들께 감사드립니다!

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
