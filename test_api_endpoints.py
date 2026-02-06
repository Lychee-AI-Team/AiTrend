#!/usr/bin/env python3
"""
测试 ScreenshotAPI.net - 尝试不同的API端点
"""

import os
import requests

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

if not API_KEY:
    print("❌ 未找到 SCREENSHOTAPI_KEY")
    exit(1)

print("=" * 70)
print("📸 测试 ScreenshotAPI.net - 尝试不同端点")
print("=" * 70)

# 测试不同的API端点
endpoints = [
    "https://shot.screenshotapi.net/screenshot",
    "https://api.screenshotapi.net/v1/screenshot",
    "https://api.screenshotapi.net/shot",
    "https://screenshotapi.net/api/v1/screenshot",
    "https://screenshotapi.net/screenshot",
    "https://api.screenshotapi.net/capture",
]

test_url = "https://www.google.com"

print(f"\n测试URL: {test_url}")
print(f"API Key: {API_KEY[:10]}...\n")

for endpoint in endpoints:
    print(f"{'='*70}")
    print(f"尝试端点: {endpoint}")
    print(f"{'='*70}")
    
    try:
        params = {
            "token": API_KEY,
            "url": test_url,
            "width": 1200,
            "height": 800
        }
        
        response = requests.get(endpoint, params=params, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            if 'image' in response.headers.get('content-type', ''):
                print("✅ 成功！返回图片")
                print(f"图片大小: {len(response.content)} bytes")
                # 保存成功案例
                output_path = f'/home/ubuntu/.openclaw/workspace/AiTrend/video/test_screenshots/success_{endpoint.split("/")[-1]}.png'
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"已保存: {output_path}")
                break
            else:
                print(f"返回内容: {response.text[:200]}")
        else:
            print(f"错误: {response.text[:100]}")
            
    except Exception as e:
        print(f"异常: {str(e)}")
    
    print()

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)
