# AiTrend v0.3.0

🔥 **AI 热点发现引擎** - 自动采集和发布 AI 产品资讯

<p align="center">
  <a href="https://github.com/Lychee-AI-Team/AiTrend/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/Lychee-AI-Team/AiTrend/ci.yml?branch=main&style=flat-square" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

<p align="center">
  <b>🌍 多语言文档</b> |
  <a href="README.md">🇨🇳 简体中文</a> •
  <a href="README.en.md">🇺🇸 English</a> •
  <a href="README.ja.md">🇯🇵 日本語</a> •
  <a href="README.ko.md">🇰🇷 한국어</a> •
  <a href="README.es.md">🇪🇸 Español</a>
</p>

---

## 📸 运行效果

<table>
  <tr>
    <td width="50%" align="center">
      <a href="IMG_1034.PNG">
        <img src="IMG_1034.PNG" width="100%" alt="Discord Forum 效果1"/>
      </a>
    </td>
    <td width="50%" align="center">
      <a href="IMG_1035.PNG">
        <img src="IMG_1035.PNG" width="100%" alt="Discord Forum 效果2"/>
      </a>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <a href="IMG_1036.PNG">
        <img src="IMG_1036.PNG" width="100%" alt="Discord Forum 效果3"/>
      </a>
    </td>
    <td width="50%" align="center">
      <a href="IMG_1037.PNG">
        <img src="IMG_1037.PNG" width="100%" alt="Discord Forum 效果4"/>
      </a>
    </td>
  </tr>
</table>

<sub align="center">点击缩略图查看大图</sub>

---

## ✨ 特性

- 🧩 **模块化设计** - 自由组合信息源和输出渠道
- 🤖 **AI 内容生成** - 使用 Gemini 自动生成高质量中文介绍
- 📊 **多数据源支持** - GitHub、Product Hunt、HackerNews、Reddit、Tavily
- 📢 **多渠道发布** - Discord、Telegram、飞书
- 🔄 **自动去重** - 24小时滑动窗口防止重复

## 🚀 快速开始

### 方式1：手动安装

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env

# 运行
python3 -m src.hourly
```

### 方式2：Docker 部署

```bash
docker-compose up -d
```

### 配置要求

必需的环境变量（`.env` 文件）：
- `GEMINI_API_KEY` - Gemini API 密钥
- `DISCORD_WEBHOOK_URL` - Discord Webhook URL

可选：
- `PRODUCTHUNT_TOKEN` - Product Hunt API 令牌
- `TAVILY_API_KEY` - Tavily API 密钥

## 📁 项目结构

```
AiTrend/
├── src/                    # 核心代码
│   ├── __main__.py        # 模块入口
│   ├── hourly.py          # 主运行逻辑
│   ├── llm_content_generator.py  # LLM内容生成
│   ├── sources/           # 数据源模块
│   │   ├── base.py
│   │   ├── github_trending.py
│   │   ├── producthunt.py
│   │   ├── reddit.py
│   │   ├── tavily.py
│   │   ├── hackernews.py
│   │   └── twitter.py
│   └── core/              # 核心服务
│       ├── config_loader.py
│       ├── deduplicator.py
│       └── webhook_sender.py
├── publishers/            # 发布模块
│   ├── base.py
│   ├── forum_publisher.py
│   └── text_publisher.py
├── tests/                 # 测试目录
├── config/                # 配置文件
│   ├── config.json
│   └── config.example.yaml
├── docs/                  # 文档
├── scripts/               # 工具脚本
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── skill.yaml
```

## 📄 文档

- [API Key 设置指南](docs/API_KEY_SETUP.md)
- [开发指南](docs/DEVELOPMENT_GUIDE.md)
- [故障排查](docs/TROUBLESHOOTING.md)
- [快速参考](docs/QUICK_REFERENCE.md)
- [贡献指南](CONTRIBUTING.md)

## 🔧 支持的渠道

| 渠道 | 状态 | 说明 |
|------|------|------|
| Discord Forum | ✅ 已支持 | 自动创建每日主题帖 |
| Discord Text | ✅ 已支持 | 发送到文字频道 |
| Telegram | 🚧 开发中 | 即将支持 |
| 飞书 | 🚧 开发中 | 即将支持 |

## 📊 数据源

| 数据源 | API Key | 说明 |
|--------|---------|------|
| GitHub Trending | 可选 | 热门 AI 项目 |
| Product Hunt | 可选 | 新产品发布 |
| HackerNews | 无需 | 开发者社区热点 |
| Reddit | 无需 | AI 社区讨论 |
| Tavily | 可选 | AI 搜索 |

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md)。

## 📜 许可证

[MIT License](LICENSE)

## 🙏 致谢

感谢所有贡献者为这个项目付出的努力！

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
