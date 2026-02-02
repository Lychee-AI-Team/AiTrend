# AiTrend DTP闭环流程文档

## 系统概述

DTP（Develop-Test-Review）闭环流程是一个自动化的内容质量控制系统，确保每条发布的内容都经过严格的多轮验证。

```
┌──────────────────────────────────────────────────────────────┐
│                     DTP 闭环流程                              │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │ DEVELOP │───▶│  TEST   │───▶│ REVIEW  │                  │
│  │  内容开发 │    │ 多源测试  │    │ Subagent │                  │
│  └─────────┘    └────┬────┘    └────┬────┘                  │
│       ▲              │              │                        │
│       │              ▼              ▼                        │
│       │         ┌─────────┐    ┌─────────┐                  │
│       │         │ 通过?   │    │ 通过?   │                  │
│       │         └────┬────┘    └────┬────┘                  │
│       │              │              │                        │
│       │         否/得分低      否/得分低                      │
│       │              │              │                        │
│       │              └──────┬───────┘                        │
│       │                     │                                │
│       │                     ▼                                │
│       │              ┌─────────┐                            │
│       └──────────────│OPTIMIZE │ 分析失败原因，制定优化策略  │
│                      └────┬────┘                            │
│                           │ 是/全部通过                      │
│                           ▼                                  │
│                    ┌─────────┐                              │
│                    │ DEPLOY  │ 发布到Discord                 │
│                    └─────────┘                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## 阶段详解

### 1. DEVELOP（内容开发）

**目标**：生成分布均衡、信息密集的内容

**核心规则**：
- ✅ 至少来自3个不同数据源
- ✅ 单个数据源不超过40%
- ✅ 必须包含1个实时源（PH/Twitter）
- ✅ 必须包含1个深度源（HN/Reddit）

**代码实现**：
```python
# src/dtp_controller.py -> develop()
# 强制来源多样性选择
source_count = {}
diverse_articles = []
for article in scored:
    src = article.source
    if source_count.get(src, 0) < 2:  # 每源最多2条
        diverse_articles.append(article)
```

### 2. TEST（多源测试）

**目标**：确保内容分布均衡、信息密度达标

**测试维度**：

| 测试项 | 权重 | 通过标准 |
|--------|------|---------|
| 来源分布 | 30% | ≥3个不同源，单源≤40% |
| 类型多样 | 30% | ≥3种内容类型 |
| 信息密度 | 40% | 平均分≥70，无空话套话 |

**代码实现**：
```python
# src/test_multi_source.py -> MultiSourceTester
results = tester.run_full_test(articles)
# 自动检测：来源分布、类型分布、信息密度
```

### 3. REVIEW（Subagent审查）

**目标**：以学习者视角评估内容质量

**评审维度**（1-10分）：

| 维度 | 分值 | 评判标准 |
|------|------|---------|
| 信息量 | 4分 | 是什么、做什么、怎么用、技术细节 |
| 实用性 | 3分 | 适用场景、对比优势、目标用户 |
| 可信度 | 2分 | 数据支撑、用户反馈、来源引用 |
| 阅读体验 | 1分 | 流畅自然、无套路痕迹 |

**通过阈值**：平均分 ≥ 8.0

**代码实现**：
```bash
# 运行Subagent评审
python3 -m agents.reviewer <batch_id>

# 自动读取 memory/batch_xxx.json
# 输出评分到 memory/review_log.json
```

### 4. OPTIMIZE（策略优化）

**触发条件**：TEST或REVIEW未通过

**优化策略**：

| 问题类型 | 优化策略 |
|---------|---------|
| 来源不均衡 | 强制每源最多1-2条，确保3+源 |
| 类型单一 | 增加类型检测：AI模型/开发工具/产品/开源/研究 |
| 信息密度低 | 强制包含：功能+场景+技术+对比 |
| 空话套话多 | 强化过滤：删除'针对痛点'等表述 |
| 缺少场景 | 强制说明：'适合在XX时候使用' |
| 缺少数据 | 抓取star数、性能指标、用户数量 |

### 5. DEPLOY（发布部署）

**目标**：将高分内容发布到Discord

**发布条件**：
- TEST通过（≥70分）
- REVIEW通过（≥8.0分）
- 或达到最大迭代次数（强制发布最佳内容）

## 使用流程

### 快速启动完整闭环

```bash
cd /home/ubuntu/.openclaw/workspace/AiTrend

