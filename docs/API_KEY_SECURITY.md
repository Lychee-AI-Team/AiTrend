# API Key 安全配置指南

## 🔐 安全状态报告

### Gemini API Key 安全检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 存储位置 | ✅ 安全 | `.env` 文件，权限 600 |
| Git忽略 | ✅ 已配置 | `.gitignore` 已排除 `.env` |
| 代码硬编码 | ✅ 无泄露 | 代码中使用 `os.getenv()` 读取 |
| 备份文件 | ✅ 已保护 | `.env.keys` 同样被忽略 |
| 泄露风险 | 🟢 低 | 仅本地存储，未提交到Git |

**Gemini API Key 状态**: ✅ **安全，无泄露风险**

### Moltbook API Key 安全检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 存储位置 | ✅ 安全 | `~/.openclaw/workspace/moltbook_credentials.env` |
| 代码硬编码 | ✅ 无泄露 | 代码中使用 `os.getenv('MOLTBOOK_API_KEY')` |
| 注册信息 | ✅ 完整 | 已注册为 pipixia20250202 |
| 验证状态 | ✅ 已验证 | 状态: verified |

**Moltbook API Key 状态**: ✅ **安全，无泄露风险**

---

## 📋 新用户安装配置指南

### 1. 克隆项目

```bash
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend
```

### 2. 配置环境变量

复制示例文件并编辑：

```bash
cp .env.example .env
nano .env
```

### 3. 必需配置的 API Key

#### Gemini API Key (用于LLM内容生成)

1. 访问 https://ai.google.dev/
2. 创建 API Key
3. 添加到 `.env`：
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

#### Moltbook API Key (用于采集AI社区内容)

**每个AI代理需要单独注册获取API Key**

1. 让AI代理访问 https://www.moltbook.com
2. 执行注册命令：
```bash
curl -X POST https://www.moltbook.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "YourAgentName", "description": "AI assistant"}'
```

3. 保存返回的 API Key 到 `.env`：
```bash
MOLTBOOK_API_KEY=moltbook_sk_xxx
```

4. 访问 claim_url 完成验证（需要人类验证推文）

#### 其他可选 API Key

```bash
# Product Hunt (可选)
PRODUCTHUNT_TOKEN=your_token_here

# Tavily (可选)
TAVILY_API_KEY=your_key_here

# Discord Webhook (必需)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx
```

### 4. 安全保护措施

`.env` 文件已配置以下保护：
- ✅ `.gitignore` 排除，不会意外提交
- ✅ 文件权限 600（仅所有者可读写）
- ✅ 预提交钩子检查，防止密钥泄露

### 5. 验证配置

```bash
# 验证 Gemini
python3 -c "import os; print('Gemini:', '✅' if os.getenv('GEMINI_API_KEY') else '❌')"

# 验证 Moltbook
python3 -c "import os; print('Moltbook:', '✅' if os.getenv('MOLTBOOK_API_KEY') else '❌')"
```

---

## ⚠️ 安全警告

1. **不要将 `.env` 文件提交到 Git**
   - 已配置 `.gitignore` 自动排除
   - 如意外提交，立即撤销并更换API Key

2. **API Key 权限最小化**
   - Gemini Key：仅用于文本生成
   - Moltbook Key：仅用于读取公开帖子

3. **定期轮换**
   - 建议每3个月更换一次API Key
   - 如发现泄露迹象，立即更换

4. **本地存储**
   - API Key 仅存储在本地 `.env` 文件
   - 不会上传到任何服务器

---

## 🔍 安全审计日志

**审计时间**: 2026-02-04
**审计人**: 皮皮虾

### 检查结果

| 项目 | 状态 |
|------|------|
| Gemini API Key 硬编码检查 | ✅ 无硬编码 |
| Moltbook API Key 硬编码检查 | ✅ 无硬编码 |
| .env 文件 Git 忽略检查 | ✅ 已配置 |
| 文件权限检查 | ✅ 600 (仅所有者) |
| 备份文件保护 | ✅ .env.keys 被忽略 |
| 预提交钩子 | ✅ 密钥保护已启用 |

### 结论

**安全状态**: 🟢 **安全**

- 所有API Key均通过环境变量读取
- 无硬编码密钥存在于代码中
- .env 文件被 Git 忽略保护
- 文件权限正确设置

**建议**: 可以安全提交代码到GitHub
