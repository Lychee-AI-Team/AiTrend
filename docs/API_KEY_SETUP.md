# API Key 设置指南

本文档介绍如何获取各信息源平台的 API Key。

---

## GitHub Token（可选但推荐）

### 用途
- 提高 API 速率限制（5000次/小时 vs 60次/小时）
- 访问私有仓库信息

### 获取步骤

1. 登录 GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单最下方 → Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token (classic)
6. 填写信息：
   - Note: `AiTrend`
   - Expiration: 无过期或自定义
   - Scopes: 勾选 `repo` 和 `read:user`
7. Generate token
8. **立即复制**（只显示一次）

### 配置
```bash
# .env 文件
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

---

## Product Hunt Token（必需）

### 用途
- 访问 Product Hunt GraphQL API
- 获取产品投票、评论数据

### 获取步骤

1. 登录 Product Hunt
2. 访问: https://www.producthunt.com/v2/oauth/applications
3. 点击 Create Application
4. 填写信息：
   - Name: `AiTrend`
   - Redirect URL: `http://localhost:3000/callback`
   - Description: `AI project discovery tool`
5. Create Application
6. 进入应用详情页
7. 找到 **Token** 部分
8. 点击 Generate Token
9. 复制 Token

### 配置
```bash
# .env 文件
PRODUCTHUNT_TOKEN=your_token_here
```

---

## HackerNews

### 说明
HackerNews 使用 Firebase API，**无需认证**。

直接访问：
```
https://hacker-news.firebaseio.com/v0/
```

无需配置。

---

## Reddit

### 说明
当前使用 **Pushshift API**，**无需认证**。

如需使用官方 Reddit API，需要 OAuth 认证。

### Pushshift（当前使用）
无需配置，直接可用：
```
https://api.pullpush.io/reddit/submission/search
```

### Reddit API（可选）

如需要实时数据，可申请 Reddit API：

1. 登录 Reddit
2. 访问: https://www.reddit.com/prefs/apps
3. 点击 create another app
4. 填写信息：
   - Name: `AiTrend`
   - Type: `script`
   - Description: `AI project discovery`
   - About URL: `http://localhost`
   - Redirect URI: `http://localhost:8080/callback`
5. create app
6. 获取：
   - Client ID（在应用名称下方）
   - Secret（显示为 secret）

### 配置（可选）
```bash
# .env 文件（仅使用官方API时需要）
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
```

---

## 推荐新增平台

### arXiv（即将开发）

**说明**: 无需认证，直接访问 API。

```
http://export.arxiv.org/api/query
```

### Twitter/X（可选）

**说明**: 需要 Twitter Developer Account。

### 获取步骤

1. 访问: https://developer.twitter.com/
2. 申请 Developer Account（需审核）
3. 创建 Project
4. 创建 App
5. 获取 API Key 和 Secret
6. 生成 Bearer Token

### 配置
```bash
# .env 文件
TWITTER_BEARER_TOKEN=your_bearer_token
```

---

## 配置检查清单

创建 `.env` 文件后，检查以下配置：

```bash
# 必需
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# 可选但推荐
GITHUB_TOKEN=ghp_...
PRODUCTHUNT_TOKEN=...
TAVILY_API_KEY=tvly-...

# 大模型（可选，默认使用 OpenClaw）
# OPENAI_API_KEY=sk-...
# KIMI_API_KEY=...
```

---

## 验证配置

运行测试脚本验证配置：

```bash
# 测试 GitHub
python3 -c "from modules.sources.github_trend import GithubTrend; s=GithubTrend({'languages':['python']}); print('GitHub:', s.discover()[:1])"

# 测试 Product Hunt
python3 -c "from modules.sources.producthunt import Producthunt; s=Producthunt({'categories':['AI']}); print('PH:', s.is_enabled())"

# 测试 HackerNews
python3 -c "from modules.sources.hackernews import Hackernews; s=Hackernews({}); print('HN:', s.discover()[:1])"

# 测试 Reddit
python3 -c "from modules.sources.reddit import Reddit; s=Reddit({'subreddits':['MachineLearning']}); print('Reddit:', s.discover()[:1])"
```

---

## 故障排查

### GitHub Token 无效

**症状**: 403 Forbidden
**解决**: 
1. 检查 Token 是否过期
2. 重新生成 Token
3. 确认 Scopes 包含 `repo`

### Product Hunt Token 无效

**症状**: 401 Unauthorized
**解决**:
1. 检查 Token 是否正确复制
2. 重新生成 Token
3. 确认 Application 状态正常

### 速率限制

**症状**: 429 Too Many Requests
**解决**:
1. 添加 delay 参数
2. 使用缓存
3. 申请更高限额

---

## 安全提示

1. **不要将 .env 文件提交到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **定期轮换 Token**
   - GitHub: 每 90 天
   - Product Hunt: 每 180 天

3. **限制 Token 权限**
   - 只授予最小必需权限
   - 定期审查权限

---

**文档版本**: 1.0  
**更新日期**: 2026-02-03
