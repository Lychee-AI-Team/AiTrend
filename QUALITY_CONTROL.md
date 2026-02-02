# AiTrend 质量控制系统使用说明

## 系统架构

```
┌─────────────┐     生成内容      ┌─────────────┐
│   主Agent   │ ───────────────▶ │  SubAgent   │
│ (quality_   │                  │  (reviewer) │
│  control.py)│ ◀─────────────── │             │
└─────────────┘     返回评分      └─────────────┘
        │                                │
        │ 发布高分内容                   │ 读取批次
        ▼                                ▼
┌─────────────┐                  ┌─────────────┐
│   Discord   │                  │  batch_xxx  │
│   讨论区    │                  │   .json     │
└─────────────┘                  └─────────────┘
```

## 使用流程

### 1. 启动质量控制系统

```bash
cd /home/ubuntu/.openclaw/workspace/AiTrend
python3 -m src.quality_control
```

系统会：
1. 生成5条候选内容
2. 保存到 `memory/batch_xxx.json`
3. 等待Subagent评审

### 2. 启动Subagent评审

```bash
python3 -m agents.reviewer <batch_id>
```

例如：
```bash
python3 -m agents.reviewer 20250202_193000
```

Subagent会：
1. 读取批次内容
2. 以AI学习者视角逐条评审
3. 给出1-10分评分
4. 保存到 `memory/review_log.json`

### 3. 系统自动判断

- 平均分 ≥ 8.0：自动发布到Discord
- 平均分 < 8.0：收集问题，优化策略，重新生成

### 4. 循环优化

如果评分不达标，系统会：
1. 分析问题模式
2. 调整生成参数
3. 重新生成5条
4. 再次评审
5. 直到达标或达到最大迭代次数

## 评分标准

| 维度 | 分值 | 评判要点 |
|------|------|---------|
| 信息量 | 4分 | 是什么、能做什么、怎么用、技术细节 |
| 实用性 | 3分 | 适用场景、对比优势、目标用户 |
| 可信度 | 2分 | 数据支撑、用户反馈、来源引用 |
| 阅读体验 | 1分 | 流畅自然、无套路痕迹 |

## 常见问题

**Q: Subagent评分主观性太强怎么办？**
A: 评审标准已量化，基于关键词检测和结构分析，减少主观判断。

**Q: 每次都要手动运行Subagent吗？**
A: 当前版本需要手动触发。后续可以通过cron自动触发subagent评审。

**Q: 如何查看评审历史？**
A: 查看 `memory/review_log.json` 文件。

## 文件说明

- `src/quality_control.py` - 主控制流程
- `agents/reviewer.py` - Subagent评审脚本
- `agents/reviewer_persona.md` - Subagent角色定义
- `memory/batch_xxx.json` - 批次内容文件
- `memory/review_log.json` - 评审日志
