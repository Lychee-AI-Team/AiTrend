#!/usr/bin/env python3
"""
脚本转换器
将视频脚本和音频元数据转换为 Remotion 输入格式
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime


class ScriptConverter:
    """Remotion 输入数据转换器"""
    
    def __init__(self, fps: int = 30):
        """
        初始化转换器
        
        Args:
            fps: 视频帧率（默认30fps）
        """
        self.fps = fps
    
    def convert(self, script_file: str, audio_metadata_file: str, output_file: str = None) -> Dict[str, Any]:
        """
        转换脚本和音频元数据为 Remotion 输入格式
        
        Args:
            script_file: 视频脚本 JSON 文件路径
            audio_metadata_file: 音频元数据文件路径
            output_file: 输出文件路径（可选）
            
        Returns:
            Remotion 输入数据
        """
        # 加载脚本
        with open(script_file, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        # 加载音频元数据
        with open(audio_metadata_file, 'r', encoding='utf-8') as f:
            audio_data = json.load(f)
        
        script = script_data.get('video_script', {})
        segments = audio_data.get('segments', [])
        
        # 构建音频时长映射
        audio_durations = {}
        for seg in segments:
            if seg.get('success'):
                scene_id = seg.get('scene_id')
                duration_ms = seg.get('duration_ms', 0)
                audio_durations[scene_id] = duration_ms
        
        # 构建 Remotion 场景数据
        scenes = []
        current_frame = 0
        
        # 开场场景
        if 'opening' in script:
            duration_ms = audio_durations.get('opening', 10000)  # 默认10秒
            duration_frames = self._ms_to_frames(duration_ms)
            
            scenes.append({
                "id": "opening",
                "type": "opening",
                "startFrame": current_frame,
                "durationFrames": duration_frames,
                "text": script['opening'],
                "audioFile": "assets/audio/opening.mp3",
                "durationMs": duration_ms
            })
            current_frame += duration_frames
        
        # 详细播报场景
        for i, hotspot in enumerate(script.get('detailed_hotspots', []), 1):
            scene_id = f"detailed_{i}"
            duration_ms = audio_durations.get(scene_id, 45000)  # 默认45秒
            duration_frames = self._ms_to_frames(duration_ms)
            
            scenes.append({
                "id": scene_id,
                "type": "detailed",
                "rank": hotspot.get('rank', i),
                "startFrame": current_frame,
                "durationFrames": duration_frames,
                "title": hotspot.get('title', ''),
                "text": hotspot.get('script', ''),
                "keyPoint": hotspot.get('key_point', ''),
                "source": hotspot.get('source', ''),
                "audioFile": f"assets/audio/{scene_id}.mp3",
                "durationMs": duration_ms
            })
            current_frame += duration_frames
        
        # 快速播报场景（合集）
        quick_items = []
        for i, hotspot in enumerate(script.get('quick_hotspots', []), 1):
            scene_id = f"quick_{i}"
            duration_ms = audio_durations.get(scene_id, 20000)  # 默认20秒
            
            quick_items.append({
                "rank": hotspot.get('rank', i + 3),
                "title": hotspot.get('title', ''),
                "text": hotspot.get('script', ''),
                "durationMs": duration_ms
            })
        
        if quick_items:
            total_duration_ms = sum(item['durationMs'] for item in quick_items)
            duration_frames = self._ms_to_frames(total_duration_ms)
            
            scenes.append({
                "id": "quick_summary",
                "type": "quick",
                "startFrame": current_frame,
                "durationFrames": duration_frames,
                "items": quick_items,
                "audioFiles": [f"assets/audio/quick_{i}.mp3" for i in range(1, len(quick_items) + 1)],
                "durationMs": total_duration_ms
            })
            current_frame += duration_frames
        
        # 结尾场景
        if 'closing' in script:
            duration_ms = audio_durations.get('closing', 8000)  # 默认8秒
            duration_frames = self._ms_to_frames(duration_ms)
            
            scenes.append({
                "id": "closing",
                "type": "closing",
                "startFrame": current_frame,
                "durationFrames": duration_frames,
                "text": script['closing'],
                "audioFile": "assets/audio/closing.mp3",
                "durationMs": duration_ms
            })
            current_frame += duration_frames
        
        # 构建最终输出
        output = {
            "date": script_data.get('date'),
            "generationTime": datetime.now().isoformat(),
            "fps": self.fps,
            "totalFrames": current_frame,
            "totalDuration": self._frames_to_time(current_frame),
            "scenes": scenes,
            "metadata": {
                "scriptFile": script_file,
                "audioMetadataFile": audio_metadata_file,
                "sceneCount": len(scenes),
                "detailedCount": len(script.get('detailed_hotspots', [])),
                "quickCount": len(script.get('quick_hotspots', []))
            }
        }
        
        # 保存到文件
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"💾 Remotion 输入数据已保存: {output_file}")
        
        # 打印摘要
        print(f"\n📋 Remotion 数据摘要:")
        print(f"  总帧数: {current_frame} (@{self.fps}fps)")
        print(f"  总时长: {output['totalDuration']}")
        print(f"  场景数: {len(scenes)}")
        for scene in scenes:
            print(f"    - {scene['id']}: {scene['durationMs']}ms ({scene['durationFrames']}帧)")
        
        return output
    
    def _ms_to_frames(self, ms: int) -> int:
        """毫秒转换为帧数"""
        return int((ms / 1000) * self.fps)
    
    def _frames_to_time(self, frames: int) -> str:
        """帧数转换为时间字符串"""
        total_seconds = frames / self.fps
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes}:{seconds:02d}"


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Remotion 输入数据转换器')
    parser.add_argument('--script', '-s', required=True, help='视频脚本文件路径')
    parser.add_argument('--audio', '-a', required=True, help='音频元数据文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出文件路径')
    parser.add_argument('--fps', type=int, default=30, help='视频帧率（默认30）')
    
    args = parser.parse_args()
    
    converter = ScriptConverter(fps=args.fps)
    result = converter.convert(args.script, args.audio, args.output)


if __name__ == '__main__':
    main()
