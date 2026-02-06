#!/usr/bin/env python3
"""
获取网站Open Graph图片 - 绕过Cloudflare截图
"""

import requests
from bs4 import BeautifulSoup
import os

def get_og_image(url: str) -> str:
    """
    获取网站的Open Graph图片URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 查找 og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image.get('content')
        
        # 2. 查找 twitter:image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image.get('content')
        
        # 3. 查找 twitter:image:src (旧版)
        twitter_image_src = soup.find('meta', attrs={'name': 'twitter:image:src'})
        if twitter_image_src and twitter_image_src.get('content'):
            return twitter_image_src.get('content')
        
        return None
        
    except Exception as e:
        print(f"  获取失败: {e}")
        return None


def download_image(url: str, output_path: str) -> bool:
    """
    下载图片
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
        
    except Exception as e:
        print(f"  下载失败: {e}")
        return False


def main():
    """获取所有网站的Open Graph图片"""
    
    websites = [
        {
            'name': 'Molt Beach',
            'url': 'https://www.producthunt.com/products/molt-beach',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_1.png'
        },
        {
            'name': 'Claude Opus 4.6',
            'url': 'https://www.producthunt.com/products/anthropic-5',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_2.png'
        },
        {
            'name': 'Qwen3-Coder',
            'url': 'https://github.com/QwenLM/Qwen3-Coder',
            'output': '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots/hotspot_3.png'
        }
    ]
    
    print("=" * 70)
    print("🌐 获取网站Open Graph图片（绕过Cloudflare）")
    print("=" * 70)
    
    success_count = 0
    
    for site in websites:
        print(f"\n📸 {site['name']}")
        print(f"   URL: {site['url']}")
        
        # 获取图片URL
        image_url = get_og_image(site['url'])
        
        if image_url:
            print(f"   🖼️  找到图片: {image_url[:80]}...")
            
            # 下载图片
            if download_image(image_url, site['output']):
                file_size = os.path.getsize(site['output']) / 1024
                print(f"   ✅ 下载成功: {file_size:.1f}KB")
                success_count += 1
            else:
                print(f"   ❌ 下载失败")
        else:
            print(f"   ⚠️  未找到Open Graph图片")
    
    print(f"\n{'='*70}")
    print(f"📊 结果: {success_count}/{len(websites)} 成功")
    print(f"{'='*70}")
    
    return success_count == len(websites)


if __name__ == '__main__':
    main()
