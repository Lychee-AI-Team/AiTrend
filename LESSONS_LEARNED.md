# AiTrend 视频制作项目 - 错误总结与经验记录

**记录时间**: 2026-02-06  
**记录人**: OpenClaw  
**项目**: AiTrend 自动视频生成

---

## 📋 项目背景

本项目旨在将AiTrend收集的AI热点信息自动转换为短视频，包括：
- 从Discord/数据源获取AI热点
- 生成TTS语音
- 使用Remotion渲染视频
- 输出60秒竖版短视频

---

## ❌ 错误记录与解决方案

### 错误 #1: 音频路径错误 - `full_audio.mp3` 显示 undefined

**症状**:
```
Studio中显示: undefined/index-chinese-fixed.tsx:89
```

**根本原因**:
- 音频文件放在 `assets/audio/` 目录
- Remotion的 `staticFile()` 从 `public/` 目录读取
- 路径不匹配导致找不到文件

**解决方案**:
```bash
# 错误路径
assets/audio/2026-02-06/full_audio.mp3

# 正确路径
src/public/audio/2026-02-06/full_audio.mp3
```

**经验教训**:
- Remotion的文件访问必须使用 `staticFile()` 
- `staticFile()` 只能从 `public/` 目录读取
- 生成音频后必须复制到 `public/` 目录

---

### 错误 #2: 网站截图被Cloudflare拦截

**症状**:
```
❌ 截图失败: Page.goto: Timeout 30000ms exceeded
截图显示Cloudflare验证页面
```

**根本原因**:
- Product Hunt等网站使用高级反爬虫保护
- TLS指纹检测 + 行为分析
- Playwright被识别为自动化工具

**尝试的解决方案**:
1. User-Agent伪装 ❌ 失败
2. 禁用自动化检测 ❌ 失败
3. 延长等待时间 ❌ 失败
4. 使用Open Graph图片 ❌ 部分网站不支持

**最终解决方案**:
- **放弃截图方案**，改为卡片式设计
- 显示：中文解读 + URL + 排名
- 不依赖外部网站截图

**经验教训**:
- 网站截图不稳定，容易被拦截
- 应该设计不依赖截图的UI方案
- 卡片式设计更稳定、更可控

---

### 错误 #3: 视频文案没有信息量（垃圾内容）

**症状**:
```
文案: "ClawApp获得81个赞，是一个新的AI产品。"
问题: 观众不知道产品是做什么的
```

**根本原因**:
- `sent_articles.json` 只存储了标题和URL
- 缺少 `summary` 和 `metadata` 字段
- `deduplicator.py` 的存储逻辑缺陷

**代码缺陷**:
```python
# 修复前 - 只存储基础字段
sent_articles.append({
    'url': article.url,
    'title': article.title,  # 只有标题
    # ❌ 缺少 summary
    # ❌ 缺少 metadata
})
```

**解决方案**:
```python
# 修复后 - 存储完整信息
sent_articles.append({
    'url': article.url,
    'title': article.title,
    'summary': article.summary,        # ✅ 新增
    'source': article.source,          # ✅ 新增
    'metadata': article.metadata,      # ✅ 新增
})
```

**经验教训**:
- 数据存储必须完整，不能只存标题
- 需要包含：summary、source、metadata
- 修改存储逻辑后要重新获取数据

---

### 错误 #4: 音频与视频时长不匹配

**症状**:
```
音频时长: 27秒
视频时长: 60秒
问题: 视频播完了音频还没放完，或音频放完了视频还在
```

**根本原因**:
- 使用了固定的60秒视频模板
- 没有根据音频实际长度调整场景时长

**解决方案**:
```typescript
// 动态计算场景时长
const sceneDuration = audioDurationInSeconds * fps;

<Sequence 
  from={startFrame}
  durationInFrames={sceneDuration}  // 跟随音频
>
  <Scene />
  <Audio src={staticFile(audioFile)} />
</Sequence>
```

**经验教训**:
- 视频时长应该跟随音频实际长度
- 不要固定时长，要动态计算
- 每个场景单独配置音频文件

---

### 错误 #5: 语音使用英文而非中文

**症状**:
```
TTS语音: "Memory for AI Agents in 6 lines of code"
问题: 中文观众听不懂
```

**根本原因**:
- 直接使用了数据源的英文summary
- 没有转换为中文解读

