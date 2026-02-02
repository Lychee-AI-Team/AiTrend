# AiTrend 信息源开发经验总结

## 一、已开发平台对比

### 1.1 平台特性对比

| 平台 | API类型 | 认证方式 | 数据特点 | 开发难度 | 内容风格 |
|------|---------|----------|----------|----------|----------|
| **GitHub** | REST API | Token (可选) | Star增长率、代码数据 | ⭐⭐ | 技术硬核 |
| **Product Hunt** | GraphQL | Token (必需) | 产品投票、Maker描述 | ⭐⭐⭐ | 产品导向 |
| **HackerNews** | Firebase | 无需认证 | 讨论热度、评论质量 | ⭐⭐ | 技术讨论 |
| **Reddit** | Pushshift | 无需认证 | 社区投票、草根反馈 | ⭐⭐ | 经验分享 |

### 1.2 各平台挖掘标准

**GitHub Trend**
- 指标：Star增长率 (stars/day) 而非绝对数量
- 计算：创建时间 → 今日时长 / star数量
- 语言：Python, Node.js, Go
- 阈值：0.5 stars/天

**Product Hunt**
- 指标：Upvote数量
- 分类：AI, Developer Tools, Productivity
- 时间：Daily/Weekly
- 阈值：50 votes

**HackerNews**
- 指标：Points + Comments
- 关键词：AI, machine learning, open source
- 阈值：100 points, 20 comments

**Reddit (Pushshift)**
- 指标：Upvotes
- 社区：r/MachineLearning, r/LocalLLaMA, r/technology
- 时间：最近7天
- 阈值：50 upvotes, 10 comments

---

## 二、开发经验总结

### 2.1 API接入经验

**GitHub**
```python
# 经验：使用Search API而非Trending页面
# 原因：Trending页面是HTML，Search API返回JSON
query = f"language:{lang} created:>{one_week_ago}"
url = "https://api.github.com/search/repositories"
```

**Product Hunt**
```python
# 经验：GraphQL比REST更灵活
# 坑点：需要正确的Authorization Header
headers = {'Authorization': f'Bearer {token}'}
```

**HackerNews**
```python
# 经验：Firebase API非常简单
# 注意：需要分别获取item详情
# 优化：并行处理多个items
```

**Reddit**
```python
# 经验：Pushshift无需OAuth
# 替代：Reddit官方API需要OAuth，Pushshift是更好选择
url = "https://api.pullpush.io/reddit/submission/search"
```

### 2.2 常见坑点

| 问题 | 平台 | 解决方案 |
|------|------|----------|
| 403 Forbidden | Reddit | 使用Pushshift替代 |
| 401 Unauthorized | Product Hunt | 检查Token格式 |
| Rate Limit | GitHub | 添加delay，使用Token |
| 空数据 | Pushshift | 放宽时间范围 |
| HTML解析 | GitHub Trend | 改用Search API |

### 2.3 内容生成经验

**提示词设计原则**
1. ❌ 禁止套话开头："最近发现"、"今天看到"
2. ❌ 禁止结构化：第一第二、首先其次
3. ❌ 禁止列表符号：- * •
4. ✅ 直接描述：是什么、能做什么、为什么值得用

**开头多样化策略**
```python
opening_styles = [
    "直接定义式",
    "功能切入式",
    "场景描述式",
    "对比传统式",
    "独特卖点式"
]
# 使用index % len(styles)循环
```

**内容长度控制**
- GitHub: 技术细节多，400字
- Product Hunt: 产品导向，300字
- HackerNews: 讨论为主，300字
- Reddit: 经验分享，300字

---

## 三、文档完善建议

### 3.1 新增文档

1. **API_KEY_SETUP.md** - 各平台API Key获取指南
2. **TROUBLESHOOTING.md** - 常见问题排查
3. **PLATFORM_GUIDE.md** - 各平台特点详细介绍
4. **CONTENT_STYLE.md** - 内容风格指南

### 3.2 现有文档更新

- [x] SKILL.md - 已完成
- [x] DEVELOPMENT_GUIDE.md - 已完成
- [x] QUICK_REFERENCE.md - 已完成
- [ ] 添加新平台时需同步更新

---

## 四、推荐新增信息源

### 4.1 高优先级

#### 1. **arXiv Papers** ⭐⭐⭐
- **URL**: https://arxiv.org/
- **API**: arXiv API (无需认证)
- **数据**: 最新AI/ML论文
- **价值**: 学术研究前沿
- **分类**: cs.AI, cs.CL, cs.LG, cs.CV
- **挖掘标准**: 最近7天，有代码链接
- **开发难度**: ⭐⭐

