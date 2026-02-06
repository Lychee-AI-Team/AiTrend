# Remotion Studio 版本列表

## 当前运行中

### 竖屏版本 (端口: 3003)
**访问**: http://localhost:3003
- 文件: `index-vertical.tsx`
- 分辨率: 1080x1920 (9:16)
- 特色: AI厂商Logo、手机适配
- 状态: ✅ 运行中

---

## 可启动的其他版本

### 1. 横屏完整版
**文件**: `index.tsx`
- 分辨率: 1920x1080 (16:9)
- 特色: 完整DailyNews组件
- 问题: 可能有黑屏问题

### 2. 最小化测试版
**文件**: `test-minimal.tsx`
- 分辨率: 1920x1080
- 特色: 最简单的红底白字
- 用途: 验证基础渲染是否正常

### 3. 真实组件测试版
**文件**: `test-real-components.tsx`
- 分辨率: 1920x1080
- 特色: 真实Opening/DetailedHotspot组件，无Audio
- 用途: 诊断黑屏问题

### 4. 中文测试版
**文件**: `test-chinese.tsx`
- 分辨率: 1920x1080
- 特色: 专门测试中文显示

### 5. 横屏内联数据版
**文件**: `index-inline.tsx`
- 分辨率: 1920x1080
- 特色: 数据硬编码，无fs依赖

---

## 启动命令

```bash
cd AiTrend/video/src

# 横屏完整版
npx remotion studio index.tsx --port=3000

# 最小化测试
npx remotion studio test-minimal.tsx --port=3001

# 真实组件测试
npx remotion studio test-real-components.tsx --port=3002

# 中文测试
npx remotion studio test-chinese.tsx --port=3004

# 内联数据版
npx remotion studio index-inline.tsx --port=3005
```

---

**需要启动哪个版本供对比观察？**
