#!/usr/bin/env python3
"""
60秒视频生成完整流程
整合: 截图 -> LLM脚本 -> TTS -> 渲染
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from screenshot_fetcher import ScreenshotFetcher
from llm_processor_60s import VideoScriptGenerator60s
from tts_generator import MinimaxTTS


def run_pipeline(date: str = None, base_dir: str = None):
    """
    运行60秒视频生成完整流程
    
    Args:
        date: 日期 (YYYY-MM-DD)
        base_dir: 项目根目录
    """
    date = date or datetime.now().strftime('%Y-%m-%d')
    base_dir = base_dir or '/home/ubuntu/.openclaw/workspace/AiTrend/video'
    
    print(f"\n{'='*60}")
    print(f"🎬 60秒视频生成流程 - {date}")
    print(f"{'='*60}\n")
    
    # 路径配置
    input_file = f"{base_dir}/data/selected_{date}.json"
    screenshot_dir = f"{base_dir}/assets/screenshots/{date}"
    audio_dir = f"{base_dir}/assets/audio/60s/{date}"
    script_file = f"{base_dir}/data/script_60s_{date}.json"
    output_video = f"{base_dir}/data/output/daily_60s_{date}.mp4"
    
    # 确保目录存在
    os.makedirs(screenshot_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_video), exist_ok=True)
    
    # ========== 步骤1: 检查输入数据 ==========
    print("[步骤 1/5] 检查输入数据...")
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    hotspots = data.get('hotspots', [])
    if len(hotspots) < 3:
        print(f"⚠️ 热点数量不足 ({len(hotspots)}个)，需要至少3个")
        return False
    
    print(f"✅ 加载 {len(hotspots)} 个热点")
    
    # ========== 步骤2: 网站截图 ==========
    print("\n[步骤 2/5] 抓取网站截图...")
    try:
        fetcher = ScreenshotFetcher(output_dir=screenshot_dir, max_workers=3)
        screenshot_results = fetcher.capture_batch(hotspots[:3])  # 只截图前3个
        
        # 更新热点数据
        for i, hotspot in enumerate(hotspots[:3]):
            if i in screenshot_results:
                hotspot['screenshot'] = f"screenshots/{date}/hotspot_{i}.png"
                hotspot['use_screenshot'] = True
            else:
                hotspot['use_screenshot'] = False
        
        print(f"✅ 截图完成: {len(screenshot_results)}/3 成功")
    except Exception as e:
        print(f"⚠️ 截图失败: {e}，将使用Logo替代")
    
    # ========== 步骤3: 生成60秒脚本 ==========
    print("\n[步骤 3/5] 生成60秒视频脚本...")
    try:
        generator = VideoScriptGenerator60s()
        script_data = generator.generate(hotspots[:3], date)
        
        with open(script_file, 'w') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 脚本生成完成: {script_data['total_duration']}")
    except Exception as e:
        print(f"❌ 脚本生成失败: {e}")
        return False
    
    # ========== 步骤4: 生成语音 (speed=1.2) ==========
    print("\n[步骤 4/5] 生成语音 (语速1.2x)...")
    try:
        tts = MinimaxTTS(speed=1.2)  # 语速提高20%
        
        script = script_data['script']
        texts = {
            'opening': script['opening'],
            'hotspot_1': script['hotspots'][0]['script'],
            'hotspot_2': script['hotspots'][1]['script'],
            'hotspot_3': script['hotspots'][2]['script'],
            'closing': script['closing'],
        }
        
        results = []
        for name, text in texts.items():
            output_file = f"{audio_dir}/{name}.mp3"
            result = tts.generate(text, output_file)
            results.append(result)
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {name}")
        
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ 语音生成完成: {success_count}/{len(results)}")
    except Exception as e:
        print(f"❌ 语音生成失败: {e}")
        return False
    
    # ========== 步骤5: 渲染视频 ==========
    print("\n[步骤 5/5] 渲染视频...")
    try:
        # 找到浏览器路径
        browser_path = subprocess.run(
            ["find", os.path.expanduser("~/.cache/ms-playwright"), "-name", "chrome", "-type", "f"],
            capture_output=True, text=True
        ).stdout.strip().split('\n')[0]
        
        cmd = [
            'npx', 'remotion', 'render',
            'src/index-60s.tsx',
            'DailyNews60s',
            output_video,
            '--browser-executable=' + browser_path,
            '--concurrency=2',
            '--overwrite'
        ]
        
        print(f"执行: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ 视频渲染完成: {output_video}")
        else:
            print(f"❌ 渲染失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 渲染异常: {e}")
        return False
    
    # 完成
    print(f"\n{'='*60}")
    print(f"🎉 60秒视频生成完成!")
    print(f"{'='*60}")
    print(f"\n📁 输出文件:")
    print(f"  视频: {output_video}")
    print(f"  脚本: {script_file}")
    print(f"  音频: {audio_dir}")
    
    return True


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='60秒视频生成流程')
    parser.add_argument('--date', '-d', help='日期 (YYYY-MM-DD)')
    parser.add_argument('--base-dir', '-b', help='项目根目录')
    
    args = parser.parse_args()
    
    success = run_pipeline(args.date, args.base_dir)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
