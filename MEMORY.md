# MEMORY.md - 长期记忆

## GitHub 配置

### 已配置项
- ✅ GitHub Personal Access Token 已配置（2026-01-31）
- ✅ Token 可直接提交到仓库
- ✅ 组织: Lychee-AI-Team (https://github.com/Lychee-AI-Team/)
- ✅ 主分支命名: main

## 服务器信息

### Webhook 服务器
- **公网 IP**: 115.190.215.54
- **端口**: 3000
- **Webhook URL**: http://115.190.215.54:3000
- **飞书群聊 ID**: oc_9a3c218325fd2cfa42f2a8f6fe03ac02
- **Systemd 服务**: clawdbot-webhook.service
- **工作目录**: /root/clawd/webhook-server

### Brave Search API 限制
- **⚠️ 重要**: Brave Search API 在本地服务器（115.190.215.54）上无法运行（网络限制/超时）
- **✅ 可用环境**: GitHub Actions 可以正常使用 Brave Search API
- **API Key**: 有效，已配置到环境变量和 `.brave-api-key` 文件
- **解决方案**: 在本地运行时使用 mock 数据模式，在 GitHub Actions 中使用真实 API

### 支持的端点
- `/` - AI Hotspot 收集
- `/webhook/ai-news` - AI News 收集
- `/webhook/github` - GitHub 事件
- `/health` - 健康检查

## 项目开发

### 当前项目：AiTrend
- **仓库**: Lychee-AI-Team/AiTrend
- **本地路径**: /root/AiTrend
- **主分支**: main
- **开发规则**:
  - 所有开发任务都在此仓库中进行
  - 使用 GitHub Actions 进行自动化
  - AI 热点收集脚本：`scripts/ai-hotspot-collector.sh`
  - AI News 收集脚本：`scripts/collect-news.js`
  - 收集来源：GitHub Trending、中国大模型、Zread、AI Hot Today

### GitHub Actions
- **ai-hotspot.yml**: 每天 05:00, 13:00, 21:00 UTC 运行
- **ai-news.yml**: 每天 01:00 UTC 运行

---
*此文件记录需要长期保存的重要信息*
