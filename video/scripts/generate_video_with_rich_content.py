#!/usr/bin/env python3
"""
视频文案生成器 - 从AiTrend完整数据生成有信息量的文案
"""

import json
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/video/scripts')

from tts_generator import MinimaxTTS
import os


def load_latest_articles(count=3):
    """加载最新的文章（包含完整信息）"""
    with open('/home/ubuntu/.openclaw/workspace/AiTrend/memory/sent_articles.json', 'r') as f:
        data = json.load(f)
    
    articles = data.get('articles', [])
    # 按时间排序，取最新的
    latest = sorted(articles, key=lambda x: x.get('sent_at', 0), reverse=True)[:count]
    return latest


def generate_rich_script(article: dict) -> str:
    """
    基于文章完整信息生成有信息量的视频文案
    """
    title = article.get('title', '')
    summary = article.get('summary', '')
    url = article.get('url', '')
    metadata = article.get('metadata', {})
    
    # 提取产品名称（从标题中）
    import re
    match = re.search(r'\]\s*(.+?)\s*⭐', title)
    product_name = match.group(1) if match else title.split(']')[-1].split('⭐')[0].strip()
    
    # 使用summary作为核心内容
    if summary and len(summary) > 20:
        # 如果有详细摘要，直接使用
        return f"{product_name}，{summary}"
    else:
        # 如果摘要太短，生成一个基础介绍
        return f"{product_name}是一个新的AI产品，值得关注和了解。"


def main():
    """生成视频音频（使用完整信息）"""
    
    print("=" * 60)
    print("🎬 视频文案生成器（使用AiTrend完整数据）")
    print("=" * 60)
    
    # 加载最新3条文章
    articles = load_latest_articles(3)
    
    print(f"\n加载到 {len(articles)} 条最新文章\n")
    
    # 显示文章信息
    for i, article in enumerate(articles, 1):
        print(f"{'='*60}")
        print(f"文章 #{i}")
        print(f"{'='*60}")
        print(f"标题: {article.get('title', 'N/A')}")
        print(f"摘要: {article.get('summary', 'N/A')[:100]}..." if article.get('summary') else "摘要: (无)")
        print(f"来源: {article.get('source', 'N/A')}")
        print(f"元数据: {article.get('metadata', {})}")
        print()
    
    # 检查是否有足够的信息
    has_summary = any(article.get('summary') for article in articles)
    
    if not has_summary:
        print("⚠️ 警告: 当前文章缺少摘要信息")
        print("需要重新运行AiTrend获取完整数据，或人工提供文案")
        return
    
    # 生成文案
    print("\n" + "=" * 60)
    print("📄 生成的视频文案")
    print("=" * 60)
    
    scripts = {
        'opening': '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。'
    }
    
    for i, article in enumerate(articles, 1):
        script = generate_rich_script(article)
        scripts[f'hotspot_{i}'] = script
        print(f"\n热点{i}: {script}")
    
    scripts['closing'] = '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。'
    
    print("\n" + "=" * 60)
    print("🎤 生成TTS音频...")
    print("=" * 60)
    
    # 生成音频
    os.makedirs('/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06', exist_ok=True)
    tts = MinimaxTTS(speed=1.2)
    
    total_duration = 0
    for name, text in scripts.items():
        output = f'/home/ubuntu/.openclaw/workspace/AiTrend/video/assets/audio/2026-02-06/{name}.mp3'
        result = tts.generate(text, output)
        if result['success']:
            sec = result['duration_ms'] / 1000
            total_duration += sec
            print(f"✅ {name}: {sec:.2f}秒 - {text[:50]}...")
        else:
            print(f"❌ {name}: 失败")
    
    print(f"\n总时长: {total_duration:.2f}秒")
    print(f"\n音频已保存到: assets/audio/2026-02-06/")


if __name__ == '__main__':
    main()
