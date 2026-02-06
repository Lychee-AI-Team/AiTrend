# 视频黑屏问题系统性调研方案

**问题**: Remotion渲染的视频显示为纯黑屏  
**目标**: 找到根本原因并制定保底方案

---

## 一、问题现象分析

### 当前情况
- ✅ 渲染过程完成（Rendered 6300/6300）
- ✅ 视频文件生成（8.7MB）
- ✅ 时长正确（3分30秒）
- ❌ 画面纯黑，无内容显示
- ❌ 音频情况待确认

### 可能原因清单

#### A. 渲染输出问题
- [ ] 组件返回null或空内容
- [ ] CSS背景色覆盖内容
- [ ] 字体加载失败导致文字不可见
- [ ] 动画初始状态问题

#### B. 资源加载问题
- [ ] 音频文件路径错误导致渲染阻塞
- [ ] 字体文件缺失
- [ ] 图片/资源404

#### C. 环境问题
- [ ] Chromium无头模式兼容性问题
- [ ] GPU加速问题
- [ ] 内存不足导致渲染失败

#### D. 代码逻辑问题
- [ ] 条件渲染错误
- [ ] props传递失败
- [ ] 异步数据加载问题

---

## 二、AB测试方案

### 测试A：最简化版本（保底方案）
**目标**: 验证Remotion基础渲染是否正常

```tsx
// test-minimal.tsx
import React from 'react';
import {Composition, registerRoot} from 'remotion';

const MinimalVideo = () => (
  <div style={{
    width: 1920,
    height: 1080,
    backgroundColor: '#ff0000', // 红色背景
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }}>
    <h1 style={{color: '#ffffff', fontSize: 100}}>TEST</h1>
  </div>
);

registerRoot(() => (
  <Composition
    id="Minimal"
    component={MinimalVideo}
    durationInFrames={30}
    fps={30}
    width={1920}
    height={1080}
  />
));
```

### 测试B：无音频版本
**目标**: 排除音频加载问题

```tsx
// 复制 DailyNews.tsx，移除所有 Audio 组件
// 只保留视觉组件
```

### 测试C：静态文本版本
**目标**: 排除动画和动态效果问题

```tsx
// 纯静态内容，无动画，无useCurrentFrame
```

### 测试D：单场景版本
**目标**: 排除Sequence多场景问题

```tsx
// 只渲染一个场景，不切换
```

### 测试E：不同浏览器引擎
**目标**: 排除Chromium兼容性问题

```bash
# 测试1: Playwright Chromium
npx remotion render ... --browser-executable=~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome

# 测试2: 系统Chromium
npx remotion render ... --browser-executable=/usr/bin/chromium-browser

# 测试3: Headless Shell
npx remotion render ... --browser-executable=~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell
```

### 测试F：不同分辨率和帧率
**目标**: 排除分辨率/性能问题

```tsx
// 720p @30fps
width: 1280, height: 720

// 480p @30fps
width: 640, height: 480
```

---

## 三、诊断检查清单

### 1. 组件输出检查
```typescript
// 在组件中添加日志
const VideoComponent = () => {
  console.log("Component rendering");
  console.log("Props:", props);
  
  return (
    <div>
      {console.log("Returning JSX")}
      ...
    </div>
  );
};
```

### 2. 样式检查
```typescript
// 确保没有z-index问题
// 确保背景色不是纯黑
// 确保文字颜色可见
```

### 3. 资源加载检查
```bash
# 检查音频文件是否存在
ls -la video/src/public/audio/2026-02-06/

# 检查文件权限
file video/src/public/audio/2026-02-06/*.mp3
```

### 4. Remotion调试
```bash
# 启用详细日志
DEBUG=remotion* npx remotion render ...

# 使用预览模式检查
npx remotion preview
```

---

## 四、保底方案

### 方案1: 纯静态图片序列
如果Remotion组件渲染有问题，改用：
1. Python生成每一帧的图片（PIL/Pillow）
2. 使用FFmpeg将图片序列合成视频
3. 使用moviepy添加音频

### 方案2: MoviePy完全替代
完全使用Python的moviepy库：
```python
from moviepy.editor import *

# 创建视频片段
clips = []
for scene in scenes:
    # 生成文本clip
    txt_clip = TextClip(scene['text'], fontsize=70, color='white', size=(1920,1080))
    txt_clip = txt_clip.set_duration(scene['duration'])
    clips.append(txt_clip)

# 合并
video = concatenate_videoclips(clips)
video = video.set_audio(AudioFileClip("audio.mp3"))
video.write_videofile("output.mp4", fps=30)
```

### 方案3: 使用FFmpeg直接合成
```bash
# 生成测试视频
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 -pix_fmt yuv420p test.mp4

# 添加音频
ffmpeg -i test.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
```

---

## 五、执行计划

### 阶段1: 基础验证（10分钟）
1. ✅ 运行测试A（最简化版本）
2. 检查结果：是否正常显示红色背景和TEST文字

### 阶段2: 逐步增加复杂度（20分钟）
1. 测试B（无音频版DailyNews）
2. 测试C（静态版）
3. 测试D（单场景版）

### 阶段3: 环境测试（10分钟）
1. 测试E（不同浏览器引擎）
2. 测试F（不同分辨率）

### 阶段4: 实施保底方案（如果需要）
1. 选择并实施最佳保底方案
2. 验证输出质量

---

## 六、预期结果

| 测试 | 预期 | 实际 | 结论 |
|------|------|------|------|
| 测试A | 红色背景+TEST文字 | ? | ? |
| 测试B | DailyNews无音频 | ? | ? |
| 测试C | 纯静态内容 | ? | ? |
| 测试D | 单场景正常 | ? | ? |
| 测试E | 不同引擎 | ? | ? |
| 测试F | 不同分辨率 | ? | ? |

---

**开始执行AB测试...**
