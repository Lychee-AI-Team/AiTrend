# AiTrend Skill

## 概述

AiTrend 是一个模块化 AI 项目发现与内容发布系统。系统自动从 GitHub Trend 等平台发现新兴项目，使用大模型生成自然叙述内容，并发布到 Discord 等平台。

## 架构设计

### 模块化架构

```
AiTrend/
├── launcher.py              # 启动中枢
├── modules/
│   ├── sources/             # 信息源模块（可插拔）
│   │   ├── base.py
│   │   └── github_trend.py
│   ├── processors/          # 处理器模块（可插拔）
│   │   ├── base.py
│   │   ├── readme_processor.py
│   │   └── search_processor.py
│   └── output/              # 输出模块
│       └── narrative_composer.py
├── publishers/              # 发布模块（可插拔）⭐
│   ├── base.py              # 发布模块基类
│   ├── forum_publisher.py   # Discord论坛发布
│   └── text_publisher.py    # Discord文字频道发布
├── config.yaml              # 主配置文件
└── docs/
    └── SKILL.md             # 本文档
```

## 发布模块系统（重点）

### 模块说明

#### 1. ForumPublisher - Discord论坛发布模块

**功能**：发布内容到 Discord 论坛频道，创建新帖子

**适用场景**：
- 需要为每个项目创建独立讨论帖
- 希望内容有独立的评论区
- 论坛结构便于后期检索

**配置项**：
```yaml
publishers:
  forum:
    enabled: true
    webhook_url: "https://discord.com/api/webhooks/..."  # 论坛频道Webhook
    thread_name: "{name} – {source}"                      # 帖子标题模板
    username: "AiTrend"                                   # 发布者名称
    delay: 2                                              # 帖子间隔(秒)
    max_length: 1900                                      # 内容最大长度
```

**标题模板变量**：
- `{name}` - 项目名称
- `{source}` - 来源（如 GitHub）
- `{date}` - 日期

---

#### 2. TextPublisher - Discord文字频道发布模块

**功能**：发布内容到 Discord 文字频道，发送普通消息

**适用场景**：
- 简单的消息流推送
- 不需要独立讨论区
- 快速浏览多个项目

**配置项**：
```yaml
publishers:
  text:
    enabled: false                                        # 设为true启用
    webhook_url: "https://discord.com/api/webhooks/..."  # 文字频道Webhook
    use_embed: false                                      # 是否使用Embed格式
    username: "AiTrend"
    delay: 1
    avatar_url: ""                                        # 自定义头像URL
```

**格式说明**：
- `use_embed: false` - 纯文本格式，带标题和链接
- `use_embed: true` - Embed卡片格式，更美观

---

### 模块切换方法

#### 方法1：通过配置文件切换（推荐）

编辑 `config.yaml`：

```yaml
# 切换到论坛发布
publishers:
  forum:
    enabled: true      # 启用论坛发布
  text:
    enabled: false     # 禁用文字频道

# 切换到文字频道发布
publishers:
  forum:
    enabled: false     # 禁用论坛
  text:
    enabled: true      # 启用文字频道
```

#### 方法2：通过代码动态切换

```python
from publishers import create_publisher

# 创建论坛发布模块
forum_publisher = create_publisher('forum', {
    'webhook_url': '...',
    'thread_name': '{name} – {source}'
})

# 创建文字频道发布模块
text_publisher = create_publisher('text', {
    'webhook_url': '...',
    'use_embed': False
})

# 根据条件切换
if use_forum:
    publisher = forum_publisher
else:
    publisher = text_publisher

# 使用选中的发布模块
publisher.publish(content)
```

---

### 配置方法

#### 步骤1：获取 Discord Webhook URL

**论坛频道**：
1. 在 Discord 中创建论坛频道
2. 频道设置 → 集成 → Webhook → 新建 Webhook
3. 复制 Webhook URL

**文字频道**：
1. 在 Discord 中创建文字频道
2. 频道设置 → 集成 → Webhook → 新建 Webhook
3. 复制 Webhook URL

#### 步骤2：配置环境变量

创建 `.env` 文件：
```bash
# Discord配置
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# 大模型API（可选，默认使用OpenClaw）
# OPENAI_API_KEY=sk-...
# KIMI_API_KEY=...

# 其他数据源API
TAVILY_API_KEY=tvly-...
```

#### 步骤3：编辑 config.yaml

```yaml
# 信息源配置
sources:
  github_trend:
    enabled: true
    languages: ['python', 'javascript', 'go']
    max_candidates: 10
    growth_threshold: 0.5

# 发布模块配置
publishers:
  # 论坛发布模块
  forum:
    enabled: true
    webhook_url: ""  # 从环境变量读取或在此填写
    thread_name: "{name} – {source}"
    username: "AiTrend"
    delay: 2
    max_length: 1900
  
  # 文字频道发布模块
  text:
    enabled: false
    webhook_url: ""
    use_embed: false
    username: "AiTrend"
    delay: 1
```

---

## 运行与日志

### 运行方式

```bash
# 完整流程
python3 launcher.py

# 仅测试发布模块
python3 test_publisher.py

# 手动流程
python3 run_flow.py
```

### 日志系统

日志文件位置：`logs/aitrend_YYYY-MM-DD.log`

日志内容：
- 模块加载状态
- 项目发现数量
- 内容生成状态
- 发布成功/失败记录
- 错误详情

示例日志：
```
[2026-02-02 21:30:15] INFO: 启动中枢初始化
[2026-02-02 21:30:16] INFO: 加载发布模块: ForumPublisher
[2026-02-02 21:30:20] INFO: 发现 10 个候选项目
[2026-02-02 21:30:25] INFO: 生成内容: nanobot (387字符)
[2026-02-02 21:30:30] SUCCESS: 发布成功: nanobot – GitHub
```

---

## 格式一致性

### 内容格式

无论是论坛帖子还是文字频道消息，内容格式保持一致：

```
项目名称

自然叙述内容（口语化、无列表、无套话）

项目链接: https://github.com/...
```

### 差异点

| 特性 | ForumPublisher | TextPublisher |
|------|----------------|---------------|
| 载体 | 论坛帖子 | 普通消息 |
| 标题 | thread_name 参数 | 内容第一行 |
| 评论 | 独立评论区 | 无独立评论区 |
| 检索 | 论坛内可搜索 | 频道历史记录 |

---

## 故障排查

### 发布失败

**检查清单**：
1. Webhook URL 是否正确
2. 频道是否有发送权限
3. 内容是否超过长度限制
4. 是否触发速率限制

**日志查看**：
```bash
tail -f logs/aitrend_$(date +%Y-%m-%d).log
```

### 模块切换无效

**检查清单**：
1. config.yaml 中 enabled 字段是否正确
2. 是否重启了程序
3. 配置格式是否正确（缩进、冒号空格）

---

## 扩展开发

### 添加新的发布模块

1. 继承 `BasePublisher`：
```python
from publishers.base import BasePublisher

class TelegramPublisher(BasePublisher):
    def publish(self, content):
        # 实现发布逻辑
        pass
```

2. 注册到 `publishers/__init__.py`：
```python
PUBLISHER_MAP = {
    'forum': ForumPublisher,
    'text': TextPublisher,
    'telegram': TelegramPublisher,  # 新增
}
```

3. 在 `config.yaml` 中添加配置项

---

## 版本信息

- **当前版本**: 2.0
- **更新日期**: 2026-02-02
- **主要更新**: 模块化发布系统、ForumPublisher完善、日志系统
