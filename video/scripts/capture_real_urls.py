#!/usr/bin/env python3
"""
真实URL截图 - 使用今天AI热点的真实URL
"""

import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from screenshot_fetcher import ScreenshotFetcher

# 今天真实的AI热点URL
hotspots = [
    {
        "id": 1,
        "url": "https://www.producthunt.com/products/molt-beach",
        "title": "Molt Beach"
    },
    {
        "id": 2,
        "url": "https://www.producthunt.com/products/anthropic-5",
        "title": "Claude Opus 4.6"
    },
    {
        "id": 3,
        "url": "https://github.com/QwenLM/Qwen3-Coder",
        "title": "Qwen3-Coder"
    }
]

output_dir = '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots'

print("=" * 60)
print("🌐 对真实AI热点URL截图")
print("=" * 60)
print("\n目标网站:")
for h in hotspots:
    print(f"  {h['id']}. {h['title']}")
    print(f"     URL: {h['url']}")
print()

fetcher = ScreenshotFetcher(output_dir=output_dir, max_workers=3)
results = fetcher.capture_batch(hotspots)

print("\n" + "=" * 60)
print("📊 截图结果")
print("=" * 60)

for hotspot_id, path in results.items():
    print(f"✅ 热点 {hotspot_id}: {path}")
    # 重命名为标准格式
    new_path = os.path.join(output_dir, f'hotspot_{hotspot_id}.png')
    if path != new_path and os.path.exists(path):
        os.rename(path, new_path)
        print(f"   重命名为: {new_path}")

print(f"\n总计: {len(results)}/{len(hotspots)} 个网站截图成功")
