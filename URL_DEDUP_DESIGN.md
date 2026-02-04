# URL 去重完美方案设计

## 问题分析

### 矛盾点
- **情况A**: `?srsltid=xxx` → 同一篇文章，应该去重 ✅
- **情况B**: `?id=123` vs `?id=456` → 不同文章，应该保留 ❌
- **情况C**: `?page=1` vs `?page=2` → 不同内容，应该保留 ❌

### 核心挑战
如何区分 **跟踪参数** vs **内容参数**？

---

## 完美方案：多层防御体系

### 第一层：智能参数识别（白名单）

```python
# 只移除已知的"纯跟踪参数"
TRACKING_PARAMS = {
    # 广告/分析跟踪
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'gclid', 'fbclid', 'msclkid', 'dclid', 'zanpid', 'kenshoo',
    
    # 社交媒体跟踪
    'srsltid',  # Google
    'si', 'igshid', 'ttclid',  # TikTok/Instagram
    'twclid', 'li_fat_id',  # Twitter/LinkedIn
    
    # 邮件/推广跟踪
    'mc_cid', 'mc_eid',  # Mailchimp
    'yclid', 'cid', 'ecid',
    'ref', 'referrer', 'referral_code',
    
    # A/B测试
    'variant', 'ab_test', 'exp_id',
}

# 保留的"内容参数"（白名单）
CONTENT_PARAMS = {
    'id', 'post', 'article', 'p', 'story',
    'page', 'offset', 'cursor', 'next',
    'category', 'tag', 'topic', 'channel',
    'user', 'author', 'u',
    'v', 'version', 'rev',
    'lang', 'locale', 'l',
    'format', 'type', 't',
}
```

### 第二层：路径优先策略

```python
def get_url_signature(url: str) -> str:
    """
    生成 URL 签名用于去重
    策略：路径优先，参数次之
    """
    parsed = urlparse(url)
    
    # 1. 基础路径（最重要）
    base_path = parsed.path.rstrip('/')
    
    # 2. 保留内容参数，移除跟踪参数
    query_params = parse_qsl(parsed.query)
    content_params = [
        f"{k}={v}" for k, v in query_params
        if k.lower() not in TRACKING_PARAMS
    ]
    
    # 3. 生成签名
    if content_params:
        return f"{base_path}?{'&'.join(sorted(content_params))}"
    return base_path
```

### 第三层：内容指纹兜底

```python
import hashlib

def content_fingerprint(title: str, summary: str = "") -> str:
    """
    基于内容的指纹
    即使 URL 不同，相同内容也能识别
    """
    # 提取关键词（标题前50字 + 摘要前100字）
    text = (title[:50] + summary[:100]).lower()
    
    # 移除常见噪音词
    noise_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for'}
    words = [w for w in re.findall(r'\b\w+\b', text) 
             if w not in noise_words and len(w) > 2]
    
    # 排序后生成指纹（确保相同关键词不同顺序也得到相同指纹）
    fingerprint_text = ''.join(sorted(words))
    return hashlib.sha256(fingerprint_text.encode()).hexdigest()[:16]
```

### 第四层：域名特定规则

```python
DOMAIN_RULES = {
    # 新闻媒体：通常 ID 参数是内容标识
    'techcrunch.com': {'keep_params': ['id', 'guccounter']},
    'medium.com': {'keep_params': []},  # Medium 路径即 ID
    
    # 论坛：可能用 ?t=123 表示帖子
    'news.ycombinator.com': {'keep_params': ['id']},
    
    # 电商：需要保留商品 ID
    'amazon.com': {'keep_params': ['dp', 'asin']},
    'producthunt.com': {'keep_params': ['utm_campaign']},  # PH 用 utm 作为产品标识
    
    # 默认规则
    'default': {'keep_params': ['id', 'post', 'p', 'article']}
}
```

### 第五层：相似度检测

