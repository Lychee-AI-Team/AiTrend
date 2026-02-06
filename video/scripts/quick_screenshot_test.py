#!/usr/bin/env python3
"""
快速截图测试 - 使用新闻源URL
"""

import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from screenshot_fetcher import ScreenshotFetcher

# 新闻源URL（从selected_2026-02-06.json）
hotspots = [
    {
        "id": 1,
        "url": "https://openai.com/blog/gpt-5-preview",
        "title": "OpenAI GPT-5"
    },
    {
        "id": 2,
        "url": "https://ai.meta.com/blog/",
        "title": "Meta Llama 3.5"
    },
    {
        "id": 3,
        "url": "https://deepmind.google/discover/blog/",
        "title": "DeepMind Robot"
    }
]

output_dir = '/home/ubuntu/.openclaw/workspace/AiTrend/video/src/public/screenshots'

print("=" * 60)
print("🌐 开始抓取新闻源网站截图")
print("=" * 60)

fetcher = ScreenshotFetcher(output_dir=output_dir, max_workers=3)
results = fetcher.capture_batch(hotspots)

print("\n" + "=" * 60)
print("📊 截图结果")
print("=" * 60)

for hotspot_id, path in results.items():
    print(f"✅ 热点 {hotspot_id}: {path}")

print(f"\n总计: {len(results)}/{len(hotspots)} 个网站截图成功")
print(f"\n截图保存位置: {output_dir}")
