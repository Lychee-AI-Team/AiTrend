#!/usr/bin/env python3
"""
视频生成流程
整合所有步骤：精选 -> LLM脚本 -> TTS -> 转换 -> 渲染
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selector import HotspotSelector
from llm_processor import VideoScriptGenerator
from tts_generator import MinimaxTTS
from script_converter import ScriptConverter


class VideoPipeline:
    """视频生成流程管理器"""
    
    def __init__(self, base_dir: str = None):
        """
        初始化流程
        
        Args:
            base_dir: 视频模块根目录（默认为 AiTrend/video）
        """
        self.base_dir = base_dir or '/home/ubuntu/.openclaw/workspace/AiTrend/video'
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'audio'), exist_ok=True)
    
    def run(self, input_file: str = None, date: str = None, skip_render: bool = False) -> Dict:
        """
        运行完整视频生成流程
        
        Args:
            input_file: 输入数据文件（默认自动查找）
            date: 日期（YYYY-MM-DD，默认今天）
            skip_render: 是否跳过 Remotion 渲染（用于测试）
            
        Returns:
            流程执行结果
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        
        print(f"\n{'='*60}")
        print(f"🎬 AiTrend 视频生成流程 - {date}")
        print(f"{'='*60}\n")
        
        # 步骤1: 查找输入文件
        if not input_file:
            input_file = self._find_input_file(date)
        
        if not os.path.exists(input_file):
            print(f"❌ 输入文件不存在: {input_file}")
            return {"success": False, "error": "输入文件不存在"}
        
        print(f"📁 输入文件: {input_file}\n")
        
        # 步骤2: 热点精选
        print("[步骤 1/5] 热点精选...")
        selected_file = os.path.join(self.data_dir, f'selected_{date}.json')
        selector = HotspotSelector(max_items=8, min_heat_score=50)
        selected_data = selector.select(input_file, selected_file)
        
        if selected_data['selected_count'] == 0:
            print("❌ 没有精选到热点，流程终止")
            return {"success": False, "error": "无热点数据"}
        
        print()
        
        # 步骤3: LLM 生成脚本
        print("[步骤 2/5] LLM 生成视频脚本...")
        script_file = os.path.join(self.data_dir, f'script_{date}.json')
        
        try:
            generator = VideoScriptGenerator()
            script_data = generator.generate(selected_file, script_file)
        except Exception as e:
            print(f"❌ 脚本生成失败: {e}")
            return {"success": False, "error": f"脚本生成失败: {e}"}
        
        print()
        
        # 步骤4: TTS 生成语音
        print("[步骤 3/5] TTS 生成语音...")
        audio_dir = os.path.join(self.assets_dir, 'audio', date)
        
        try:
            tts = MinimaxTTS()
            tts_result = tts.generate_from_script(script_file, audio_dir)
            
            # 检查成功率
            success_count = sum(1 for r in tts_result['results'] if r.get('success'))
            if success_count == 0:
                print("❌ TTS 全部失败，流程终止")
                return {"success": False, "error": "TTS 生成失败"}
        except Exception as e:
            print(f"❌ TTS 生成失败: {e}")
            return {"success": False, "error": f"TTS 生成失败: {e}"}
        
        print()
        
        # 步骤5: 数据转换
        print("[步骤 4/5] 转换 Remotion 输入数据...")
        audio_metadata = os.path.join(audio_dir, 'metadata.json')
        remotion_input = os.path.join(self.data_dir, f'remotion_input_{date}.json')
        
        try:
            converter = ScriptConverter(fps=30)
            remotion_data = converter.convert(script_file, audio_metadata, remotion_input)
        except Exception as e:
            print(f"❌ 数据转换失败: {e}")
            return {"success": False, "error": f"数据转换失败: {e}"}
        
        print()
        
        # 步骤6: Remotion 渲染（可选）
        if not skip_render:
            print("[步骤 5/5] Remotion 渲染视频...")
            render_result = self._render_video(remotion_input, date)
            
            if not render_result['success']:
                print(f"⚠️  渲染失败，但前几步已完成")
        else:
            print("[步骤 5/5] ⏭️  跳过渲染（skip_render=True）")
            render_result = {"success": True, "skipped": True}
        
        print()
        
        # 汇总结果
        result = {
            "success": True,
            "date": date,
            "steps": {
                "select": {"file": selected_file, "count": selected_data['selected_count']},
                "script": {"file": script_file, "model": script_data.get('model')},
                "tts": {"dir": audio_dir, "segments": len(tts_result['results'])},
                "convert": {"file": remotion_input},
                "render": render_result
            },
            "output": {
                "selected": selected_file,
                "script": script_file,
                "audio": audio_dir,
                "remotion_input": remotion_input,
                "video": render_result.get('video_file') if render_result.get('success') else None
            }
        }
        
        print(f"{'='*60}")
        print(f"✅ 流程完成!")
        print(f"{'='*60}")
        print(f"\n📁 输出文件:")
        print(f"  精选数据: {selected_file}")
        print(f"  视频脚本: {script_file}")
        print(f"  音频文件: {audio_dir}")
        print(f"  Remotion输入: {remotion_input}")
        if result['output']['video']:
            print(f"  视频文件: {result['output']['video']}")
        
        return result
    
    def _find_input_file(self, date: str) -> str:
        """查找输入文件"""
        # 可能的文件名
        candidates = [
            os.path.join(self.data_dir, 'input', f'daily_raw_{date}.json'),
            os.path.join(self.data_dir, 'input', f'daily_content_{date}.json'),
            os.path.join('/home/ubuntu/.openclaw/workspace/AiTrend/data', f'daily_raw_{date}.json'),
            os.path.join('/home/ubuntu/.openclaw/workspace/AiTrend/data', f'output_{date}.json'),
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        # 如果没找到，返回第一个候选路径（让后续报错）
        return candidates[0]
    
    def _render_video(self, remotion_input: str, date: str) -> Dict:
        """调用 Remotion 渲染视频"""
        video_dir = os.path.join(self.data_dir, 'output')
        os.makedirs(video_dir, exist_ok=True)
        
        output_file = os.path.join(video_dir, f'daily_{date}.mp4')
        
        # 检查 Remotion 是否安装
        remotion_dir = os.path.join(self.base_dir, 'src')
        if not os.path.exists(os.path.join(remotion_dir, 'package.json')):
            print("⚠️  Remotion 未安装，跳过渲染")
            return {"success": False, "error": "Remotion 未安装"}
        
        # 设置环境变量
        env = os.environ.copy()
        env['REMOTION_INPUT'] = remotion_input
        env['REMOTION_OUTPUT'] = output_file
        
        try:
            # 调用 Remotion 渲染
            result = subprocess.run(
                ['npm', 'run', 'render'],
                cwd=remotion_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print(f"✅ 视频渲染完成: {output_file}")
                return {"success": True, "video_file": output_file}
            else:
                print(f"❌ 渲染失败: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            print("❌ 渲染超时")
            return {"success": False, "error": "渲染超时"}
        except Exception as e:
            print(f"❌ 渲染异常: {e}")
            return {"success": False, "error": str(e)}


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AiTrend 视频生成流程')
    parser.add_argument('--input', '-i', help='输入数据文件路径')
    parser.add_argument('--date', '-d', help='日期 (YYYY-MM-DD，默认今天)')
    parser.add_argument('--skip-render', action='store_true', help='跳过 Remotion 渲染')
    parser.add_argument('--base-dir', '-b', help='视频模块根目录')
    
    args = parser.parse_args()
    
    pipeline = VideoPipeline(base_dir=args.base_dir)
    result = pipeline.run(
        input_file=args.input,
        date=args.date,
        skip_render=args.skip_render
    )
    
    if not result['success']:
        sys.exit(1)


if __name__ == '__main__':
    main()
