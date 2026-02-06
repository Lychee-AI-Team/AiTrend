# AiTrend 开发规范与经验总结

## 一、模块化设计原则（第一宪法）

### 1.1 核心原则

**可插拔性**
- 每个模块必须独立运行，不依赖其他模块
- 通过配置文件启用/禁用，无需修改代码
- 统一接口，可随时替换实现

**单一职责**
- 信息源模块：只负责发现和提取原始数据
- 内容整理模块：只负责处理和转换数据
- 发布模块：只负责最终输出

**配置驱动**
- 所有可变参数必须通过配置文件管理
- 支持环境变量覆盖配置
- 配置变更无需重启（尽可能）

### 1.2 模块接口规范

```python
# 信息源模块接口
class BaseSource(ABC):
    @abstractmethod
    def discover(self) -> List[Dict]: ...
    
    def is_enabled(self) -> bool: ...

# 内容整理模块接口  
class BaseProcessor(ABC):
    @abstractmethod
    def process(self, candidate: Dict) -> str: ...
    
    def can_process(self, candidate: Dict) -> bool: ...

# 发布模块接口
class BasePublisher(ABC):
    @abstractmethod
    def publish(self, content: Dict) -> bool: ...
    
    @abstractmethod
    def publish_batch(self, contents: List[Dict]) -> int: ...
    
    def validate_config(self) -> bool: ...
```

---

## 二、信息源模块开发规范

### 2.1 文件结构

```
modules/sources/
├── base.py              # 基类（已有，不要修改）
├── github_trend.py      # 示例实现
└── {source_name}.py     # 新模块
```

### 2.2 必须实现的方法

```python
class NewSource(BaseSource):
    def __init__(self, config: Dict):
        super().__init__(config)
        # 提取配置项
        self.api_key = config.get('api_key') or os.getenv('ENV_KEY')
        # 初始化 HTTP 会话
        self.session = requests.Session()
        
    def is_enabled(self) -> bool:
        """检查模块是否可用（配置完整）"""
        return bool(self.api_key)
    
    def discover(self) -> List[Dict]:
        """
        发现候选项目
        
        返回格式：
        {
            'name': '项目名称',
            'url': '项目链接',
            'description': '描述',
            'source_type': 'source_name',
            'source_name': 'Source Name',
            # 其他元数据...
        }
        """
        pass
```

### 2.3 开发步骤

1. **继承基类**
   ```python
   from modules.sources.base import BaseSource
   ```

2. **提取配置**
   - 优先从 config 读取
   - 其次从环境变量读取
   - 提供默认值

3. **实现 discover()**
   - 调用 API 或抓取网页
   - 解析响应数据
   - 标准化字段名
   - 返回统一格式

4. **添加日志**
   ```python
   from modules.logger import get_logger
   logger = get_logger()
   logger.info("发现 X 个项目")
   ```

5. **注册模块**
   ```python
   # modules/sources/__init__.py
   from .new_source import NewSource
   ```

6. **添加配置**
   ```yaml
   # config.yaml
   sources:
     new_source:
       enabled: true
       api_key: ""
       max_candidates: 10
   ```

### 2.4 经验总结

**GitHub 模块经验：**
- 使用 GitHub API 而非网页抓取（稳定）
- 增长率计算：(stars / days_since_created)
- 多语言并行请求提高效率
- 备用 README 地址（main/master）

**Product Hunt 模块经验：**
- GraphQL API 比 REST 更灵活
- 按 topic 过滤比全量获取高效
- 注意 API 权限和速率限制
- 产品描述可能为空，需要处理

---

## 三、内容整理规范

### 3.1 提示词设计原则

**禁止项（硬性约束）：**
```
❌ 禁止套话开头："最近发现"、"今天看到"、"找到一个"
❌ 禁止序号：第一第二、首先其次
❌ 禁止列表符号：- * •
❌ 禁止重复用词和句式（重复性惩罚）
❌ 禁止空话：针对痛点、功能设计、架构清晰、旨在解决
```

**必须项：**
```
✅ 直接描述产品是什么、能做什么
✅ 连续段落，无结构化痕迹
✅ 控制在 300-400 字
✅ 最后必须包含链接
```

### 3.2 提示词模板

