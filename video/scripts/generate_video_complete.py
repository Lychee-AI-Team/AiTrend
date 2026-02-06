#!/usr/bin/env python3
"""
完整解决方案：使用Tavily搜索获取产品信息并生成视频
"""

import http.client
import json
import os
import sys

# 读取环境变量
env_path = '/home/ubuntu/.openclaw/workspace/AiTrend/.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')
from tts_generator import MinimaxTTS


def search_with_tavily(query: str) -> dict:
    """使用Tavily搜索"""
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        return None
    
    conn = http.client.HTTPSConnection("api.tavily.com", timeout=30)
    
    try:
        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "max_results": 3
        })
        
        headers = {"Content-Type": "application/json"}
        conn.request("POST", "/search", body=payload, headers=headers)
        response = conn.getresponse()
        
        if response.status == 200:
            return json.loads(response.read().decode())
        else:
            print(f"API错误: {response.status}")
            return None
            
    finally:
        conn.close()


def extract_product_description(product_name: str, search_results: dict) -> str:
    """从搜索结果提取产品描述"""
    
    # 首先尝试获取AI生成的答案
    answer = search_results.get('answer', '')
    if answer and len(answer) > 50:
        return answer[:200]
    
    # 否则从结果中提取
    results = search_results.get('results', [])
    if results:
        content = results[0].get('content', '')
        # 提取前200个字符作为描述
        return content[:200] if content else f"{product_name}是一个新的AI产品"
    
    return f"{product_name}是一个值得关注的AI产品"


def generate_video_scripts():
    """生成视频文案和音频"""
    
    products = [
        {"name": "ClawApp", "query": "ClawApp AI product what does it do features"},
        {"name": "OpenAI Frontier", "query": "OpenAI Frontier Product Hunt features what is it"},
        {"name": "Obi", "query": "Obi Product Hunt AI tool features"}
    ]
    
    print("=" * 60)
    print("🔍 搜索产品详细信息...")
    print("=" * 60)
    
    scripts = {
        'opening': '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。'
    }
    
    for i, product in enumerate(products, 1):
        print(f"\n搜索 {product['name']}...")
        
        results = search_with_tavily(product['query'])
        
        if results:
            description = extract_product_description(product['name'], results)
            # 生成中文文案
            script = f"{product['name']}，{description}"
            scripts[f'hotspot_{i}'] = script
            print(f"✅ 找到信息: {script[:80]}...")
        else:
            # 如果搜索失败，使用基础文案
            scripts[f'hotspot_{i}'] = f"{product['name']}是一个新的AI产品，值得关注和了解。"
            print(f"⚠️ 使用基础文案")
    
    scripts['closing'] = '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。'
    
    # 生成音频
    print("\n" + "=" * 60)
    print("🎤 生成TTS音频...")
    print("=" * 60)
    
    os.makedirs('/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06', exist_ok=True)
    tts = MinimaxTTS(speed=1.2)
    
    total_duration = 0
    frame_config = []
    current_frame = 0
    fps = 30
    
    for name, text in scripts.items():
        output = f'/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06/{name}.mp3'
        result = tts.generate(text, output)
        if result['success']:
            sec = result['duration_ms'] / 1000
            frames = int(sec * fps)
            total_duration += sec
            frame_config.append({
                'name': name,
                'start': current_frame,
                'duration': frames,
                'seconds': sec
            })
            current_frame += frames
            print(f"✅ {name}: {sec:.2f}秒 ({frames}帧)")
        else:
            print(f"❌ {name}: 失败")
    
    print(f"\n总时长: {total_duration:.2f}秒")
    print(f"总帧数: {current_frame}帧 (@30fps)")
    
    # 输出视频配置
    print("\n" + "=" * 60)
    print("🎬 视频配置")
    print("=" * 60)
    print(f"fps: 30")
    print(f"totalFrames: {current_frame}")
    for cfg in frame_config:
        print(f"{cfg['name']}: start={cfg['start']}, duration={cfg['duration']}帧 ({cfg['seconds']:.2f}秒)")
    
    return scripts, frame_config


if __name__ == '__main__':
    scripts, config = generate_video_scripts()
    
    print("\n" + "=" * 60)
    print("✅ 完成！音频已保存")
    print("=" * 60)
