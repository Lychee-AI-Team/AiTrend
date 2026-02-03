# AiTrend v0.3.0

🔥 **AI 热点发现引擎** - 自动采集和发布 AI 产品资讯

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Version-0.3.0-orange.svg?style=flat-square" alt="Version">
</p>

## ✨ 特性

- 🧩 **模块化设计** - 自由组合信息源和输出渠道
- 🤖 **AI 内容生成** - 使用 Gemini 自动生成高质量中文介绍
- 📊 **多数据源支持** - GitHub、Product Hunt、HackerNews、Reddit、Tavily
- 📢 **多渠道发布** - Discord、Telegram、飞书
- 🔄 **自动去重** - 24小时滑动窗口防止重复

## 🚀 快速开始

### 方式1：一键安装

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
./install.sh
```

### 方式2：Docker 部署

```bash
docker-compose up -d
```

### 配置

```bash
# 1. 配置 API Key
nano .env.keys

# 必需：
# - GEMINI_API_KEY
# - DISCORD_WEBHOOK_URL

# 2. 编辑配置
nano config/config.yaml

# 3. 运行
python3 -m src.hourly
```

## 📁 项目结构

```
AiTrend/
├── src/              # 核心代码
│   ├── sources/      # 信息源模块
│   ├── core/         # 核心功能
│   └── hourly.py     # 主入口
├── config/           # 配置文件
├── docs/             # 文档
├── install.sh        # 安装脚本
├── Dockerfile        # Docker 镜像
└── skill.yaml        # OpenClaw Skill 描述
```

## 📄 文档

- [安装指南](docs/installation.md)
- [配置说明](docs/configuration.md)
- [API 文档](docs/api.md)

## 📜 许可证

MIT License

---

**GitHub**: https://github.com/Lychee-AI-Team/AiTrend
