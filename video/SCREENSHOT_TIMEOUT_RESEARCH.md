# 网站截图超时问题调研报告

**问题**: Product Hunt等网站截图超时（30秒）  
**原则**: 不使用降级方案，必须解决根本问题

---

## 问题分析

### 超时场景
```
❌ https://www.producthunt.com/products/molt-beach - Timeout 30000ms
❌ https://www.producthunt.com/products/anthropic-5 - Timeout 30000ms
✅ https://github.com/QwenLM/Qwen3-Coder - 成功
```

### 根本原因

**1. 网站加载策略不同**
- **GitHub**: 页面结构简单，DOM加载快
- **Product Hunt**: 大量JavaScript、动态内容、广告追踪

**2. Playwright默认等待条件太严格**
```python
page.goto(url, wait_until='networkidle')  # 等待所有网络请求完成
```
- Product Hunt有持续的后台请求（analytics、tracking）
- 30秒内无法达到"networkidle"状态

**3. 可能的额外因素**
- CDN资源加载慢
- 第三方脚本阻塞
- 反爬虫机制

---

## 解决方案（不使用降级）

### 方案1：降低等待条件（推荐）

```python
# 不再等待networkidle，只等待DOM加载完成
page.goto(url, wait_until='domcontentloaded', timeout=30000)

# 然后额外等待关键元素出现
page.wait_for_selector('main, [class*="content"], h1', timeout=10000)

# 再等待视觉稳定
page.wait_for_timeout(3000)  # 等待3秒渲染
```

### 方案2：增加超时时间

```python
page.goto(url, wait_until='networkidle', timeout=60000)  # 60秒超时
```

### 方案3：禁用不必要资源

```python
# 阻止图片、CSS、字体加载（纯截图不需要）
page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
```

### 方案4：使用更轻的截图方案

```python
# 直接请求网站缩略图API
# 如: https://screenshotapi.net/ (但需API key，可能违反原则)
```

---

## 建议实施方案

### 最佳方案：组合方案1+2

```python
def capture_website_v2(url: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1200, 'height': 800},
            device_scale_factor=2
        )
        page = context.new_page()
        
        try:
            # 1. 先尝试domcontentloaded（更快）
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 2. 等待关键内容元素
            try:
                page.wait_for_selector('main, article, [class*="content"], h1', timeout=10000)
            except:
                pass  # 元素不存在也继续
            
            # 3. 等待视觉稳定（给JS渲染时间）
            page.wait_for_timeout(5000)  # 5秒
            
            # 4. 截图
            page.screenshot(path=output_path, full_page=False)
            
            return True
            
        except Exception as e:
            # 如果还是失败，尝试60秒超时
            try:
                page.goto(url, wait_until='load', timeout=60000)
                page.wait_for_timeout(3000)
                page.screenshot(path=output_path, full_page=False)
                return True
            except:
                return False
        finally:
            browser.close()
```

---

## 下一步

请确认是否使用**方案1（降低等待条件）**重新截图？

或者需要我：
1. 修改screenshot_fetcher.py实现新方案
2. 重新对3个真实URL截图
3. 验证截图质量

**不使用任何降级方案，必须真实截图成功！** 🦞
