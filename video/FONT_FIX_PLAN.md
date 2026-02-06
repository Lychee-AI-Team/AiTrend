# 视频中文显示问题修复方案

**问题根因**: 系统中缺少中文字体，导致中文显示为方框/空白  
**解决方案**: 安装中文字体 + 指定字体路径

---

## 一、问题确认

### 当前情况
- ✅ Remotion渲染正常（有画面）
- ✅ 视频生成成功
- ❌ 中文显示为方框/空白（字体缺失）

### 根本原因
系统只安装了英文字体，没有中文字体：
- DejaVu Sans（英文）
- Liberation Sans（英文）
- 缺少：Noto Sans CJK、思源黑体、微软雅黑等中文字体

---

## 二、解决方案

### 方案1: 安装系统级中文字体（推荐）

```bash
# 安装 Google Noto 中文字体
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk

# 或安装思源黑体
sudo apt-get install -y fonts-noto-cjk fonts-noto-color-emoji
```

### 方案2: 使用本地字体文件

1. 下载中文字体文件（如 NotoSansSC-Regular.otf）
2. 放入 `video/assets/fonts/` 目录
3. Remotion组件中使用绝对路径引用

### 方案3: 使用图片代替文字（保底）

将文字渲染为图片，然后合成视频：
```python
from PIL import Image, ImageDraw, ImageFont
# 生成文字图片
```

### 方案4: 使用 MoviePy（保底）

MoviePy可以更好地处理字体：
```python
from moviepy.editor import TextClip
# 指定字体文件路径
```

---

## 三、实施计划

### 步骤1: 安装中文字体
```bash
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
```

### 步骤2: 验证字体安装
```bash
fc-list :lang=zh | head -10
```

### 步骤3: 更新 Remotion 组件
修改字体设置为中文字体：
```typescript
fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif'
```

### 步骤4: 重新渲染视频

---

## 四、字体备选方案

如果系统安装失败，使用本地字体：

1. 下载字体：
   ```bash
   wget https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf
   ```

2. Remotion中使用：
   ```typescript
   // 通过CSS @font-face引入
   ```

---

**立即开始执行方案1...**
