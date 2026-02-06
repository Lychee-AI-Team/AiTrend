#!/usr/bin/env python3
"""
Minimax TTS 生成器
用于 AiTrend 视频配音
"""

import requests
import json
import os
import sys
from typing import Dict, List
from datetime import datetime


class MinimaxTTS:
    """Minimax 文字转语音客户端"""
    
    def __init__(self, api_key: str = None, voice_id: str = None, speed: float = 1.2):
        """
        初始化 Minimax TTS 客户端
        
        Args:
            api_key: Minimax API Key（默认从环境变量读取）
            voice_id: 音色ID（默认从环境变量读取）
            speed: 语速（1.0正常，1.2快20%，默认1.2）
        """
        self.api_key = api_key or os.getenv('MINIMAX_API_KEY')
        self.voice_id = voice_id or os.getenv('MINIMAX_VOICE_ID', 'mastercui')
        self.speed = speed
        
        if not self.api_key:
            raise RuntimeError("❌ MINIMAX_API_KEY not set. 请确保环境变量已正确导出")
        
        self.base_url = "https://api.minimaxi.com/v1/t2a_v2"
    
    def generate(self, text: str, output_file: str, voice_id: str = None, speed: float = None) -> Dict:
        """
        生成单段语音
        
        Args:
            text: 要合成的文本
            output_file: 输出文件路径
            voice_id: 音色ID（可选，覆盖默认）
            speed: 语速（可选，覆盖默认，1.0正常，1.2快20%）
            
        Returns:
            包含 audio_url 和 duration 的字典
        """
        voice = voice_id or self.voice_id
        speed = speed or self.speed
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "speech-2.8-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice,
                "speed": speed,
                "vol": 1,
                "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            },
            "output_format": "url"  # 返回URL，方便下载
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            result = response.json()
            
            if result.get("base_resp", {}).get("status_code", -1) != 0:
                raise Exception(f"TTS失败: {result.get('base_resp', {}).get('status_msg', '未知错误')}")
            
            # 下载音频
            audio_url = result["data"]["audio"]
            self._download_audio(audio_url, output_file)
            
            return {
                "file": output_file,
                "url": audio_url,
                "duration_ms": result["extra_info"]["audio_length"],
                "word_count": result["extra_info"]["word_count"],
                "success": True
            }
            
        except Exception as e:
            return {
                "file": output_file,
                "error": str(e),
                "success": False
            }
    
    def generate_batch(self, scripts: Dict[str, str], output_dir: str, voice_id: str = None) -> List[Dict]:
        """
        批量生成多段语音
        
        Args:
            scripts: {场景ID: 文本内容}
            output_dir: 输出目录
            voice_id: 音色ID（可选）
            
        Returns:
            每段语音的元数据列表
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        print(f"🎙️  开始批量生成语音，共 {len(scripts)} 段...")
        
        for idx, (scene_id, text) in enumerate(scripts.items(), 1):
            output_file = os.path.join(output_dir, f"{scene_id}.mp3")
            
            print(f"  [{idx}/{len(scripts)}] 生成 {scene_id}...", end=" ")
            
            try:
                result = self.generate(text, output_file, voice_id)
                result["scene_id"] = scene_id
                results.append(result)
                
                if result["success"]:
                    duration_sec = result['duration_ms'] // 1000
                    print(f"✅ {duration_sec}s")
                else:
                    print(f"❌ {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ {e}")
                results.append({
                    "scene_id": scene_id,
                    "error": str(e),
                    "success": False
                })
        
        # 保存元数据（供 Remotion 使用）
        metadata_file = os.path.join(output_dir, "metadata.json")
        metadata = {
            "generation_time": datetime.now().isoformat(),
            "voice_id": voice_id or self.voice_id,
            "total_segments": len(scripts),
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
            "segments": results
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 生成完成: {metadata['successful']}/{metadata['total_segments']} 成功")
        print(f"💾 元数据已保存: {metadata_file}")
        
        return results
    
    def generate_from_script(self, script_file: str, output_dir: str) -> Dict:
        """
        从视频脚本文件生成全部语音
        
        Args:
            script_file: 视频脚本 JSON 文件路径
            output_dir: 音频输出目录
            
        Returns:
            生成结果统计
        """
        # 加载脚本
        with open(script_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        script = data.get('video_script', {})
        
        # 提取所有需要语音的文本
        texts = {}
        
        # 开场
        if 'opening' in script:
            texts['opening'] = script['opening']
        
        # 详细播报
        for i, hotspot in enumerate(script.get('detailed_hotspots', []), 1):
            scene_id = f"detailed_{i}"
            texts[scene_id] = hotspot.get('script', '')
        
        # 快速播报
        for i, hotspot in enumerate(script.get('quick_hotspots', []), 1):
            scene_id = f"quick_{i}"
            texts[scene_id] = hotspot.get('script', '')
        
        # 结尾
        if 'closing' in script:
            texts['closing'] = script['closing']
        
        print(f"📖 从脚本提取 {len(texts)} 段文本")
        
        # 批量生成
        results = self.generate_batch(texts, output_dir)
        
        return {
            "script_file": script_file,
            "output_dir": output_dir,
            "total_segments": len(texts),
            "results": results
        }
    
    def _download_audio(self, url: str, output_file: str):
        """下载音频文件"""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            f.write(response.content)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Minimax TTS 生成器')
    parser.add_argument('--script', '-s', help='视频脚本文件路径（自动生成全部语音）')
    parser.add_argument('--text', '-t', help='单段文本')
    parser.add_argument('--output', '-o', required=True, help='输出文件或目录')
    parser.add_argument('--voice', '-v', help='音色ID（可选，默认从环境变量读取）')
    
    args = parser.parse_args()
    
    # 初始化 TTS
    tts = MinimaxTTS(voice_id=args.voice)
    
    if args.script:
        # 从脚本生成全部语音
        result = tts.generate_from_script(args.script, args.output)
    elif args.text:
        # 生成单段语音
        result = tts.generate(args.text, args.output, args.voice)
        print(f"{'✅' if result['success'] else '❌'} 生成结果: {result}")
    else:
        print("❌ 请指定 --script 或 --text")
        sys.exit(1)


if __name__ == "__main__":
    main()