```python
def build_prompt(product_info: Dict, index: int) -> str:
    """
    构建LLM提示词
    
    Args:
        product_info: 产品信息
        index: 索引，用于多样化开头
    """
    
    # 多样化开头策略
    opening_styles = [
        "直接定义式",
        "功能切入式", 
        "场景描述式",
        "对比传统式",
        "独特卖点式"
    ]
    style = opening_styles[index % len(opening_styles)]
    
    context = f"""
产品名: {product_info['name']}
Slogan: {product_info['tagline']}
介绍: {product_info['description'][:400]}
"""
    
    return f"""写一段产品介绍：

{context}

核心要求（严格遵守）：
1. ❌ 禁止开头用"最近发现"、"今天看到"、"找到一个"等套话
2. ❌ 禁止第一第二、首先其次等序号
3. ❌ 禁止用列表符号（- * •）
4. ❌ 禁止重复用词和句式
5. ❌ 禁止空话："针对痛点"、"功能设计"、"架构清晰"、"旨在解决"
6. ✅ 直接描述产品是什么、能做什么、为什么值得用
7. ✅ 连续段落，300字以内
8. ✅ 最后必须包含链接: {product_info['url']}

开头风格: 使用"{style}"的方式开头"""
```

### 3.3 内容验证

生成内容后必须验证：
1. 是否包含链接
2. 是否超过长度限制
3. 是否有结构化痕迹（正则检查）
4. 是否有重复开头（与历史内容对比）

---

## 四、发布模块开发规范

### 4.1 必须实现的功能

```python
class BasePublisher(ABC):
    def format_content(self, content: Dict) -> Dict:
        """
        格式化内容
        
        确保：
        1. 链接在内容中
        2. 长度符合平台限制
        3. 格式与其他发布模块一致
        """
        pass
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        pass
    
    def publish(self, content: Dict) -> bool:
        """发布单条内容"""
        pass
    
    def publish_batch(self, contents: List[Dict]) -> int:
        """批量发布，带错误处理和日志"""
        pass
```

### 4.2 错误处理规范

```python
try:
    response = self.session.post(url, json=payload, timeout=15)
    response.raise_for_status()
    logger.success(f"发布成功: {name}")
    return True
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # 速率限制处理
        retry_after = int(e.response.headers.get('Retry-After', 5))
        logger.warning(f"速率限制，等待 {retry_after} 秒...")
        time.sleep(retry_after)
        return self.publish(content)  # 重试
    else:
        logger.error(f"HTTP 错误: {e.response.status_code}")
        return False
        
except Exception as e:
    logger.error(f"发布失败: {e}")
    return False
```

### 4.3 格式一致性

所有发布模块必须保持内容格式一致：
```
标题（如适用）

自然叙述内容

链接
```

差异只在载体：
- Forum：创建帖子，有独立评论区
- Text：发送消息，无独立评论区

---

## 五、配置规范

### 5.1 配置文件结构

```yaml
# config.yaml
sources:
  source_name:
    enabled: true           # 布尔值，控制启用/禁用
    api_key: ""            # 敏感信息，优先从环境变量读取
    max_candidates: 10     # 整数
    timeout: 15            # 秒

processors:
  processor_name:
    enabled: true
    max_length: 400        # 内容长度限制

publishers:
  forum:                  # 模块标识符
    enabled: true
    webhook_url: ""        # Discord Webhook
    thread_name: "{name} – {source}"
    username: "AiTrend"
    delay: 2               # 发布间隔（秒）
```

### 5.2 环境变量命名

```bash
# 数据源API
{SOURCE}_API_KEY=xxx
GITHUB_TOKEN=xxx
PRODUCTHUNT_TOKEN=xxx

# 发布渠道
DISCORD_WEBHOOK_URL=xxx

# 大模型（可选）
OPENAI_API_KEY=xxx
# 大模型API（可选，默认使用Gemini）
```

---

## 六、日志规范

### 6.1 日志级别使用

```python
logger.debug("调试信息，开发使用")
logger.info("一般信息，流程记录")
logger.warning("警告，需要关注但可继续")
logger.error("错误，功能受影响")
logger.success("成功操作（自定义）")
```

### 6.2 必须记录的节点

- 模块初始化（配置信息）
- 数据源发现（数量）
- 内容生成（长度）
- 发布操作（成功/失败）
- 错误详情（异常信息）

