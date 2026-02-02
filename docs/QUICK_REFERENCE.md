# AiTrend 开发速查表

## 快速开始

### 新增信息源模块（5分钟）

```bash
# 1. 复制模板
cp modules/sources/github_trend.py modules/sources/new_source.py

# 2. 修改类名和API
# 3. 注册模块
echo "from .new_source import NewSource" >> modules/sources/__init__.py

# 4. 添加配置
cat >> config.yaml << EOF
  new_source:
    enabled: true
    api_key: ""
    max_candidates: 10
EOF

# 5. 测试
python3 -c "from modules.sources.new_source import NewSource; s = NewSource({'api_key': 'test'}); print(s.is_enabled())"
```

---

## 核心接口

### 信息源基类

```python
from modules.sources.base import BaseSource

class NewSource(BaseSource):
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get('api_key')
    
    def is_enabled(self):
        return bool(self.api_key)
    
    def discover(self):
        # 返回 List[Dict]
        return [{
            'name': '...',
            'url': '...',
            'source_name': 'new_source'
        }]
```

### 发布基类

```python
from publishers.base import BasePublisher

class NewPublisher(BasePublisher):
    def __init__(self, config):
        super().__init__(config)
        self.webhook = config.get('webhook_url')
    
    def validate_config(self):
        return bool(self.webhook)
    
    def publish(self, content):
        # content: {'name', 'content', 'url', 'source'}
        pass
    
    def publish_batch(self, contents):
        success = 0
        for c in contents:
            if self.publish(c):
                success += 1
        return success
```

---

## 提示词模板

### 标准产品描述

```python
def build_prompt(product, index):
    styles = [
        "直接定义式",
        "功能切入式",
        "场景描述式"
    ]
    
    return f"""
写产品介绍：

产品: {product['name']}
描述: {product['description'][:400]}

禁止：
- "最近发现"等套话开头
- 第一第二等序号
- 列表符号（- * •）
- 重复用词
- 空话（针对痛点、功能设计）

必须：
- 直接描述产品是什么、能做什么
- 连续段落，300字内
- 包含链接: {product['url']}

开头风格: {styles[index % len(styles)]}
"""
```

---

## 日志使用

```python
from modules.logger import get_logger

logger = get_logger()

logger.info("一般信息")
logger.success("成功操作")
logger.warning("警告")
logger.error("错误")
logger.section("分段标题")  # 自动打印 === 分隔线
```

---

## 配置项

### 信息源配置

```yaml
sources:
  source_name:
    enabled: true           # 布尔
    api_key: ""            # 字符串，优先从环境变量读取
    max_candidates: 10     # 整数
    timeout: 15            # 秒，整数
```

### 发布配置

```yaml
publishers:
  forum:
    enabled: true
    webhook_url: ""         # Discord Webhook URL
    thread_name: "{name} – {source}"
    username: "AiTrend"
    delay: 2               # 秒
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| ModuleNotFoundError | 未注册 | 添加到 `__init__.py` |
| 0个项目 | API错误 | 检查Token，简化参数 |
| HTTP 400 | 格式错误 | 检查payload，截断内容 |
| 重复开头 | 提示词问题 | 添加多样化开头约束 |
| 速率限制 | 请求太快 | 添加 delay 参数 |

---

## 文件清单

### 新增信息源需要修改

```
modules/sources/
├── __init__.py          # + 导入新模块
└── new_source.py        # 新文件

config.yaml              # + 配置项
docs/DEVELOPMENT_GUIDE.md # 更新文档
```

### 新增发布模块需要修改

```
publishers/
├── __init__.py          # + 注册新模块
├── base.py              # 已有
└── new_publisher.py     # 新文件

config.yaml              # + 配置项
```

---

## 测试命令

```bash
# 测试单个模块
python3 -c "from modules.sources.new import New; s=New({}); s.discover()"

# 测试发布
python3 test_publisher.py

# 运行完整流程
python3 launcher_v2.py

# 查看日志
tail -f logs/aitrend_$(date +%Y-%m-%d).log
```

---

## Git 提交规范

```bash
# 新增模块
git commit -m "feat: add {source_name} source module

- Add modules/sources/{source_name}.py
- Register in __init__.py
- Update config.yaml
- Tested: X projects fetched"

# 修复问题
git commit -m "fix: {description}

- Fix {specific_issue}
- Update {related_files}"

# 文档更新
git commit -m "docs: update development guide

- Add {section}
- Update {content}"
```

---

## 环境变量

```bash
# 必须
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# 信息源（根据启用的模块）
export PRODUCTHUNT_TOKEN="..."
export GITHUB_TOKEN="..."  # 可选，提高速率限制

# 大模型（可选，默认使用OpenClaw）
export OPENAI_API_KEY="..."
export KIMI_API_KEY="..."
```

---

**保存此页，开发时快速查阅**
