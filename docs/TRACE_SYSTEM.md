# 诊断回溯系统使用指南

## 概述

AiTrend 内置全流程追踪日志系统，为每条生成的内容分配唯一追踪ID，记录从信息发现到最终发布的完整处理流程。

---

## 追踪ID格式

```
AIT-YYYYMMDD-XXXXXX
```

示例：`AIT-20260203-A1B2C3`

---

## 在消息中查看追踪ID

每条发布的消息底部都会附带追踪ID：

```
这是消息正文内容...

---
🆔 **追踪ID**: `AIT-20260203-A1B2C3`
💡 如发现内容问题，请发送此ID进行诊断
```

---

## 诊断命令

### 1. 根据追踪ID诊断

```bash
python3 diagnose.py <追踪ID>
```

示例：
```bash
python3 diagnose.py AIT-20260203-A1B2C3
```

### 2. 查看最近的消息列表

```bash
python3 diagnose.py --recent
```

或使用 launcher：
```bash
python3 launcher.py --diagnose AIT-20260203-A1B2C3
```

---

## 诊断报告内容

诊断报告包含以下信息：

```
============================================================
🔍 诊断报告: AIT-20260203-A1B2C3
============================================================

📋 基本信息:
  信息名称: VideoGPA: Distilling Geometry Priors...
  信息源: arXiv
  创建时间: 2026-02-03T10:30:00
  当前状态: completed

🔧 模块执行 (4 个):
  ✅ source: success (2 条日志)
  ✅ readme_processor: success (3 条日志)
  ✅ narrative_composer: success (1 条日志)
  ✅ forum_publisher: success (1 条日志)

📝 关键日志:
  🟢 [10:30:01] source: 信息源 arXiv 发现 1 条候选
  🟢 [10:30:02] readme_processor: 模块 readme_processor 开始处理
  🟢 [10:30:03] readme_processor: README获取成功
  🟢 [10:30:04] narrative_composer: 内容合成完成
  🟢 [10:30:05] forum_publisher: 发布成功

🔗 原始链接: https://arxiv.org/abs/2601.23286
```

---

## 日志级别说明

| 级别 | 图标 | 含义 |
|------|------|------|
| DEBUG | 🔵 | 调试信息 |
| INFO | 🟢 | 正常流程 |
| WARNING | 🟡 | 警告（非致命）|
| ERROR | 🔴 | 错误（可能影响输出）|

---

## 常见问题诊断

### 问题1: 内容质量不佳

**症状**: 生成的介绍不够准确或详细

**诊断步骤**:
```bash
python3 diagnose.py <追踪ID>
```

查看：
- 处理器是否正常执行
- 输入数据是否完整
- README/搜索模块是否返回有效内容

### 问题2: 发布失败

**症状**: 消息未出现在 Discord

**诊断步骤**:
```bash
python3 diagnose.py <追踪ID>
```

查看：
- `forum_publisher` 或 `text_publisher` 状态
- 错误日志详情

### 问题3: 信息源无数据

**症状**: 某信息源长期无输出

**诊断步骤**:
```bash
python3 diagnose.py --recent
```

查看：
- 最近该信息源的追踪记录
- source 模块的日志

---

## 日志文件位置

追踪日志存储在：
```
logs/traces/
├── 20260203/
│   ├── AIT-20260203-A1B2C3.json
│   ├── AIT-20260203-D4E5F6.json
│   └── ...
├── 20260202/
│   └── ...
```

每个追踪ID对应一个 JSON 文件，包含：
- 完整处理流程
- 所有模块日志
- 输入输出数据
- 错误信息

---

## 配置选项

在 `config.yaml` 中启用/禁用追踪：

```yaml
system:
  enable_trace: true  # 启用追踪日志
```

---

## 使用场景示例

### 场景1: 用户反馈某条消息有问题

用户发送：
> "这条消息的内容好像不太对，追踪ID是 AIT-20260203-A1B2C3"

诊断：
```bash
python3 diagnose.py AIT-20260203-A1B2C3
```

### 场景2: 批量检查最近发布

```bash
python3 diagnose.py --recent
```

### 场景3: 排查发布失败

```bash
python3 diagnose.py AIT-20260203-XXXXXX
```

查看 `forum_publisher` 状态是否为 `error`

---

## 技术细节

### 追踪系统架构

```
信息发现 → 生成追踪ID → 记录各模块日志 → 发布 → 附带追踪ID
    ↓
TraceLogger (单例)
    ↓
logs/traces/YYYYMMDD/<trace_id>.json
```

### 日志内容

每个追踪记录包含：
- `trace_id`: 唯一标识
- `source`: 信息源
- `name`: 信息名称
- `url`: 原始链接
- `status`: 处理状态 (started/completed/error/failed)
- `logs[]`: 详细日志列表
- `modules{}`: 各模块执行状态
- `errors[]`: 错误列表
- `final_output`: 最终输出（前1000字符）

---

## 注意事项

1. **日志保留**: 默认长期保留，定期手动清理旧日志
2. **敏感信息**: 日志中可能包含 API 响应，注意保护
3. **性能**: 追踪对性能影响极小，建议始终启用

---

**文档版本**: 1.0  
**更新日期**: 2026-02-03
