#!/usr/bin/env python3
"""
测试 ScreenshotAPI.net 截图功能
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

if not API_KEY:
    print("❌ 未找到 SCREENSHOTAPI_KEY")
    exit(1)

print("=" * 70)
print("📸 测试 ScreenshotAPI.net 截图功能")
print("=" * 70)

# 测试网站列表
test_urls = [
    {
        "name": "Product Hunt - ClawApp",
        "url": "https://www.producthunt.com/products/clawapp",
        "filename": "test_producthunt_clawapp.png"
    },
    {
        "name": "GitHub - Qwen3-Coder",
        "url": "https://github.com/QwenLM/Qwen3-Coder",
        "filename": "test_github_qwen3.png"
    },
    {
        "name": "Google",
        "url": "https://www.google.com",
        "filename": "test_google.png"
    }
]

output_dir = '/home/ubuntu/.openclaw/workspace/AiTrend/video/test_screenshots'
os.makedirs(output_dir, exist_ok=True)

print(f"\nAPI Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print(f"输出目录: {output_dir}\n")

results = []

for i, site in enumerate(test_urls, 1):
    print(f"{'='*70}")
    print(f"测试 #{i}: {site['name']}")
    print(f"URL: {site['url']}")
    print(f"{'='*70}")
    
    try:
        # 调用 ScreenshotAPI.net
        api_url = "https://api.screenshotapi.net/screenshot"
        params = {
            "token": API_KEY,
            "url": site['url'],
            "width": 1200,
            "height": 800,
            "fresh": "true",
            "full_page": "false"
        }
        
        print(f"调用API: {api_url}")
        print(f"参数: {json.dumps(params, indent=2)}")
        
        response = requests.get(api_url, params=params, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查返回的是图片还是错误信息
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            if 'image' in content_type:
                # 保存截图
                output_path = os.path.join(output_dir, site['filename'])
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / 1024
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
                # 可能是错误信息
                print(f"⚠️ 返回的不是图片")
                print(f"响应内容: {response.text[:200]}")
                results.append({
                    'name': site['name'],
                    'status': 'error',
                    'error': 'Not an image'
                })
        else:
            print(f"❌ API调用失败")
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
    else:
        print(f"   错误: {r.get('error', 'Unknown')}")

print(f"\n截图保存在: {output_dir}/")

# 检查是否有成功的截图
if success_count > 0:
    print("\n✅ 至少有一个网站截图成功！")
else:
    print("\n❌ 所有测试都失败了")
