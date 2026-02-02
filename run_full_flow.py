#!/usr/bin/env python3
"""
AiTrend 完整自动化流程
抓取 → LLM生成 → 发布（确保链接传递）
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# 加载环境变量
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def fetch_candidates() -> List[Dict]:
    """获取候选项目"""
    print("="*60)
    print("📡 从GitHub Trend挖掘项目...")
    print("="*60)
    
    from modules.sources.github_trend import GithubTrend
    
    config = {
        'languages': ['python', 'javascript', 'go'],
        'max_candidates': 3,
        'growth_threshold': 0.5
    }
    
    source = GithubTrend(config)
    candidates = source.discover()
    
    for c in candidates:
        c['source_name'] = 'github_trend'
    
    print(f"\n✅ 发现 {len(candidates)} 个候选项目")
    return candidates[:3]

def generate_content_with_llm(candidate: Dict) -> Dict:
    """
    使用OpenClaw大模型生成内容
    确保链接被包含
    """
    from sessions_spawn import sessions_spawn
    
    name = candidate.get('name', '')
    description = candidate.get('description', '')
    url = candidate.get('url', '')
    stars = candidate.get('stars', 0)
    language = candidate.get('language', '')
    
    print(f"\n📝 生成内容: {name}")
    print(f"   URL: {url}")
    
    # 构建任务
    context_parts = [f"项目名称: {name}"]
    
    if description:
        context_parts.append(f"项目描述: {description}")
    
    if stars:
        context_parts.append(f"GitHub Stars: {stars}")
    
    if language:
        context_parts.append(f"主要语言: {language}")
    
    context = "\n\n".join(context_parts)
    
    task = f"""请用自然叙述的方式介绍以下项目：

{context}

要求：
1. 不要列表、不要序号、不要用 bullet points
2. 禁止空话套话（如"针对痛点"、"功能设计"、"架构清晰"、"旨在解决"）
3. 像跟朋友介绍一样口语化、流畅
4. 突出产品特点、亮点、为什么值得关注
5. 控制在400字以内
6. 直接输出内容，不要标题，不要"好的"、"明白"等确认词"""
    
    print(f"   🤖 调用OpenClaw大模型...")
    
    # 调用大模型
    result = sessions_spawn(
        task=task,
        timeout_seconds=120
    )
    
    if result:
        # 确保链接被包含
        if url not in result:
            result = result.strip() + f"\n\n{url}"
        
        print(f"   ✅ 生成成功 ({len(result)} 字符)")
        
        return {
            'name': name,
            'content': result,
            'url': url,
            'source': 'GitHub'
        }
    else:
        print(f"   ❌ 生成失败")
        return None

def publish_to_discord(contents: List[Dict]) -> int:
    """发布到Discord"""
    print("\n" + "="*60)
    print("📤 发布到 Discord 论坛")
    print("="*60)
    
    from publishers import create_publisher
    
    config = {
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
        'thread_name': '{name} – {source}',
        'username': 'AiTrend',
        'delay': 2
    }
    
    publisher = create_publisher('forum', config)
    
    if not publisher:
        print("❌ 创建发布模块失败")
        return 0
    
    # 验证每个内容都有链接
    for content in contents:
        url = content.get('url', '')
        text = content.get('content', '')
        
        if url and url not in text:
            print(f"⚠️  {content['name']} 内容中缺少链接，自动添加")
            content['content'] = text.strip() + f"\n\n{url}"
    
    return publisher.publish_batch(contents)

def main():
    """主流程"""
    print("\n" + "="*60)
    print("🎯 AiTrend 完整自动化流程")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 获取候选项目
    candidates = fetch_candidates()
    
    if not candidates:
        print("❌ 未发现候选项目")
        return
    
    # 2. 使用大模型生成内容
    print("\n" + "="*60)
    print("🤖 OpenClaw大模型内容生成")
    print("="*60)
    
    generated_contents = []
    for candidate in candidates:
        content = generate_content_with_llm(candidate)
        if content:
            generated_contents.append(content)
        time.sleep(1)  # 避免过快调用
    
    print(f"\n✅ 成功生成 {len(generated_contents)} 条内容")
    
    # 3. 发布到Discord
    if generated_contents:
        published = publish_to_discord(generated_contents)
        print(f"\n{'='*60}")
        print(f"✅ 流程完成！发布 {published}/{len(generated_contents)} 条内容")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    else:
        print("\n❌ 没有内容可发布")

if __name__ == '__main__':
    main()