### 6.3 日志格式

```
[2026-02-02 22:40:52] INFO: 模块初始化完成
[2026-02-02 22:40:52] INFO: 发现 10 个候选项目
[2026-02-02 22:40:55] SUCCESS: 发布成功: moltbook
[2026-02-02 22:40:57] ERROR: HTTP 错误: 429
```

---

## 七、测试流程

### 7.1 单元测试

```python
# test_new_module.py
def test_source():
    source = NewSource(config)
    assert source.is_enabled() == True
    
    candidates = source.discover()
    assert len(candidates) > 0
    assert 'name' in candidates[0]
    assert 'url' in candidates[0]
```

### 7.2 集成测试

1. 单模块测试
   ```bash
   python3 run_new_source.py
   ```

2. 全流程测试（限制数量）
   ```bash
   python3 launcher_v2.py
   ```

3. 发布测试
   ```bash
   python3 test_publisher.py
   ```

### 7.3 发布前检查清单

- [ ] 配置验证通过
- [ ] 日志记录完整
- [ ] 错误处理完善
- [ ] 文档已更新
- [ ] 测试通过

---

## 八、文档规范

### 8.1 必须文档

1. **SKILL.md** - 用户文档
   - 模块功能说明
   - 配置方法
   - 切换方法

2. **开发规范**（本文档）- 开发者文档
   - 接口规范
   - 开发步骤
   - 经验总结

3. **代码注释**
   - 类和方法docstring
   - 关键逻辑注释

### 8.2 文档更新时机

- 新增模块时
- 接口变更时
- 配置项变更时
- 发现新问题/解决方案时

---

## 九、常见错误与解决方案

### 9.1 模块加载失败

**现象：** `ModuleNotFoundError`
**原因：** 未在 `__init__.py` 注册
**解决：** 添加导入语句

### 9.2 API 返回空数据

**现象：** 发现 0 个项目
**原因：** API 限制、参数错误、Token 无效
**解决：** 
- 检查 Token
- 简化查询参数
- 添加调试日志

### 9.3 发布失败 400

**现象：** HTTP 400 Bad Request
**原因：** 内容格式错误、长度超限
**解决：**
- 检查 payload 格式
- 截断超长内容
- 验证必填字段

### 9.4 重复开头

**现象：** 多条内容开头相似
**原因：** 提示词缺乏多样性约束
**解决：**
- 添加开头多样化策略
- 使用索引选择不同风格
- 明确禁止套话

---

## 十、开发工作流程

### 10.1 新增信息源流程

1. 复制 `github_trend.py` 作为模板
2. 修改类名和 API 调用
3. 标准化返回字段
4. 添加日志记录
5. 注册到 `__init__.py`
6. 添加配置项到 `config.yaml`
7. 创建测试脚本
8. 测试并调试
9. 更新文档
10. 提交代码

### 10.2 新增发布模块流程

1. 继承 `BasePublisher`
2. 实现 `publish()` 和 `publish_batch()`
3. 添加配置验证
4. 添加错误处理
5. 注册到 `publishers/__init__.py`
6. 添加配置项
7. 测试发布功能
8. 更新文档

---

## 十一、经验总结

### 11.1 成功的做法

✅ **模块化先行**：先设计接口，再实现功能
✅ **配置驱动**：所有可变项提取到配置
✅ **详细日志**：每个关键节点记录状态
✅ **渐进开发**：一个模块一个模块开发测试
✅ **直接描述**：提示词约束比风格描述更有效

### 11.2 失败的教训

❌ **一次性开发多个模块**：调试困难
❌ **忽视配置验证**：运行时才发现缺少参数
❌ **日志不完善**：问题难以定位
❌ **套话提示词**：生成内容重复结构化
❌ **缺少错误处理**：API 失败导致整个流程中断

### 11.3 关键决策

1. **使用基类 + 工厂模式**：统一接口，易于扩展
2. **日志单例**：全局一致，自动文件分割
3. **提示词约束优先**：禁止比建议更有效
4. **直接发布到论坛**：避免对话污染
5. **环境变量 + 配置双重支持**：灵活部署

---

**文档版本：** 1.0  
**最后更新：** 2026-02-02  
**适用范围：** AiTrend 项目所有开发者
