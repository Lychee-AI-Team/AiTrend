#!/usr/bin/env python3
"""
截图增强版 - 绕过Cloudflare检测
"""

import os
from playwright.sync_api import sync_playwright


def capture_with_bypass(url: str, output_path: str) -> bool:
    """
    截图 - 绕过Cloudflare和反爬虫
    
    策略:
    1. 使用真实User-Agent
    2. 禁用自动化检测
    3. 添加额外Headers
    4. 延长等待时间
    """
    
    try:
        with sync_playwright() as p:
            # 启动浏览器（禁用自动化检测）
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # 创建上下文（模拟真实用户）
            context = browser.new_context(
                viewport={'width': 1200, 'height': 800},
                device_scale_factor=2,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Referer': 'https://www.google.com/'
                }
            )
            
            page = context.new_page()
            
            # 访问网站
            print(f"  访问: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 等待页面稳定（让Cloudflare验证完成）
            print(f"  等待页面稳定...")
            page.wait_for_timeout(8000)  # 8秒
            
            # 检查是否有Cloudflare验证
            page_content = page.content()
            if 'cloudflare' in page_content.lower() or 'checking your browser' in page_content.lower():
                print(f"  ⚠️  检测到Cloudflare，延长等待...")
                page.wait_for_timeout(10000)  # 额外10秒
            
            # 截图
            page.screenshot(path=output_path, full_page=False)
            print(f"  ✅ 截图成功: {output_path}")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False


def main():
    """重新截图所有网站"""
    
    screenshots = [
        {
            'url': 'https://www.producthunt.com/products/molt-beach',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_1.png',
            'name': 'Molt Beach'
        },
        {
            'url': 'https://www.producthunt.com/products/anthropic-5',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_2.png',
            'name': 'Claude Opus 4.6'
        },
        {
            'url': 'https://github.com/QwenLM/Qwen3-Coder',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_3.png',
            'name': 'Qwen3-Coder'
        }
    ]
    
    print("=" * 60)
    print("🌐 增强版截图 - 绕过Cloudflare")
    print("=" * 60)
    
    success = 0
    for item in screenshots:
        print(f"\n📸 {item['name']}")
        if capture_with_bypass(item['url'], item['output']):
            success += 1
    
    print(f"\n{'='*60}")
    print(f"📊 结果: {success}/{len(screenshots)} 成功")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
