# 问题诊断与解决方案

## 问题1: 音频连接错误（从第二个场景开始）

### 可能原因
1. **音频文件路径错误** - 模板中使用了错误的audioFile路径
2. **文件不存在** - 某些音频文件缺失
3. **Audio组件问题** - 多个Audio组件同时存在冲突

### 解决方案

#### 检查1: 确认音频文件存在
```bash
ls -la video/assets/audio/2026-02-06/
```

#### 检查2: 确认模板中使用正确的文件名
当前模板使用:
- `audio/2026-02-06/hotspot_1.mp3` ✅ 存在 (106K)
- `audio/2026-02-06/hotspot_2.mp3` ✅ 存在 (126K)
- `audio/2026-02-06/hotspot_3.mp3` ✅ 存在 (126K)

文件都存在，问题可能是：

#### 解决方案A: 禁用音频先测试画面
```typescript
// 临时注释掉Audio组件
{/* {scene.audioFile && <Audio src={staticFile(scene.audioFile)} />} */}
```

#### 解决方案B: 使用单一音频文件（避免多音轨）
将所有语音合并为一个60秒的音频文件：
```bash
ffmpeg -i "concat:opening.mp3|hotspot_1.mp3|hotspot_2.mp3|hotspot_3.mp3|closing.mp3" -acodec copy output.mp3
```

---

## 问题2: Cloudflare拦截截图

### 症状
- 截图显示Cloudflare验证页面
- 或截图内容为"Checking your browser..."

### 原因
Cloudflare检测到自动化工具（Playwright），触发反爬虫保护。

### 解决方案（按优先级）

#### 方案1: 添加User-Agent和Headers（推荐）
```python
context = browser.new_context(
    viewport={'width': 1200, 'height': 800},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    extra_http_headers={
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
)
```

#### 方案2: 禁用自动化检测
```python
browser = p.chromium.launch(
    headless=True,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
    ]
)
```

#### 方案3: 使用更长的延迟（让Cloudflare验证完成）
```python
page.goto(url, wait_until='networkidle')
page.wait_for_timeout(10000)  # 等待10秒让验证完成
```

#### 方案4: 使用第三方截图服务（绕过Cloudflare）
- https://screenshotapi.net/
- https://www.screenshotapi.io/

#### 方案5: 使用网站缩略图API（不需要截图）
```python
# Google PageSpeed Insights API
thumbnail_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&screenshot=true"
```

---

## 立即执行方案

### 1. 修复音频问题
```bash
# 合并所有音频为一个文件
cd video/assets/audio/2026-02-06
ffmpeg -i "concat:opening.mp3|hotspot_1.mp3|hotspot_2.mp3|hotspot_3.mp3|closing.mp3" -acodec copy full_audio.mp3
```

然后在模板中只使用一个Audio组件：
```typescript
<Audio src={staticFile('audio/2026-02-06/full_audio.mp3')} />
```

### 2. 修复Cloudflare截图问题
```python
# 使用增强版截图脚本
def capture_with_cloudflare_bypass(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(8000)  # 等待Cloudflare验证
        
        page.screenshot(path=output_path)
```

---

**请确认先解决哪个问题？** 还是同时解决？🦞
