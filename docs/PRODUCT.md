# AiTrend 视频自动生成系统 - v1.0

**版本号**: v1.0  
**发布日期**: 2026-02-06  
**状态**: 已交付 ✅

---

## 📋 产品概述

AiTrend 视频自动生成系统是一个自动化工具，用于将AI热点资讯转换为短视频内容。系统支持多种数据源，自动生成TTS语音，使用Remotion渲染高质量视频。

---

## ✨ 核心功能

### 1. 多数据源支持
- **Product Hunt** - AI产品发布平台
- **Hacker News** - 技术社区热点
- **GitHub Trending** - 开源项目趋势
- **Tavily Search** - AI搜索引擎

### 2. 自动化视频制作
- 自动获取热点信息
- AI生成中文解读文案
- TTS语音合成（支持语速调节）
- 网站截图自动化（绕过Cloudflare）
- Remotion视频渲染

### 3. 智能截图方案
- 使用 ScreenshotAPI.net
- 绕过Cloudflare和反爬虫
- 成功率: 100%

---

## 🎯 视频规格

| 参数 | 值 |
|------|-----|
| **分辨率** | 1080x1920 (竖屏 9:16) |
| **帧率** | 30fps |
| **时长** | 约2分钟 |
| **语速** | 1.5倍 |
| **格式** | MP4 |

### 视频结构
1. **开场** (5秒) - Logo + 欢迎语
2. **热点1** (38秒) - 中文解读 + 截图动画
3. **热点2** (40秒) - 中文解读 + 截图动画
4. **热点3** (35秒) - 中文解读 + 截图动画
5. **结尾** (5秒) - Logo + 结束语

---

## 🎨 设计规范

### 视觉风格
- **背景**: 深色渐变 (#0a0a0f → #1a1a2e)
- **主色调**: 蓝色渐变 (#00d4ff → #7b2cbf)
- **Logo**: 圆角40px + 阴影效果
- **截图**: 1200x800，缩放动画 (1.2 → 0.833)

### 动画效果
- **截图动画**: 水平居中，从大到小
- **缓动函数**: Easing.out(Easing.ease) 先快后慢
- **动画时长**: 等于场景时长 (自动同步)

### 文案规范
- **字数**: 250-300字每条热点
- **语言**: 中文解读
- **内容**: 产品介绍 + 功能特点 + 应用场景 + GitHub星标

---

## 🔧 技术栈

### 后端
- **Python** - 数据处理、API集成
- **Node.js** - Remotion视频渲染
- **TypeScript** - 视频组件开发

### 视频渲染
- **Remotion** - React视频制作框架
- **FFmpeg** - 视频编码

### 数据源API
- **Product Hunt API** - 产品数据
- **GitHub API** - 开源项目数据
- **Hacker News API** - 社区热点
- **ScreenshotAPI.net** - 网站截图
- **Minimax TTS** - 语音合成

---

## 📁 项目结构

```
AiTrend/
├── src/                          # 后端源码
│   ├── sources/                  # 数据源
│   │   ├── producthunt.py
│   │   ├── hackernews.py
│   │   ├── github_trending.py
│   │   └── tavily.py
│   ├── core/                     # 核心逻辑
│   │   ├── deduplicator.py
│   │   └── summarizer.py
│   └── __main__.py               # 入口
├── video/                        # 视频制作
│   ├── src/                      # Remotion组件
│   │   ├── index-final.tsx       # 最终版模板
│   │   ├── index-with-screenshots.tsx
│   │   └── ...
│   ├── assets/audio/             # TTS音频
│   └── data/                     # 视频配置
├── memory/                       # 数据存储
│   └── sent_articles.json
├── config/                       # 配置文件
│   └── config.json
├── docs/                         # 文档
│   ├── PRODUCT.md                # 产品文档
│   ├── LESSONS_LEARNED.md        # 经验总结
│   └── SCREENSHOT_RESEARCH.md    # 截图调研
└── .env                          # 环境变量
```

---

## 🚀 使用流程

### 1. 数据收集
```bash
python -m src
```
- 从各数据源获取AI热点
- 去重过滤
- 存储到 memory/sent_articles.json

### 2. 视频制作
```bash
# 选择3条热点
cd video
python scripts/generate_video.py

# 下载截图
python scripts/download_screenshots.py

# 生成TTS
python scripts/generate_tts.py
```

### 3. 视频渲染
```bash
cd video/src
npx remotion render index-final.tsx DailyNewsFinal ../output/video.mp4
```

---

## 💰 成本分析

### 免费额度
| 服务 | 免费额度 | 实际使用 |
|------|----------|----------|
| ScreenshotAPI.net | 100次/月 | 90次/月 |
| GitHub API | 5000次/小时 | <100次/天 |
| Product Hunt | 依赖Token | 按需使用 |

### 预估成本
- **截图API**: $0 (免费额度足够)
- **TTS服务**: Minimax (已配置API Key)
- **总成本**: 基本免费

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| **截图成功率** | 100% (5/5) |
| **视频渲染时长** | 约5-8分钟 |
| **单视频大小** | 约50-100MB |
| **音频生成时间** | 约2-3分钟 |

---

## ✅ 质量标准

### 内容质量
- ✅ 中文解读 250-300字
- ✅ 包含产品功能、应用场景、GitHub星标
- ✅ 语速1.5倍，清晰流畅

### 视觉质量
- ✅ 截图1200x800，缩放动画
- ✅ Logo圆角40px
- ✅ 统一配色方案
- ✅ 竖屏1080x1920

### 技术质量
- ✅ 绕过Cloudflare截图
- ✅ 音频与视频时长同步
- ✅ 场景切换流畅

---

## 📝 版本历史

### v1.0 (2026-02-06)
- ✅ 初始版本交付
- ✅ 5选3截图策略
- ✅ 截图缩放动画
- ✅ 开头结尾Logo圆角
- ✅ 完整产品文档

---

## 🔮 未来规划

### v1.1 计划
- [ ] 支持更多数据源 (Reddit, Twitter)
- [ ] AI自动文案生成
- [ ] 多语言支持 (英文版本)
- [ ] 自动上传到视频平台

### v2.0 计划
- [ ] 可视化配置界面
- [ ] 模板系统
- [ ] 批量视频生成
- [ ] 数据分析仪表盘

---

## 👥 团队

- **产品**: AiTrend Team
- **开发**: OpenClaw AI Assistant
- **设计**: AiTrend Design

---

## 📄 相关文档

- [产品经验总结](LESSONS_LEARNED.md)
- [截图方案调研](SCREENSHOT_RESEARCH.md)
- [动画实现报告](ANIMATION_FEASIBILITY_REPORT.md)

---

**版本状态**: ✅ 已交付  
**GitHub**: https://github.com/Lychee-AI-Team/AiTrend

---

*AiTrend v1.0 - 让AI热点触手可及* 🦞
