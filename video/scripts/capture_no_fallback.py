#!/usr/bin/env python3
"""
截图超时解决方案 - 不使用降级方案
使用更宽松的加载条件和重试机制
"""

import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from playwright.sync_api import sync_playwright


def capture_with_retry(url: str, output_path: str, max_retries: int = 2) -> bool:
    """
    截图 - 使用更宽松的加载条件
    
    策略:
    1. 先尝试domcontentloaded（不等待所有网络请求）
    2. 等待关键元素出现
    3. 给JS渲染时间
    4. 如果失败，尝试60秒超时
    """
    
    for attempt in range(max_retries):
        print(f"  尝试 {attempt + 1}/{max_retries}: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1200, 'height': 800},
                    device_scale_factor=2
                )
                page = context.new_page()
                
                try:
                    if attempt == 0:
                        # 第一次尝试：快速加载
                        print("    策略1: domcontentloaded + 关键元素等待")
                        page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        
                        # 等待关键内容元素
                        try:
                            page.wait_for_selector('main, article, [class*="content"], h1, .product-header', timeout=10000)
                            print("    关键元素已加载")
                        except:
                            print("    关键元素未找到，继续...")
                        
                        # 等待JS渲染
                        page.wait_for_timeout(5000)  # 5秒
                        
                    else:
                        # 第二次尝试：更长的超时
                        print("    策略2: 60秒超时 + load事件")
                        page.goto(url, wait_until='load', timeout=60000)
                        page.wait_for_timeout(3000)
                    
                    # 截图
                    page.screenshot(path=output_path, full_page=False)
                    print(f"    ✅ 截图成功: {output_path}")
                    return True
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            print(f"    ❌ 失败: {str(e)[:100]}")
            if attempt < max_retries - 1:
                print("    准备重试...")
            else:
                print(f"    所有{max_retries}次尝试均失败")
                return False
    
    return False


def main():
    # 真实AI热点URL（今天推送到Discord的）
    hotspots = [
        {
            "id": 1,
            "url": "https://www.producthunt.com/products/molt-beach",
            "title": "Molt Beach",
            "output": "/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_1.png"
        },
        {
            "id": 2,
            "url": "https://www.producthunt.com/products/anthropic-5",
            "title": "Claude Opus 4.6",
            "output": "/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_2.png"
        },
        {
            "id": 3,
            "url": "https://github.com/QwenLM/Qwen3-Coder",
            "title": "Qwen3-Coder",
            "output": "/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_3_v2.png"
        }
    ]
    
    print("=" * 60)
    print("🌐 重新截图 - 使用新策略（无降级方案）")
    print("=" * 60)
    
    success_count = 0
    
    for hotspot in hotspots:
        print(f"\n📸 {hotspot['title']}")
        print(f"   URL: {hotspot['url']}")
        
        if capture_with_retry(hotspot['url'], hotspot['output']):
            success_count += 1
        else:
            print(f"   ⚠️ 截图失败，需要进一步调研其他方案")
    
    print("\n" + "=" * 60)
    print(f"📊 结果: {success_count}/{len(hotspots)} 成功")
    print("=" * 60)


if __name__ == '__main__':
    main()
