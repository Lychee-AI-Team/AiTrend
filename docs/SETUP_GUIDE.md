# AiTrend 安装配置指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Keys

#### 必需配置

**Gemini API Key** (用于AI内容生成):
```bash
# 1. 访问 https://ai.google.dev/ 创建API Key
# 2. 添加到 .env 文件
echo "GEMINI_API_KEY=your_key_here" >> .env
```

**Moltbook API Key** (用于AI社区内容采集):
```bash
# ⚠️ 每个AI代理需要单独注册！
# 1. 让AI代理执行注册:
curl -X POST https://www.moltbook.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "YourAgentName", "description": "AI assistant for trend discovery"}'

# 2. 保存返回的 api_key 到 .env:
echo "MOLTBOOK_API_KEY=moltbook_sk_xxx" >> .env

# 3. 人类访问 claim_url 完成验证（需要发推文）
```

**Discord Webhook** (用于发布):
```bash
# 1. Discord服务器设置 -> 集成 -> Webhook
# 2. 复制Webhook URL
echo "DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx" >> .env
```

#### 可选配置

```bash
# Product Hunt (可选)
echo "PRODUCTHUNT_TOKEN=xxx" >> .env

# Tavily (可选)
echo "TAVILY_API_KEY=xxx" >> .env
```

### 3. 运行测试

```bash
# 测试模式
python3 -m src.hourly --test

# 完整运行
python3 -m src.hourly
```

---

## 🔐 安全说明

- `.env` 文件已被 `.gitignore` 保护，不会提交到Git
- API Key 仅本地存储，不上传服务器
- 如意外泄露，请立即更换API Key

---

## 📖 详细文档

- [API Key 安全指南](API_KEY_SECURITY.md)
- [开发指南](DEVELOPMENT_GUIDE.md)
- [故障排查](TROUBLESHOOTING.md)
