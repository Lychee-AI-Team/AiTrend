#!/usr/bin/env python3
"""
生成60秒版本TTS - 慢语速(0.85x)
"""

import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from tts_generator import MinimaxTTS
import os

os.makedirs('/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06', exist_ok=True)

# 使用慢语速 0.85x 来达到60秒
tts = MinimaxTTS(speed=0.85)

scripts = {
    'opening': '今天AI圈发生了什么？',
    'hotspot_1': 'Molt Beach在Product Hunt发布，获得18个赞。这是一个新的AI产品，值得关注。',
    'hotspot_2': 'Anthropic在Product Hunt发布Claude Opus 4.6，获得7个赞。Anthropic继续推动大模型发展。',
    'hotspot_3': '阿里Qwen团队开源Qwen3-Coder代码模型，GitHub获得15328星。这是国产AI的重大突破。',
    'closing': '点赞关注，每天60秒了解AI热点！'
}

print("=== 生成60秒版本TTS（慢语速0.85x）===\n")

total_duration = 0

for name, text in scripts.items():
    output = f'/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06/{name}.mp3'
    print(f'生成 {name}.mp3...')
    result = tts.generate(text, output)
    if result['success']:
        duration_sec = result['duration_ms'] / 1000
        total_duration += duration_sec
        print(f'✅ {name}: {duration_sec:.2f}秒')
    else:
        print(f'❌ {name}: {result.get("error", "失败")}')

print(f"\n总时长: {total_duration:.2f}秒")
print(f"预计总帧数(@30fps): {int(total_duration * 30)}帧")

if total_duration < 55:
    print("\n⚠️ 警告: 总时长不足60秒，建议添加更多内容或使用更慢语速")
