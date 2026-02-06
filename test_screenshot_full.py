#!/usr/bin/env python3
"""
测试 ScreenshotAPI.net - 完整流程
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

print("=" * 70)
print("📸 测试 ScreenshotAPI.net - 完整截图流程")
print("=" * 70)

# 测试网站列表
test_urls = [
    {
        "name": "Product Hunt - ClawApp",
        "url": "https://www.producthunt.com/products/clawapp",
        "filename": "screenshot_producthunt_clawapp.png"
    },
    {
        "name": "GitHub - Qwen3-Coder",
        "url": "https://github.com/QwenLM/Qwen3-Coder",
        "filename": "screenshot_github_qwen3.png"
    },
    {
        "name": "Google",
        "url": "https://www.google.com",
        "filename": "screenshot_google.png"
    }
]

output_dir = '/home/ubuntu/.openclaw/workspace/AiTrend/video/test_screenshots'
os.makedirs(output_dir, exist_ok=True)

print(f"\nAPI端点: {API_ENDPOINT}")
print(f"输出目录: {output_dir}\n")

results = []

for i, site in enumerate(test_urls, 1):
    print(f"{'='*70}")
    print(f"测试 #{i}: {site['name']}")
    print(f"URL: {site['url']}")
    print(f"{'='*70}")
    
    try:
        # 第1步：调用API获取截图URL
        params = {
            "token": API_KEY,
            "url": site['url'],
            "width": 1200,
            "height": 800,
            "fresh": "true",
            "output": "json"  # 返回JSON格式
        }
        
        print(f"调用API...")
        response = requests.get(API_ENDPOINT, params=params, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            screenshot_url = data.get('screenshot', '')
            
            print(f"截图URL: {screenshot_url[:80]}...")
            
            if screenshot_url:
                # 第2步：下载截图
                print(f"下载截图...")
                img_response = requests.get(screenshot_url, timeout=60)
                
                if img_response.status_code == 200:
                    output_path = os.path.join(output_dir, site['filename'])
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    file_size = len(img_response.content) / 1024
                    print(f"✅ 截图成功!")
                    print(f"文件大小: {file_size:.1f} KB")
                    print(f"保存路径: {output_path}")
                    
                    results.append({
                        'name': site['name'],
                        'status': 'success',
                        'size_kb': file_size,
                        'path': output_path
                    })
                else:
                    print(f"❌ 下载截图失败: HTTP {img_response.status_code}")
                    results.append({
                        'name': site['name'],
                        'status': 'error',
                        'error': f'Download failed: {img_response.status_code}'
                    })
            else:
                print(f"❌ API未返回截图URL")
                print(f"响应: {json.dumps(data, indent=2)}")
                results.append({
                    'name': site['name'],
                    'status': 'error',
                    'error': 'No screenshot URL in response'
                })
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            results.append({
                'name': site['name'],
                'status': 'error',
                'error': f'HTTP {response.status_code}'
            })
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        results.append({
            'name': site['name'],
            'status': 'error',
            'error': str(e)
        })
    
    print()

# 总结
print("=" * 70)
print("📊 测试结果总结")
print("=" * 70)

success_count = sum(1 for r in results if r['status'] == 'success')
print(f"\n成功率: {success_count}/{len(test_urls)}")

for r in results:
    status_icon = "✅" if r['status'] == 'success' else "❌"
    print(f"\n{status_icon} {r['name']}")
    if r['status'] == 'success':
        print(f"   大小: {r['size_kb']:.1f} KB")
        print(f"   路径: {r['path']}")
    else:
        print(f"   错误: {r.get('error', 'Unknown')}")

print(f"\n{'='*70}")
if success_count > 0:
    print("✅ ScreenshotAPI.net 可用！截图成功！")
    print(f"\n使用方法:")
    print(f"API端点: {API_ENDPOINT}")
    print(f"参数: token={API_KEY[:10]}..., url=目标网址")
    print(f"返回: JSON包含screenshot字段（S3图片URL）")
else:
    print("❌ 所有测试都失败了")
print(f"{'='*70}")