```python
from difflib import SequenceMatcher

def url_similarity(url1: str, url2: str) -> float:
    """
    计算两个 URL 的相似度
    用于检测细微差异的重复
    """
    # 规范化后比较
    sig1 = get_url_signature(url1)
    sig2 = get_url_signature(url2)
    
    return SequenceMatcher(None, sig1, sig2).ratio()

# 使用：相似度 > 0.9 认为是同一篇文章
def is_likely_duplicate(url1: str, url2: str) -> bool:
    return url_similarity(url1, url2) > 0.9
```

---

## 完整实现代码

```python
class SmartDeduplicator:
    """智能去重器 - 完美兼容各类 URL"""
    
    def __init__(self, memory_path: str = None):
        self.memory_path = memory_path
        self.window_hours = 24
        
        # 加载配置
        self.config = self._load_config()
    
    def is_duplicate(self, article: Article) -> bool:
        """
        多层检测是否是重复文章
        只要满足任一条件即认为是重复
        """
        url = article.url
        title = article.title
        summary = article.summary
        
        # 第一层：URL 签名匹配
        url_sig = self._get_url_signature(url)
        if self._check_signature_exists(url_sig):
            return True
        
        # 第二层：内容指纹匹配
        content_fp = content_fingerprint(title, summary)
        if self._check_fingerprint_exists(content_fp):
            return True
        
        # 第三层：URL 相似度检测
        if self._check_similar_url_exists(url):
            return True
        
        return False
    
    def _get_url_signature(self, url: str) -> str:
        """获取 URL 签名（移除了跟踪参数）"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 获取域名特定规则
        domain_rule = self.DOMAIN_RULES.get(domain, self.DOMAIN_RULES['default'])
        keep_params = set(domain_rule.get('keep_params', []))
        
        # 构建签名
        base_path = parsed.path.rstrip('/')
        query_params = parse_qsl(parsed.query)
        
        # 保留内容参数 + 域名特定参数
        filtered = []
        for k, v in query_params:
            k_lower = k.lower()
            if k_lower in keep_params or k_lower in self.CONTENT_PARAMS:
                filtered.append(f"{k}={v}")
        
        if filtered:
            return f"{domain}{base_path}?{'&'.join(sorted(filtered))}"
        return f"{domain}{base_path}"
```

---

## 配置示例

```yaml
deduplication:
  # 基础配置
  window_hours: 24
  
  # URL 签名配置
  url_signature:
    # 要移除的跟踪参数
    remove_params:
      - utm_*
      - gclid
      - fbclid
      - srsltid
    
    # 要保留的内容参数
    keep_params:
      - id
      - post
      - article
      - p
  
  # 内容指纹配置
  content_fingerprint:
    enabled: true
    title_weight: 0.6
    summary_weight: 0.4
    min_content_length: 50
  
  # 相似度检测配置
  similarity:
    enabled: true
    threshold: 0.9  # 90% 相似度认为是重复
  
  # 域名特定规则
  domain_rules:
    "medium.com":
      ignore_params: true  # Medium 只用路径
    
    "producthunt.com":
      keep_params:
        - utm_campaign  # PH 用这个标识产品
```

---

## 预期效果

| 场景 | 旧方案 | 新方案 |
|------|--------|--------|
| vertu.com/?srsltid=xxx | ❌ 9次重复 | ✅ 1次 |
| example.com/?id=123 vs ?id=456 | ❌ 可能误删 | ✅ 正确保留 |
| example.com/?page=1 vs ?page=2 | ❌ 可能误删 | ✅ 正确保留 |
| 不同 URL 相同标题 | ❌ 漏检 | ✅ 指纹检测 |
| 细微 URL 差异 | ❌ 漏检 | ✅ 相似度检测 |

---

## 实施建议

### Phase 1: 立即实施（已部分完成）
- ✅ 白名单跟踪参数移除
- ⏳ 添加路径优先策略

### Phase 2: 增强版（本周）
- 添加内容指纹
- 添加相似度检测
- 添加域名规则

### Phase 3: 智能化（可选）
- 机器学习识别参数类型
- 自适应规则调整

**大师觉得这个方案如何？可以开始编码吗？** 🦞