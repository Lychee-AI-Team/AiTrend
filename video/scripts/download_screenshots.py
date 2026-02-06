#!/usr/bin/env python3
"""
下载截图用于视频制作
"""

import os
import requests
import json

# 读取API Key
env_path = '/home/ubuntu/.openclaw/workspace/AiTrend/.env'
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#') and not line.strip().startswith('TWITTER'):
                try:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
                except:
                    pass

API_KEY = env_vars.get('SCREENSHOTAPI_KEY', '')
API_ENDPOINT = "https://shot.screenshotapi.net/screenshot"

if not API_KEY:
    print("❌ 未找到 SCREENSHOTAPI_KEY")
    exit(1)

# 热点网站列表
hotspots = [
    {
        "rank": 1,
        "name": "cognee",
        "url": "https://github.com/topoteretes/cognee",
        "filename": "screenshots/hotspot_1.png"
    },
    {
        "rank": 2,
        "name": "anthropics/skills",
        "url": "https://github.com/anthropics/skills",
        "filename": "screenshots/hotspot_2.png"
    },
    {
        "rank": 3,
        "name": "PentestAgent",
        "url": "https://github.com/GH05TCREW/pentestagent",
        "filename": "screenshots/hotspot_3.png"
    }
]

output_dir = '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public'
os.makedirs(os.path.join(output_dir, 'screenshots'), exist_ok=True)

print("=" * 70)
print("📸 下载视频截图")
print("=" * 70)

for hotspot in hotspots:
    print(f"\n{'='*70}")
    print(f"热点 #{hotspot['rank']}: {hotspot['name']}")
    print(f"URL: {hotspot['url']}")
    print(f"{'='*70}")
    
    try:
        # 调用API
        params = {
            "token": API_KEY,
            "url": hotspot['url'],
            "width": 1200,
            "height": 800,
            "fresh": "true"
        }
        
        print("调用 ScreenshotAPI.net...")
        response = requests.get(API_ENDPOINT, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            screenshot_url = data.get('screenshot', '')
            
            if screenshot_url:
                # 下载图片
                print(f"下载截图...")
                img_response = requests.get(screenshot_url, timeout=60)
                
                if img_response.status_code == 200:
                    output_path = os.path.join(output_dir, hotspot['filename'])
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    file_size = len(img_response.content) / 1024
                    print(f"✅ 截图成功!")
                    print(f"文件大小: {file_size:.1f} KB")
                    print(f"保存路径: {output_path}")
                else:
                    print(f"❌ 下载失败: HTTP {img_response.status_code}")
            else:
                print(f"❌ API未返回截图URL")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

print("\n" + "=" * 70)
print("✅ 截图下载完成!")
print("=" * 70)
