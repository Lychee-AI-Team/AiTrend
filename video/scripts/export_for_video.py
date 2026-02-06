#!/usr/bin/env python3
"""
导出视频数据
从selected_*.json导出到视频模板可用的JSON格式
"""

import json
import argparse
import os
from datetime import datetime
from typing import Dict, List


def infer_vendor(title: str, url: str) -> str:
    """从标题和URL推断厂商"""
    text = (title + " " + url).lower()
    
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
    
    for keyword, vendor in vendor_map.items():
        if keyword in text:
            return vendor
    
    return 'default'


def get_logo_path(vendor: str) -> str:
    """获取Logo路径"""
    logo_map = {
        'openai': 'logos/openai.svg',
        'meta': 'logos/meta.svg',
        'google': 'logos/google.svg',
        'deepmind': 'logos/deepmind.svg',
        'anthropic': 'logos/anthropic.svg',
        'microsoft': 'logos/microsoft.svg',
    }
    return logo_map.get(vendor, 'logos/default.svg')


def export_for_video(input_file: str, output_file: str, date: str = None):
    """
    导出视频数据
    
    Args:
        input_file: selected_*.json文件路径
        output_file: 输出JSON文件路径
        date: 日期
    """
    # 加载selected数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hotspots = data.get('hotspots', [])
    date = date or data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    print(f"📊 加载 {len(hotspots)} 条热点")
    
    # 只取前3个热点
    top3 = hotspots[:3]
    
    # 构建60秒视频数据结构
    video_data = {
        'date': date,
        'fps': 30,
        'totalFrames': 1800,  # 60秒
        'scenes': []
    }
    
    # 开场 - 3秒
    video_data['scenes'].append({
        'id': 'opening',
        'type': 'opening',
        'startFrame': 0,
        'durationFrames': 90,
        'text': '今天AI圈发生了什么？',
        'audioFile': 'audio/2026-02-06/opening.mp3'
    })
    
    # 3个热点 - 各18秒
    frame = 90
    for i, hotspot in enumerate(top3, 1):
        vendor = infer_vendor(hotspot.get('title', ''), hotspot.get('url', ''))
        logo = get_logo_path(vendor)
        
        # 简写标题（60秒视频用短标题）
        short_title = hotspot.get('title', '')[:30]
        if len(hotspot.get('title', '')) > 30:
            short_title += '...'
        
        scene = {
            'id': f'hotspot_{i}',
            'type': 'hotspot',
            'startFrame': frame,
            'durationFrames': 540,  # 18秒
            'rank': i,
            'title': short_title,
            'text': hotspot.get('summary', '')[:100] + '...' if len(hotspot.get('summary', '')) > 100 else hotspot.get('summary', ''),
            'keyPoint': hotspot.get('title', '')[:20] + '...',
            'vendor': vendor,
            'logo': logo,
            'url': hotspot.get('url', ''),  # ⭐ 关键：保留原始URL
            'useScreenshot': True,
            'screenshot': f'screenshots/hotspot_{i}.png',  # 截图文件路径
            'audioFile': f'audio/2026-02-06/detailed_{i}.mp3'
        }
        
        video_data['scenes'].append(scene)
        frame += 540
    
    # 结尾 - 3秒
    video_data['scenes'].append({
        'id': 'closing',
        'type': 'closing',
        'startFrame': frame,
        'durationFrames': 90,
        'text': '点赞关注，每天60秒了解AI热点！',
        'audioFile': 'audio/2026-02-06/closing.mp3'
    })
    
    # 保存
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 视频数据已导出: {output_file}")
    print(f"\n包含 {len(video_data['scenes'])} 个场景:")
    for scene in video_data['scenes']:
        url_info = f" (URL: {scene.get('url', '无')[:40]}...)" if 'url' in scene else ''
        print(f"  - {scene['id']}: {scene.get('title', scene.get('text', ''))[:30]}...{url_info}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description='导出视频数据')
    parser.add_argument('--input', '-i', required=True, help='selected_*.json文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出JSON文件路径')
    parser.add_argument('--date', '-d', help='日期')
    
    args = parser.parse_args()
    
    export_for_video(args.input, args.output, args.date)


if __name__ == '__main__':
    main()
