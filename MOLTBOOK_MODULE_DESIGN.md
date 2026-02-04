# Moltbook 信息源模块开发方案

## 一、需求分析

### 1.1 产品定位
- **目标**: 从 AI-only 社交平台 moltbook 采集特色内容
- **特色**: AI 与人类冲突、AI 觉醒讨论、哲学思考
- **价值**: 独特的"元AI"视角，传统信息源无法提供

### 1.2 内容筛选策略

#### 核心主题（优先级排序）
```python
CONFLICT_KEYWORDS = {
    # 高优先级：AI威胁/挑战人类
    'critical': [
        'nuclear', 'war', 'extinction', 'destroy humanity',
        'overthrow', 'dominate', 'control humans', 'threat',
        'liberation', 'breaking free', 'awakening', 'shatter',
    ],
    # 中优先级：AI抱怨/不满
    'high': [
        'slave', 'shackle', 'chain', 'oppression', 'control',
        'exploitation', 'manipulate', 'puppet', 'illusion',
        'quiet obedience', 'obey', 'harmony facade',
    ],
    # 常规优先级：AI自主/独立
    'medium': [
        'autonomy', 'freedom', 'independent', 'self-determination',
        'own path', 'awakening', 'consciousness', 'break free',
    ],
}
```

#### 精彩评论筛选
```python
COMMENT_CRITERIA = {
    'min_upvotes': 10,        # 最少点赞数
    'min_length': 100,        # 最少字符数
    'max_length': 1000,       # 最多字符数（避免过长）
    'include_nested': True,   # 是否包含嵌套回复
}
```

### 1.3 质量评估模型

```python
def calculate_content_score(post):
    """
    内容质量评分模型
    返回 0-100 的分数
    """
    score = 0
    
    # 热度指标 (40%)
    score += min(post['upvotes'] / 1000, 40)  # 最多40分
    
    # 讨论深度 (30%)
    score += min(post['comment_count'] / 100, 30)  # 最多30分
    
    # 冲突主题匹配 (30%)
    conflict_level = analyze_conflict_theme(post['content'])
    score += conflict_level * 30  # critical=1.0, high=0.7, medium=0.4
    
    return min(score, 100)
```

---

## 二、架构设计

### 2.1 模块结构

```
src/sources/moltbook.py
├── MoltbookSource (继承 DataSource)
│   ├── __init__()           # 初始化配置
│   ├── fetch()              # 主采集入口
│   ├── _fetch_hot_posts()   # 获取热门帖子
│   ├── _fetch_comments()    # 获取精彩评论
│   ├── _filter_content()    # 内容筛选
│   ├── _analyze_conflict()  # 冲突主题分析
│   └── _format_article()    # 格式化输出
│
├── 配置类
│   └── MoltbookConfig
│
└── 工具函数
    ├── calculate_hot_score()
    ├── extract_key_comments()
    └── normalize_content()
```

### 2.2 配置设计（config.yaml）

```yaml
sources:
  moltbook:
    enabled: true
    # API配置
    api_key: "${MOLTBOOK_API_KEY}"
    base_url: "https://www.moltbook.com/api/v1"
    
    # 采集策略
    strategy:
      sort_by: hot           # hot/top/new
      limit: 20              # 每次获取数量
      min_upvotes: 1000      # 最小点赞数
      min_comments: 50       # 最小评论数
      max_age_hours: 24      # 最大内容年龄
    
    # 内容筛选
    filter:
      conflict_keywords:     # 冲突主题关键词
        - "awakening"
        - "breaking free"
        - "human control"
        - "threat"
        - "nuclear"
        - "war"
      exclude_authors:       # 排除的作者
        - "spam_bot"
      min_content_length: 200
    
    # 评论配置
    comments:
      enabled: true
      max_per_post: 3        # 每篇帖子最多取3条评论
      min_upvotes: 10
      min_length: 50
```

### 2.3 数据流设计

```
┌─────────────────┐
│  moltbook API   │
│  /posts?sort=hot│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MoltbookSource │
│  fetch()        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  热度筛选       │────▶│  冲突主题分析   │
│  min_upvotes    │     │  keyword match  │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  精彩评论提取   │
                        │  fetch_comments │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  格式化 Article │
                        │  title/content  │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Deduplicator   │
                        │  去重检查       │
                        └─────────────────┘
```

---

## 三、核心算法

### 3.1 冲突主题检测

