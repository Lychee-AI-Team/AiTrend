#!/usr/bin/env python3
"""
网站截图抓取器
使用Playwright自动化截图
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend')


class ScreenshotFetcher:
    """网站截图抓取器"""
    
    def __init__(self, output_dir: str = None, max_workers: int = 3):
        """
        初始化截图器
        
        Args:
            output_dir: 截图输出目录
            max_workers: 并发截图数量
        """
        self.output_dir = output_dir or '/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/screenshots'
        self.max_workers = max_workers
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 检查playwright是否安装
        try:
            from playwright.sync_api import sync_playwright
            self.playwright_available = True
        except ImportError:
            print("⚠️  Playwright未安装，正在安装...")
            os.system("pip3 install playwright --break-system-packages -q")
            os.system("playwright install chromium")
            self.playwright_available = True
    
    def capture(self, url: str, filename: str, width: int = 1200, height: int = 800) -> Optional[str]:
        """
        捕获单个网站截图
        
        Args:
            url: 网站URL
            filename: 输出文件名（不含扩展名）
            width: 视口宽度
            height: 视口高度
            
        Returns:
            截图文件路径，失败返回None
        """
        from playwright.sync_api import sync_playwright
        
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': width, 'height': height},
                    device_scale_factor=2  # 高清截图
                )
                page = context.new_page()
                
                # 访问网站
                print(f"📸 正在截图: {url}")
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 等待页面稳定
                page.wait_for_timeout(2000)  # 额外等待2秒
                
                # 截图
                page.screenshot(
                    path=output_path,
                    type='png',
                    full_page=False  # 只截取首屏
                )
                
                browser.close()
                print(f"✅ 截图成功: {output_path}")
                return output_path
                
        except Exception as e:
            print(f"❌ 截图失败 {url}: {e}")
            return None
    
    def capture_batch(self, hotspots: List[Dict]) -> Dict[str, str]:
        """
        批量截图热点网站
        
        Args:
            hotspots: 热点列表，每个包含url和id
            
        Returns:
            映射 {hotspot_id: screenshot_path}
        """
        results = {}
        
        print(f"\n🌐 开始批量截图，共 {len(hotspots)} 个网站...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_hotspot = {}
            for hotspot in hotspots:
                url = hotspot.get('url')
                hotspot_id = hotspot.get('id') or hotspot.get('rank')
                
                if not url:
                    continue
                    
                future = executor.submit(
                    self.capture, 
                    url, 
                    f"hotspot_{hotspot_id}",
                    1200,  # 宽度
                    800    # 高度（首屏）
                )
                future_to_hotspot[future] = hotspot
            
            # 收集结果
            for future in as_completed(future_to_hotspot):
                hotspot = future_to_hotspot[future]
                hotspot_id = hotspot.get('id') or hotspot.get('rank')
                
                try:
                    path = future.result()
                    if path:
                        results[hotspot_id] = path
                except Exception as e:
                    print(f"❌ 热点 {hotspot_id} 截图异常: {e}")
        
        print(f"\n📊 截图完成: {len(results)}/{len(hotspots)} 成功")
        return results
    
    def generate_fallback_logos(self, hotspots: List[Dict], screenshot_results: Dict[str, str]):
        """
        为截图失败的热点生成Logo占位信息
        
        Args:
            hotspots: 热点列表
            screenshot_results: 截图结果
            
        Returns:
            更新后的热点列表，包含screenshot字段
        """
        for hotspot in hotspots:
            hotspot_id = hotspot.get('id') or hotspot.get('rank')
            
            if hotspot_id in screenshot_results:
                # 使用截图
                filename = os.path.basename(screenshot_results[hotspot_id])
                hotspot['screenshot'] = f"screenshots/{filename}"
                hotspot['use_screenshot'] = True
            else:
                # 使用Logo fallback
                vendor = self._infer_vendor(hotspot)
                hotspot['logo'] = f"logos/{vendor}.svg"
                hotspot['use_screenshot'] = False
        
        return hotspots
    
    def _infer_vendor(self, hotspot: Dict) -> str:
        """从热点信息推断厂商"""
        title = hotspot.get('title', '').lower()
        source = hotspot.get('source', '').lower()
        
        vendor_map = {
            'openai': 'openai',
            'gpt': 'openai',
            'chatgpt': 'openai',
            'meta': 'meta',
            'llama': 'meta',
            'facebook': 'meta',
            'google': 'google',
            'deepmind': 'deepmind',
            'gemini': 'google',
            'anthropic': 'anthropic',
            'claude': 'anthropic',
            'microsoft': 'microsoft',
            'azure': 'microsoft',
            'amazon': 'amazon',
            'aws': 'amazon',
        }
        
        text = f"{title} {source}"
        for keyword, vendor in vendor_map.items():
            if keyword in text:
                return vendor
        
        return 'default'


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='网站截图抓取器')
    parser.add_argument('--input', '-i', required=True, help='热点JSON文件')
    parser.add_argument('--output', '-o', help='输出目录')
    parser.add_argument('--workers', '-w', type=int, default=3, help='并发数')
    
    args = parser.parse_args()
    
    # 加载热点数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hotspots = data.get('hotspots', [])
    
    # 初始化截图器
    fetcher = ScreenshotFetcher(output_dir=args.output, max_workers=args.workers)
    
    # 批量截图
    results = fetcher.capture_batch(hotspots)
    
    # 生成fallback
    updated_hotspots = fetcher.generate_fallback_logos(hotspots, results)
    
    # 保存结果
    data['hotspots'] = updated_hotspots
    data['screenshot_results'] = {
        'successful': len(results),
        'failed': len(hotspots) - len(results),
        'paths': results
    }
    
    with open(args.input, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {args.input}")


if __name__ == '__main__':
    main()
