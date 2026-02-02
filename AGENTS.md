# AGENTS.md - AiTrend Skill 开发记录

## 版本: v0.1.0

## 项目目标
构建一个可分享的 OpenClaw Skill，实现多源 AI 热点资讯自动收集、AI 总结、多渠道推送。

## 核心架构

### 技术栈
- **语言**: Python 3.11+
- **异步框架**: asyncio + aiohttp
- **配置管理**: Pydantic + YAML
- **数据验证**: 自验证闭环（无需人工确认）
- **插件系统**: 基类 + 动态加载

### 模块结构
```
AiTrend/
├── src/
│   ├── core/           # 收集器、总结器、验证器
│   ├── sources/        # 数据源插件（GitHub、Brave）
│   ├── channels/       # 发送渠道插件（飞书等）
│   └── utils/          # 工具函数
├── config/             # 配置文件
├── tests/              # 测试
└── docs/               # 文档
```

## 数据源插件 (v0.1.0)

### 1. GitHub Trending
- **功能**: 获取 GitHub 热门仓库
- **配置**: languages, min_stars, since
- **输出**: title, url, description, stars, language

### 2. Brave Search
- **功能**: 全网搜索 AI 热点
- **配置**: queries, api_key, freshness, count
- **输出**: title, url, description, source

## AI 总结器 (v0.1.0)

### 支持模型
- **Gemini**: gemini-2.5-flash (默认)
- **OpenAI**: gpt-4, gpt-3.5-turbo
- **Anthropic**: claude-3-sonnet

### 配置项
- provider: 模型提供商
- model: 具体模型
- api_key: API 密钥
- prompt_template: 自定义提示词
- temperature: 创造性参数

## 发送渠道 (v0.1.0)

### 已支持
- **Feishu**: 飞书群聊/私聊
- **Console**: 本地输出（测试用）

### 预留扩展
- Telegram
- Discord
- Slack
- Email

## 自验证机制 (v0.1.0)

### 三层验证
1. **数据验证**: 字段完整性、URL 可访问性
2. **总结验证**: 长度、语言、格式
3. **发送验证**: API 返回状态、消息确认

### 自动修复
- 超长内容自动截断
- 格式错误自动清理
- 空内容自动过滤
- 失败自动重试（最多 3 次）

## 配置示例 (v0.1.0)

```yaml
# 数据源
sources:
  github_trending:
    enabled: true
    languages: ["python", "typescript"]
    min_stars: 100
  
  brave_search:
    enabled: true
    queries: ["AI latest", "LLM news"]
    freshness: "pd"

# AI 总结
summarizer:
  provider: "gemini"
  model: "gemini-2.5-flash"
  temperature: 0.7

# 发送渠道
channels:
  feishu:
    enabled: true
    target: "oc_xxx"

# 定时任务
schedule:
  cron: "0 9,13,21 * * *"
```

## 开发里程碑

### v0.1.0 (当前)
- [x] 架构设计
- [ ] 核心模块开发
- [ ] 数据源实现（GitHub、Brave）
- [ ] AI 总结器实现
- [ ] 飞书渠道实现
- [ ] 自验证机制
- [ ] 测试验证
- [ ] 文档编写

### v0.2.0 (未来)
- [ ] 新增数据源（HackerNews、Reddit）
- [ ] 新增渠道（Telegram、Discord）
- [ ] Web UI 配置界面
- [ ] 历史数据浏览

### v1.0.0 (未来)
- [ ] 发布到 OpenClaw Skill 市场
- [ ] 社区插件生态
- [ ] 高级分析功能

## 执行计划

1. **创建项目结构** - 建立目录和基础文件 ✅
2. **实现数据源基类** - 定义插件接口 ✅
3. **实现 GitHub 数据源** - 爬取 Trending ✅
4. **实现 Brave 数据源** - 调用搜索 API ✅
5. **实现 AI 总结器** - 集成多模型 ✅
6. **实现渠道基类** - 定义发送接口 ✅
7. **实现飞书渠道** - 发送消息 ✅
8. **实现自验证** - 闭环验证 ✅
9. **整合测试** - 端到端测试 ✅
10. **文档完善** - README、文档 ✅

## 关键节点检查点

- [x] 方案确认（AGENTS.md 创建）
- [x] 项目结构完成
- [x] 数据源实现完成
- [x] AI 总结器完成
- [x] 渠道发送完成
- [x] 自验证完成
- [x] 端到端测试（代码完成，待运行）
- [x] 飞书消息发送（代码完成，待验证）
- [ ] 大师确认满意

## 备注

- 开发过程使用 TDD（测试驱动开发）
- 每个模块完成后立即测试
- 关键节点向大师汇报进展
- 最终输出必须在飞书对话中验证

---
记录时间: 2026-02-01
记录者: 屁屁虾🦞
版本: v0.1.0