#### 2. **Twitter/X Tech** ⭐⭐⭐
- **URL**: https://twitter.com/
- **API**: Twitter API v2 (需认证)
- **数据**: 技术讨论、产品发布
- **价值**: 实时热点
- **关键词**: #AI, #MachineLearning, #BuildInPublic
- **挖掘标准**: 转发>100，有链接
- **开发难度**: ⭐⭐⭐

#### 3. **Lobsters** ⭐⭐
- **URL**: https://lobste.rs/
- **API**: RSS/JSON (无需认证)
- **数据**: 开发者讨论
- **价值**: 硬核技术社区
- **标签**: ai, ml, programming
- **挖掘标准**: 投票>10
- **开发难度**: ⭐⭐

### 4.2 中优先级

#### 4. **Dev.to** ⭐⭐
- **URL**: https://dev.to/
- **API**: Dev.to API (需Key)
- **数据**: 技术文章
- **价值**: 实用教程
- **标签**: ai, machinelearning
- **挖掘标准**: reactions>50

#### 5. **Medium (Towards Data Science)** ⭐⭐
- **URL**: https://medium.com/towards-data-science
- **API**: RSS (无需认证)
- **数据**: 数据科学文章
- **价值**: 入门教程
- **挖掘标准**: claps>100

#### 6. **YouTube (AI Channels)** ⭐⭐
- **URL**: https://youtube.com/
- **API**: YouTube Data API
- **数据**: 技术视频
- **价值**: 可视化学习
- **频道**: Two Minute Papers, Yannic Kilcher
- **挖掘标准**: views>10k

### 4.3 低优先级（特定领域）

#### 7. **Papers with Code** ⭐⭐
- **URL**: https://paperswithcode.com/
- **API**: 需抓取
- **数据**: SOTA论文+代码
- **价值**: 研究+工程结合

#### 8. **Kaggle** ⭐
- **URL**: https://kaggle.com/
- **API**: Kaggle API
- **数据**: Notebooks, Datasets
- **价值**: 实战代码

#### 9. **Stack Overflow** ⭐
- **URL**: https://stackoverflow.com/
- **API**: Stack API
- **数据**: 热门问题
- **价值**: 实际问题解决

### 4.4 中国平台（可选）

#### 10. **掘金 (Juejin)** ⭐⭐
- **URL**: https://juejin.cn/
- **API**: 需抓取
- **数据**: 中文技术文章
- **价值**: 中文社区

#### 11. **知乎 (Zhihu)** ⭐
- **URL**: https://zhihu.com/
- **API**: 需抓取
- **数据**: 中文讨论
- **价值**: 中文问答

---

## 五、下一步建议

### 5.1 短期（1-2周）

1. **添加 arXiv 模块**
   - 最有价值的信息源
   - 无需认证
   - 开发简单

2. **完善文档**
   - API_KEY_SETUP.md
   - TROUBLESHOOTING.md

3. **测试整合**
   - 所有模块并行运行
   - 测试完整流程

### 5.2 中期（1个月）

1. **添加 Twitter 模块**
   - 实时性强
   - 需要申请API Key

2. **内容整理模块**
   - 代码分析模块
   - 社区活跃度分析

3. **优化提示词**
   - A/B测试不同风格
   - 收集反馈

### 5.3 长期（3个月）

1. **添加更多平台**
   - Lobsters
   - Dev.to
   - Papers with Code

2. **自动化部署**
   - 定时任务
   - 监控告警

3. **数据分析**
   - 热门趋势分析
   - 内容效果统计

---

## 六、技术债务

### 6.1 当前问题

1. **Reddit OAuth**
   - 现状：使用Pushshift
   - 建议：如需实时数据，需实现OAuth

2. **LLM调用方式**
   - 现状：通过subprocess调用
   - 建议：封装为统一接口

3. **错误重试机制**
   - 现状：简单重试
   - 建议：指数退避

### 6.2 性能优化

1. **并发请求**
   - 各信息源可并行
   - 使用asyncio

2. **缓存机制**
   - API结果缓存
   - 避免重复请求

3. **增量更新**
   - 只获取新数据
   - 记录last_id

---

## 七、总结

**已完成**
- ✅ 4个信息源模块
- ✅ 完整文档体系
- ✅ 12条测试内容发布

**下一步推荐**
1. 🔥 arXiv（最高优先级）
2. 🔥 完善API Key文档
3. 🔥 代码分析模块

**长期价值**
- 信息源越多，内容越丰富
- 差异化内容吸引不同受众
- 建立信息壁垒

---

**文档版本**: 1.0  
**更新日期**: 2026-02-03  
**作者**: AiTrend Team
