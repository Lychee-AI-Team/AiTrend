# 故障排查指南

本文档汇总了开发和使用过程中可能遇到的问题及解决方案。

---

## 信息源模块问题

### GitHub Trend

#### 问题：发现 0 个项目

**可能原因**:
1. 搜索条件太严格
2. API 速率限制
3. 网络问题

**解决步骤**:
```python
# 1. 检查配置
config = {
    'languages': ['python'],  # 减少语言
    'growth_threshold': 0.3,  # 降低阈值
    'max_candidates': 10
}

# 2. 测试 API
import requests
response = requests.get("https://api.github.com/search/repositories?q=language:python&sort=stars")
print(response.status_code)
```

#### 问题：403 Forbidden

**原因**: 速率限制

**解决**:
```python
# 添加延迟
import time
time.sleep(1)  # 每次请求间隔1秒

# 或使用 Token
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
```

---

### Product Hunt

#### 问题：401 Unauthorized

**原因**: Token 无效或过期

**解决**:
1. 检查 `.env` 文件中的 Token
2. 访问 https://www.producthunt.com/v2/oauth/applications
3. 重新生成 Token
4. 更新 `.env`

#### 问题：GraphQL 错误

**症状**: 返回错误信息但 HTTP 200

**解决**:
```python
# 检查响应
data = response.json()
if 'errors' in data:
    print(data['errors'])
    # 常见错误：字段不存在、查询语法错误
```

---

### HackerNews

#### 问题：获取帖子很慢

**原因**: 需要逐个获取 item 详情

**解决**:
```python
# 限制处理数量
story_ids = story_ids[:30]  # 只处理前30个

# 或使用并发
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(fetch_item, story_ids)
```

#### 问题：返回数据格式不对

**原因**: Firebase API 返回 None 表示 item 不存在

**解决**:
```python
item = response.json()
if not item or item.get('type') != 'story':
    continue  # 跳过无效数据
```

---

### Reddit

#### 问题：403 Forbidden (官方 API)

**原因**: Reddit 阻止了未认证的请求

**解决**: 使用 Pushshift API
```python
# 不要这样做
url = "https://www.reddit.com/r/MachineLearning/hot.json"  # 会403

# 改为这样
url = "https://api.pullpush.io/reddit/submission/search"  # 正常
```

#### 问题：Pushshift 返回空数据

**原因**: 查询条件太严格或时间范围不对

**解决**:
```python
# 放宽条件
params = {
    'subreddit': 'MachineLearning',
    'sort': 'desc',
    'sort_type': 'score',
    'score': '>30',  # 降低分数要求
    'size': 25,
    'after': days_ago - 86400  # 延长1天
}
```

---

## 内容生成问题

### 问题：内容生成失败

**症状**: LLM 调用返回空

**排查步骤**:
```python
# 1. 检查提示词长度
if len(prompt) > 4000:
    print("提示词过长，截断内容")

# 2. 检查特殊字符
prompt = prompt.replace('"', '\"')

# 3. 检查网络
import subprocess
result = subprocess.run(['curl', 'https://api.openai.com'], capture_output=True)
print(result.returncode)
```

### 问题：内容重复

**症状**: 多条内容开头相似

**解决**:
```python
# 多样化开头
styles = ["直接切入", "场景描述", "功能介绍"]
style = styles[index % len(styles)]

# 提示词中添加
prompt += f"\n开头风格: {style}"
```

### 问题：包含结构化内容

**症状**: 出现列表、序号

**解决**:
```python
# 后处理
text = re.sub(r'^[\s]*[-*•][\s]+', '', text, flags=re.MULTILINE)
text = re.sub(r'第一|第二|首先|其次', '', text)
```

---

## 发布模块问题

### 问题：发布失败 400

**原因**: 内容格式错误

**排查**:
```python
# 检查 payload
payload = {
    'content': content[:1900],  # 确保不超过限制
    'username': 'AiTrend'  # 必填
}

# 检查 JSON 格式
import json
json.dumps(payload)  # 确保无异常
```

### 问题：429 Rate Limited

**原因**: 发送太快

**解决**:
```python
# 添加延迟
import time
time.sleep(2)  # 每条消息间隔2秒
```

### 问题：Webhook 无效

**排查**:
```bash
# 测试 Webhook
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"test"}' \
  YOUR_WEBHOOK_URL
```

---

## 配置问题

### 问题：环境变量未加载

**排查**:
```python
import os
print(os.getenv('DISCORD_WEBHOOK_URL'))  # 检查是否为 None

# 确保加载.env
from pathlib import Path
env_path = Path('.env')
if env_path.exists():
    print("找到 .env 文件")
```

### 问题：配置文件格式错误

**排查**:
```python
import yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"YAML 格式错误: {e}")
```

---

## 性能问题

### 问题：运行速度慢

**优化建议**:

1. **并行获取信息源**
```python
from concurrent.futures import ThreadPoolExecutor

def fetch_source(source):
    return source.discover()

with ThreadPoolExecutor() as executor:
    results = executor.map(fetch_source, sources)
```

2. **缓存 API 结果**
```python
import json
from datetime import datetime, timedelta

cache_file = '/tmp/aitrend_cache.json'
cache_ttl = timedelta(hours=1)

# 检查缓存
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cache = json.load(f)
    if datetime.now() - cache['timestamp'] < cache_ttl:
        return cache['data']
```

3. **减少 LLM 调用**
```python
# 批量处理
contents = []
for candidate in candidates[:3]:  # 限制数量
    content = generate_content(candidate)
    contents.append(content)
```

---

## 日志问题

### 问题：日志不输出

**排查**:
```python
from modules.logger import get_logger

logger = get_logger()
logger.info("测试日志")  # 检查是否有输出

# 检查日志目录
import os
os.makedirs('logs', exist_ok=True)
```

### 问题：日志文件过大

**解决**:
```python
# 日志轮转
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/aitrend.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

## 网络问题

### 问题：连接超时

**解决**:
```python
# 增加超时时间
response = requests.get(url, timeout=30)

# 重试机制
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

### 问题：SSL 错误

**解决**:
```bash
# 更新证书
pip install --upgrade certifi

# 或在代码中
import certifi
response = requests.get(url, verify=certifi.where())
```

---

## 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 单步调试

```python
# 在关键点添加断点
import pdb; pdb.set_trace()

# 或使用 ipdb
import ipdb; ipdb.set_trace()
```

### 测试单个模块

```bash
# 测试单个信息源
python3 -c "
from modules.sources.github_trend import GithubTrend
source = GithubTrend({'languages': ['python']})
candidates = source.discover()
print(f'发现 {len(candidates)} 个项目')
for c in candidates[:3]:
    print(f'  - {c[\"name\"]}')
"
```

---

## 常见错误代码

| 错误 | 含义 | 解决 |
|------|------|------|
| 400 | 请求格式错误 | 检查 payload |
| 401 | 认证失败 | 检查 Token |
| 403 | 禁止访问 | 检查权限 |
| 404 | 资源不存在 | 检查 URL |
| 429 | 速率限制 | 添加延迟 |
| 500 | 服务器错误 | 稍后重试 |
| 503 | 服务不可用 | 稍后重试 |

---

## 联系支持

如以上方法无法解决问题：

1. 查看日志文件 `logs/aitrend_*.log`
2. 记录错误信息和复现步骤
3. 提交 Issue 到项目仓库

---

**文档版本**: 1.0  
**更新日期**: 2026-02-03
