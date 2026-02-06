# 问题根因分析与解决方案

## 🚨 核心问题确认

### 问题1: 视频文案没有信息量
**当前文案示例：**
> "ClawApp在Product Hunt发布，获得81个赞。这是一个新的AI工具产品，正在获得用户关注。"

**问题：** 这句话没有任何实质信息，观众不知道：
- ClawApp是做什么的？
- 有什么功能？
- 解决了什么问题？
- 为什么值得关注？

---

## 🔍 问题根因分析

### 根因1: AiTrend数据源缺陷 ❌
```json
// sent_articles.json 当前数据
{
  "title": "[Product Hunt] ClawApp ⭐81",
  "url": "https://...",
  "sent_at": 1234567890
  // ❌ 缺少: description, tagline, features
}
```

**问题：** AiTrend只存储了标题和URL，没有获取项目的详细介绍。

---

### 根因2: URL被Cloudflare保护 ❌
```
web_fetch(producthunt.com/products/clawapp)
→ 403 Forbidden (Cloudflare验证)
```

**问题：** 无法通过自动化工具获取网站详情。

---

### 根因3: 视频制作流程设计缺陷 ❌

**当前流程：**
```
文章标题 → TTS生成 → 视频
    ↓
  没有内容获取步骤！
```

**应该的流程：**
```
文章URL → 获取详情 → AI总结 → TTS生成 → 视频
            ↓
      (项目介绍/功能/价值)
```

---

## ✅ 根本解决方案

### 方案1: 修改AiTrend推送逻辑（推荐）

**修改文件：** `src/sources/producthunt.py`

```python
# 当前代码 - 只获取标题
title = item.get('name', '')

# 应该获取更多信息
article = {
    'title': item.get('name', ''),
    'tagline': item.get('tagline', ''),  # 一句话介绍
    'description': item.get('description', ''),  # 详细描述
    'features': extract_features(item),  # 功能列表
    'url': item.get('website', item.get('url', '')),
    'votes': item.get('votes_count', 0),
}
```

**Product Hunt API 提供的数据：**
- `name` - 产品名称
- `tagline` - 一句话介绍（关键！）
- `description` - 详细描述
- `topics` - 相关主题
- `makers` - 创作者信息

---

### 方案2: 使用AI根据URL生成介绍

```python
def generate_content_with_ai(title: str, url: str) -> str:
    """使用AI生成项目介绍"""
    prompt = f"""
    产品名称: {title}
    产品URL: {url}
    
    请根据产品名称和URL，推测这个AI产品的：
    1. 核心功能是什么？
    2. 解决了什么问题？
    3. 目标用户是谁？
    4. 为什么值得关注？
    
    输出一段30-50秒的中文介绍文案，用于视频播报。
    """
    
    return ai_generate(prompt)
```

---

### 方案3: 使用GitHub/GitLab API（针对开源项目）

```python
def get_github_info(repo_url: str) -> dict:
    """从GitHub API获取项目详情"""
    # https://api.github.com/repos/owner/repo
    # 获取: description, topics, readme
```

---

## 📋 重新设计的视频制作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    新的视频制作流程                          │
└─────────────────────────────────────────────────────────────┘

1. 热点收集
   ↓
   Product Hunt / GitHub / HackerNews
   ↓
   
2. 内容获取【新增步骤】
   ↓
   ├─ API获取详细信息 (tagline/description)
   ├─ 或AI生成内容
   └─ 或人工审核补充
   ↓
   
3. 内容审核【新增步骤】
   ↓
   人工确认信息准确性
   ↓
   
4. 文案生成
   ↓
   基于详细信息生成视频文案
   ↓
   
5. TTS生成
   ↓
   
6. 视频制作
   ↓
   
7. 渲染输出
```

---

## 🎯 产品经理思维：观众需要什么？

### 观众视角
- ❌ "ClawApp获得81个赞" →  meaningless
- ✅ "ClawApp是一款AI助手，可以自动整理你的笔记和任务" → valuable

### 信息价值金字塔
```
                    ┌─────────┐
         最高价值   │  为什么值得关注  │  (insight)
                    ├─────────┤
                    │  解决了什么问题  │  (value)
                    ├─────────┤
                    │  核心功能是什么  │  (features)
                    ├─────────┤
         最低价值   │  产品名称+平台   │  (basic info)
                    └─────────┘
```

### 好的视频文案示例
> "ClawApp是一款智能笔记助手，它可以自动分类你的笔记，提取关键任务，并生成每日待办清单。对于知识工作者来说，这意味着每天可以节省30分钟的整理时间，专注于真正重要的工作。"

---

## ⚡ 立即执行的修复方案

### 方案A: 人工补充文案（立即可用）
大师为每个热点提供介绍文案，我生成视频。

### 方案B: AI生成文案（需要测试）
我使用AI根据产品名称生成介绍，大师审核。

### 方案C: 修改数据源（长期方案）
修改AiTrend代码，在推送时获取更多详情。

---

**请确认使用哪个方案？** 🦞
