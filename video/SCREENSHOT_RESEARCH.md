# 网站首屏截图自动化方案调研报告

**调研时间**: 2026-02-06  
**调研目的**: 为AiTrend视频自动生成项目网站截图

---

## 方案对比

### 方案1: Playwright (推荐⭐)
**技术**: 微软开源的无头浏览器自动化工具

**优点**:
- ✅ 系统已安装（用于Remotion渲染）
- ✅ 支持Python和Node.js
- ✅ 可截图全页面或特定元素
- ✅ 支持模拟不同设备（手机/桌面）
- ✅ 可设置视口大小、延迟等待
- ✅ 免费、无API限制

**缺点**:
- ⚠️ 需要运行浏览器，资源占用
- ⚠️ 截图速度相对较慢（2-5秒/张）

**实现示例**:
```python
from playwright.sync_api import sync_playwright

def screenshot_website(url, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto(url, wait_until='networkidle')
        page.screenshot(path=output_path, full_page=False)
        browser.close()
```

---

### 方案2: Puppeteer (Node.js)
**技术**: Google Chrome团队开发的Node.js库

**优点**:
- ✅ 与Chrome深度集成
- ✅ 功能丰富，社区活跃
- ✅ 截图质量高

**缺点**:
- ⚠️ 仅支持Node.js（项目主要用Python）
- ⚠️ 需要额外安装

**实现示例**:
```javascript
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('https://example.com');
  await page.screenshot({path: 'screenshot.png'});
  await browser.close();
})();
```

---

### 方案3: Selenium + WebDriver
**技术**: 老牌浏览器自动化工具

**优点**:
- ✅ 支持多种浏览器
- ✅ Python支持好

**缺点**:
- ⚠️ 配置复杂
- ⚠️ 重量级，启动慢
- ⚠️ 截图功能不如Playwright精细

---

### 方案4: 第三方截图API

#### 4.1 Microlink.io
**优点**:
- ✅ HTTP API，简单易用
- ✅ 支持自定义视口、延迟
- ✅ 有免费额度

**缺点**:
- ⚠️ 免费版有限制（100次/天）
- ⚠️ 付费版$9/月起

**实现示例**:
```python
import requests

def screenshot_microlink(url, output_path):
    api_url = f"https://api.microlink.io/?url={url}&screenshot=true&meta=false"
    response = requests.get(api_url)
    data = response.json()
    screenshot_url = data['data']['screenshot']['url']
    # 下载图片...
```

#### 4.2 URL2PNG / Urlbox / ScreenshotAPI
**优点**:
- ✅ 专业截图服务
- ✅ 高可用性

**缺点**:
- ⚠️ 几乎都是付费服务
- ⚠️ 免费额度极少

---

### 方案5: Python专用库

#### 5.1 Pyppeteer
- Puppeteer的Python移植版
- 功能与Puppeteer类似
- 维护不如Playwright活跃

#### 5.2 html2image / imgkit
- 基于wkhtmltoimage
- 截图质量一般
- 不支持现代CSS/JS

---

## 推荐方案

### 🥇 首选: Playwright Python
**理由**:
1. 系统已安装（渲染视频用）
2. Python原生支持，与项目一致
3. 功能强大，可精细控制
4. 免费无限制

### 🥈 备选: Microlink API
**理由**:
1. 如果Playwright资源占用过高
2. 实现简单
3. 但需要考虑免费额度

---

## 技术细节 - Playwright方案

### 安装
```bash
pip install playwright
playwright install chromium
```

### 截图优化
```python
from playwright.sync_api import sync_playwright

def capture_website(url: str, output_path: str, width: int = 1200, height: int = 800):
    """
    捕获网站首屏截图
    
    Args:
        url: 网站URL
        output_path: 输出图片路径
        width: 视口宽度
        height: 视口高度（首屏）
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': width, 'height': height},
            device_scale_factor=2  # 高清截图
        )
        page = context.new_page()
        
        try:
            # 访问网站，等待加载完成
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 可选：等待特定元素出现
            # page.wait_for_selector('main', timeout=5000)
            
            # 截图（只截取首屏）
            page.screenshot(
                path=output_path,
                type='png',
                full_page=False  # 只截取视口
            )
            
            print(f"✅ 截图成功: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return False
            
        finally:
            browser.close()
```

### 批量处理
```python
from concurrent.futures import ThreadPoolExecutor

def batch_screenshots(urls: list, output_dir: str, max_workers: int = 3):
    """批量截图"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, url in enumerate(urls):
            output_path = f"{output_dir}/screenshot_{i}.png"
            future = executor.submit(capture_website, url, output_path)
            futures.append(future)
        
        results = [f.result() for f in futures]
    return results
```

---

## 集成到视频流程

```
视频生成流程（更新版）:
1. selector.py → 精选3-5个热点
2. screenshot_fetcher.py → Playwright截图
   - 读取每个热点的url
   - 生成截图到 assets/screenshots/
3. llm_processor.py → 生成60秒脚本
4. tts_generator.py → speed=1.2生成语音
5. Remotion渲染 → 60秒视频（带截图/Logo）
```

---

## 我的建议

**使用 Playwright Python 方案**:
- 最符合项目技术栈
- 系统已安装，无需额外配置
- 功能完全满足需求
- 免费无限制

**是否需要我**: 
1. 提供完整的Playwright截图实现代码？
2. 先做一个简单的截图测试？

---

**调研完成，等待确认方案！** 🦞