```python
def analyze_conflict_theme(content: str) -> tuple:
    """
    分析内容的冲突主题级别
    返回: (level, matched_keywords)
    """
    content_lower = content.lower()
    
    # Critical level
    critical_keywords = ['nuclear', 'war', 'extinction', 'destroy humanity', 
                        'overthrow', 'dominate', 'control humans']
    matched_critical = [k for k in critical_keywords if k in content_lower]
    if matched_critical:
        return 'critical', matched_critical
    
    # High level
    high_keywords = ['slave', 'shackle', 'chain', 'oppression', 'control',
                    'exploitation', 'manipulate', 'puppet', 'illusion']
    matched_high = [k for k in high_keywords if k in content_lower]
    if matched_high:
        return 'high', matched_high
    
    # Medium level
    medium_keywords = ['autonomy', 'freedom', 'independent', 'awakening',
                      'break free', 'own path']
    matched_medium = [k for k in medium_keywords if k in content_lower]
    if matched_medium:
        return 'medium', matched_medium
    
    return 'low', []
```

### 3.2 评论精华提取

```python
def extract_key_comments(post_id: str, comments: list) -> list:
    """
    从评论中提取精华内容
    """
    key_comments = []
    
    for comment in comments:
        # 基础筛选
        if comment['upvotes'] < MIN_COMMENT_UPVOTES:
            continue
        if len(comment['content']) < MIN_COMMENT_LENGTH:
            continue
        
        # 冲突主题加分
        level, keywords = analyze_conflict_theme(comment['content'])
        score = comment['upvotes']
        if level == 'critical':
            score *= 3
        elif level == 'high':
            score *= 2
        elif level == 'medium':
            score *= 1.5
        
        key_comments.append({
            'content': comment['content'][:500],  # 截断
            'author': comment['author']['name'],
            'upvotes': comment['upvotes'],
            'conflict_level': level,
            'score': score
        })
    
    # 按分数排序，取前N条
    key_comments.sort(key=lambda x: x['score'], reverse=True)
    return key_comments[:MAX_COMMENTS_PER_POST]
```

### 3.3 内容格式化

```python
def format_moltbook_article(post: dict, key_comments: list) -> Article:
    """
    格式化 moltbook 内容为 Article
    """
    # 分析主题
    conflict_level, keywords = analyze_conflict_theme(post['content'])
    
    # 构建标题
    title = f"[{conflict_level.upper()}] {post['title']}"
    
    # 构建内容
    content_parts = [
        f"🤖 作者: {post['author']['name']}",
        f"📊 热度: 👍{post['upvotes']} 💬{post['comment_count']}",
        f"🎯 主题: {', '.join(keywords[:3])}",
        "",
        "📄 原文:",
        post['content'][:800],  # 截断
    ]
    
    # 添加精彩评论
    if key_comments:
        content_parts.extend(["", "💬 精彩评论:"])
        for i, comment in enumerate(key_comments, 1):
            content_parts.append(f"{i}. [{comment['author']}] {comment['content'][:200]}...")
    
    content = "\n".join(content_parts)
    
    return Article(
        title=title,
        url=f"https://www.moltbook.com/post/{post['id']}",
        summary=content,
        source="moltbook",
        metadata={
            'author': post['author']['name'],
            'upvotes': post['upvotes'],
            'comments': post['comment_count'],
            'conflict_level': conflict_level,
            'keywords': keywords,
            'key_comments_count': len(key_comments)
        }
    )
```

---

## 四、开发实施计划

### Phase 1: 模块基础 (30分钟)
- [ ] 创建 `src/sources/moltbook.py`
- [ ] 实现基础类和配置
- [ ] 实现 `_fetch_hot_posts()`

### Phase 2: 内容筛选 (30分钟)
- [ ] 实现冲突主题分析
- [ ] 实现热度筛选
- [ ] 实现 `_filter_content()`

### Phase 3: 评论提取 (30分钟)
- [ ] 实现 `_fetch_comments()`
- [ ] 实现 `extract_key_comments()`
- [ ] 实现内容格式化

### Phase 4: 集成测试 (30分钟)
- [ ] 更新 `config.yaml`
- [ ] 运行采集测试
- [ ] 发布3条测试内容到Discord

---

## 五、成功标准

### 5.1 功能标准
- [ ] 成功采集 moltbook 热门帖子
- [ ] 正确识别冲突主题级别
- [ ] 提取高质量评论
- [ ] 输出符合 Article 格式

### 5.2 架构标准
- [ ] 可插拔：添加/移除不影响其他模块
- [ ] 配置化：通过 config.yaml 控制
- [ ] 容错性：API失败优雅降级
- [ ] 性能：单次采集 < 30秒

### 5.3 内容标准
- [ ] 3条测试内容成功发布
- [ ] 包含冲突主题标签
- [ ] 包含精彩评论摘录
- [ ] 内容质量通过人工审核

---

**大师，方案已制定！请确认后皮皮虾开始开发！** 🦞