**解决方案**:
```python
# 使用中文解读生成TTS
chinese_text = "cognee是一个AI智能体记忆框架，只需6行代码..."
tts.generate(chinese_text, output)
```

**经验教训**:
- 视频目标用户是中文观众
- 必须使用中文生成TTS
- 数据源英文需要翻译成中文解读

---

### 错误 #6: 视频内容字段过多，干扰核心信息

**症状**:
- 显示：平台标签、点赞数、副标题、英文原文、中文解读、URL
- 信息过载，观众无法聚焦核心内容

**根本原因**:
- 没有理解核心需求
- 展示了太多非必要字段

**最终需求确认**:
```
只显示:
✅ 排名
✅ 项目名称（仅视觉）
✅ 中文解读（核心内容）
✅ URL

不显示:
❌ 英文原文
❌ 平台标签（Product Hunt/GitHub）
❌ 点赞数
❌ 副标题
❌ 核心亮点卡片
```

**经验教训**:
- 必须与产品经理确认需求
- 理解观众真正需要的信息
- 少即是多，聚焦核心内容

---

### 错误 #7: 中文内容太短，没有信息量

**症状**:
```
文案: "cognee是一个AI智能体记忆框架。"
字数: 36字
问题: 太简短，观众无法了解产品价值
```

**解决方案**:
```python
# 扩展中文解读（从36字扩展到212字）
extended_text = """
cognee是一个专为AI智能体设计的记忆框架，它的最大特点是极其简洁易用，
开发者只需编写6行代码就能为AI Agent添加完整的长期记忆能力。
这意味着AI可以记住用户的对话历史、个人偏好和上下文信息...
"""
```

**最终字数**:
- 热点1: 212字
- 热点2: 248字  
- 热点3: 235字

**经验教训**:
- 内容要有足够信息量
- 每条约200+字比较合适
- 需要介绍产品功能、价值、应用场景

---

### 错误 #8: 语速不合适

**症状**:
- 1.0倍语速：太慢，视频太长
- 1.2倍语速：适中，但视频还是有点长

**解决方案**:
```python
# 测试不同语速
speed=1.0  # 45秒
speed=1.2  # 35秒  
speed=1.5  # 25-30秒每条

# 最终选择: 1.5倍
# 总时长控制在110秒（约2分钟）
```

**经验教训**:
- 语速影响视频节奏和时长
- 需要根据内容量调整语速
- 1.5倍语速适合中文快速播报

---

## ✅ 正确的开发流程

基于以上错误，总结出正确的视频制作流程：

```
1. 数据获取
   ↓
   从AiTrend获取文章（确保包含summary和metadata）
   ↓
   
2. 文案生成
   ↓
   将英文summary翻译成中文解读（200+字）
   ↓
   
3. TTS生成
   ↓
   使用中文生成TTS（1.5倍语速）
   ↓
   将音频复制到public目录
   ↓
   
4. 视频配置
   ↓
   根据音频时长计算帧数
   ↓
   配置场景：排名 + 项目名称 + 中文解读 + URL
   ↓
   
5. 视频渲染
   ↓
   使用Remotion渲染
   ↓
   
6. 输出
```

---

## 📁 相关文件

- `src/core/deduplicator.py` - 已修复存储逻辑
- `video/src/index-chinese-15x.tsx` - 最终版模板
- `video/scripts/tts_generator.py` - TTS生成工具
- `memory/sent_articles.json` - 数据存储

---

## 🎯 核心经验总结

| 方面 | 经验 |
|------|------|
| **数据** | 必须存储完整信息（summary/metadata） |
| **文案** | 必须使用中文，200+字 |
| **音频** | 必须复制到public目录 |
| **视频** | 时长跟随音频，不固定 |
| **界面** | 只显示核心信息（解读+URL） |
| **语速** | 1.5倍适合中文快速播报 |
| **截图** | 放弃截图，使用卡片设计 |

---

## 📝 后续开发建议

1. **数据源优化**: 修改所有数据源确保存储完整信息
2. **AI翻译**: 使用AI自动将英文summary翻译成中文
3. **文案模板**: 建立标准的中文解读模板
4. **自动化**: 将视频生成流程完全自动化
5. **多语言**: 考虑支持英文版本

---

**记录完成，为后续开发提供参考！** 🦞