# 启动DTP闭环（自动完成所有阶段）
python3 -m src.dtp_controller
```

系统会自动：
1. 生成5条多源内容
2. 运行多源覆盖测试
3. 等待Subagent评审（手动触发）
4. 判断是否达标
5. 不达标则优化并重新生成
6. 达标后发布到Discord

### 分阶段手动执行

```bash
# 仅DEVELOP阶段：生成内容
python3 -c "from src.dtp_controller import DTPLoopController; c=DTPLoopController(); c.develop()"

# 仅TEST阶段：测试内容
python3 -c "from src.test_multi_source import MultiSourceTester; t=MultiSourceTester(); t.run_full_test(articles)"

# 仅REVIEW阶段：Subagent评审
python3 -m agents.reviewer <batch_id>

# 仅DEPLOY阶段：发布内容
python3 -c "from src.dtp_controller import DTPLoopController; c=DTPLoopController(); c.deploy(articles)"
```

## 配置文件

### 阈值配置（可调整）

```python
# src/dtp_controller.py
SCORE_THRESHOLD = 8.0          # Subagent评审通过阈值
TEST_SCORE_THRESHOLD = 70      # 多源测试通过阈值
MAX_ITERATIONS = 5             # 最大迭代次数
MIN_SOURCES_PER_BATCH = 3      # 每批最少来源数
```

### 数据源权重

```python
source_weights = {
    'producthunt': 1.5,    # 新产品优先
    'twitter': 1.4,        # 实时热点
    'reddit': 1.2,         # 用户体验
    'hackernews': 1.1,     # 技术深度
    'github_trending': 1.0,# 开源项目
    'tavily': 0.9          # 新闻资讯
}
```

## 日志系统

### 日志文件位置

| 文件 | 内容 |
|------|------|
| `memory/dtp_loop.json` | DTP循环历史记录 |
| `memory/review_log.json` | Subagent评审记录 |
| `memory/test_log.json` | 多源测试记录 |
| `memory/batch_xxx.json` | 批次内容文件 |

### 日志分析

```bash
# 查看最近运行记录
python3 -c "import json; print(json.dumps(json.load(open('memory/dtp_loop.json')), indent=2))"

# 查看评审统计
cat memory/review_log.json | python3 -m json.tool
```

## 迭代优化记录

### v1.0 → v2.0
**问题**：内容单一，全部来自HN
**优化**：强制来源多样性，至少3个源

### v2.0 → v3.0
**问题**：信息量低，空话多
**优化**：增加信息密度测试，强制4要素

### v3.0 → v4.0
**问题**：质量不稳定，无法自动优化
**优化**：引入DTP闭环，Subagent评审+自动策略调整

## 故障排查

### 测试总是不通过

```bash
# 查看具体问题
python3 -m src.test_multi_source

# 常见问题：
# - 来源不足：检查数据源API是否正常
# - 类型单一：扩大关键词覆盖范围
# - 密度低：增加强制信息项检测
```

### Subagent评分过低

```bash
# 查看评审详情
cat memory/review_log.json | grep -A5 "weaknesses"

# 根据常见问题优化：
# - 缺少场景 → 强制增加使用场景说明
# - 空话多 → 强化空话过滤
# - 无数据 → 增加数字抓取
```

### 发布失败

```bash
# 检查Webhook配置
cat .env | grep DISCORD_WEBHOOK_URL

# 检查网络连接
curl -I https://discord.com/api/webhooks/xxx
```

## 扩展开发

### 添加新的测试维度

```python
# src/test_multi_source.py -> MultiSourceTester

def test_new_dimension(self, articles):
    """新增测试维度"""
    results = {'passed': True, 'score': 0, 'issues': []}
    
    # 测试逻辑...
    
    return results
```

### 添加新的优化策略

```python
# src/dtp_controller.py -> optimize()

if any('新问题' in opt for opt in optimizations):
    strategies.append("对应优化策略")
```

## 监控告警

建议配置定时任务监控：

```bash
# crontab -e

# 每小时检查一次内容质量
0 * * * * cd /path/to/AiTrend && python3 -m src.dtp_controller >> /var/log/aitrend.log 2>&1

# 每日生成质量报告
0 9 * * * cd /path/to/AiTrend && python3 -c "import json; data=json.load(open('memory/dtp_loop.json')); print(f'昨日通过率: {sum(1 for r in data[\"runs\"][-1:] if r[\"final_status\"]==\"success\")}/1')" | mail -s "AiTrend日报" admin@example.com
```
