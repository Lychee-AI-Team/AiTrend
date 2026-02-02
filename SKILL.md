# AiTrend Skill

纯数据收集器 - 从多源收集 AI 热点，输出结构化数据

## 安装

```bash
cd ~/.openclaw/workspace
git clone https://github.com/Lychee-AI-Team/AiTrend.git
```

## 使用

### 基本用法

运行 AiTrend 收集数据，然后用大模型生成内容：

> "运行 AiTrend 收集数据，然后将结果用口语化风格总结成周报，发送给我"

### 完整示例

**步骤 1：收集数据**
```bash
cd ~/.openclaw/workspace/AiTrend
python3 -m src
```

输出示例：
```json
{
  "count": 15,
  "articles": [
    {
      "title": "OpenClaw - AI Agent 应用商店",
      "url": "https://x.com/...",
      "summary": "700+ 插件一键安装...",
      "source": "twitter"
    }
  ]
}
```

**步骤 2：生成内容**

使用 OpenClaw 大模型将数据转换为口语化周报：

> "基于以下数据，生成一份 AI 热点周报：
> 1. 精选 8-12 个产品
> 2. 每个产品用口语化描述：谁发现的、亮点、痛点
> 3. 格式：1. **产品名** [描述] 👉 链接
> 4. 添加趋势洞察段落
> 5. 语言：简体中文
>
> [粘贴 AiTrend 输出]"

**步骤 3：发送**

OpenClaw 自动发送到用户配置的 Channel

## 数据源

- HackerNews - 开发者社区热门
- Reddit - AI 社区讨论  
- GitHub - AI 开源项目趋势
- Twitter - 实时内容（需配置）
- Product Hunt - 新产品发布（需配置）
- Brave Search - 全网搜索（需配置）

## 配置（可选）

如需启用 Twitter/PH/Brave，在 `.env` 中配置 API Keys

## 说明

- AiTrend 只负责收集数据
- 内容总结由 OpenClaw 大模型完成
- 消息发送由 OpenClaw 路由到用户 Channel
