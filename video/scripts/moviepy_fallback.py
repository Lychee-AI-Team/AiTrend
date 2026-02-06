#!/usr/bin/env python3
"""
MoviePy 保底方案 - 使用Python生成视频
当Remotion渲染失败时使用
"""

import json
import os
import sys
from datetime import datetime

def create_video_with_moviepy(input_file: str, output_file: str):
    """使用moviepy创建视频"""
    
    try:
        from moviepy.editor import (
            TextClip, CompositeVideoClip, AudioFileClip,
            concatenate_videoclips, ImageClip
        )
        from moviepy.video.fx.all import fadein, fadeout
    except ImportError:
        print("❌ moviepy 未安装，正在安装...")
        os.system("pip3 install moviepy -q")
        from moviepy.editor import (
            TextClip, CompositeVideoClip, AudioFileClip,
            concatenate_videoclips, ImageClip
        )
    
    # 加载数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scenes = data['scenes']
    base_dir = os.path.dirname(input_file)
    
    video_clips = []
    
    for scene in scenes:
        duration = scene['durationMs'] / 1000  # 转换为秒
        
        # 根据场景类型创建内容
        if scene['type'] == 'opening':
            # 开场 - 大标题
            txt_clip = TextClip(
                f"AiTrend\nAI热点日报\n\n{scene['text']}",
                fontsize=60,
                color='white',
                size=(1920, 1080),
                bg_color='#0a0a0f',
                method='caption',
                align='center',
                font='DejaVu-Sans'
            ).set_duration(duration)
            
        elif scene['type'] == 'detailed':
            # 详细播报
            content = f"热点 #{scene['rank']}\n\n{scene['title']}\n\n{scene['text']}"
            if scene.get('keyPoint'):
                content += f"\n\n核心观点: {scene['keyPoint']}"
            
            txt_clip = TextClip(
                content,
                fontsize=40,
                color='white',
                size=(1920, 1080),
                bg_color='#0f172a',
                method='caption',
                align='west',
                font='DejaVu-Sans'
            ).set_duration(duration)
            
        elif scene['type'] == 'quick':
            # 快速播报 - 列表
            content = "更多热点:\n\n"
            for item in scene['items']:
                content += f"• {item['title']}\n{item['text']}\n\n"
            
            txt_clip = TextClip(
                content,
                fontsize=35,
                color='white',
                size=(1920, 1080),
                bg_color='#1e293b',
                method='caption',
                align='west',
                font='DejaVu-Sans'
            ).set_duration(duration)
            
        elif scene['type'] == 'closing':
            # 结尾
            txt_clip = TextClip(
                f"AiTrend\n\n{scene['text']}\n\n点赞 收藏 关注",
                fontsize=50,
                color='white',
                size=(1920, 1080),
                bg_color='#1e1b4b',
                method='caption',
                align='center',
                font='DejaVu-Sans'
            ).set_duration(duration)
            
        else:
            # 默认
            txt_clip = TextClip(
                scene.get('text', ''),
                fontsize=40,
                color='white',
                size=(1920, 1080),
                bg_color='black'
            ).set_duration(duration)
        
        video_clips.append(txt_clip)
        print(f"✅ 创建片段: {scene['id']} ({duration}s)")
    
    # 合并所有片段
    print("\n🎬 合并视频片段...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # 添加音频（如果有）
    audio_file = os.path.join(base_dir, '../assets/audio/2026-02-06/opening.mp3')
    if os.path.exists(audio_file):
        print("🎵 添加音频...")
        # 需要将所有音频合并
        # 这里简化处理，使用第一个音频
        audio = AudioFileClip(audio_file)
        if audio.duration < final_video.duration:
            # 循环音频
            n_loops = int(final_video.duration / audio.duration) + 1
            audio = audio.loop(n=n_loops)
        audio = audio.subclip(0, final_video.duration)
        final_video = final_video.set_audio(audio)
    
    # 导出
    print(f"💾 导出视频: {output_file}")
    final_video.write_videofile(
        output_file,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='/tmp/tmp_audio.m4a',
        remove_temp=True
    )
    
    print(f"✅ 视频创建成功: {output_file}")
    return output_file


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MoviePy保底方案')
    parser.add_argument('--input', '-i', required=True, help='Remotion输入JSON文件')
    parser.add_argument('--output', '-o', required=True, help='输出视频文件')
    
    args = parser.parse_args()
    
    create_video_with_moviepy(args.input, args.output)
