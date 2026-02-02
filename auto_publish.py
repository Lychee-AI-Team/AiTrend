#!/usr/bin/env python3
"""
AiTrend 自动发布脚本
完整的抓取 → LLM生成 → 发布流程
确保项目链接正确传递
"""

import os
import sys
import json
import time
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
    return candidates[:3]  # 只取前3个

def build_llm_task(candidate: Dict) -> str:
    """构建LLM任务"""
    
    name = candidate.get('name', '')
    description = candidate.get('description', '')
    url = candidate.get('url', '')
    stars = candidate.get('stars', 0)
    language = candidate.get('language', '')
    
    # 构建上下文
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
6. 直接输出内容，不要标题，不要"好的"、"明白"等确认词

项目链接: {url}

重要：生成的内容最后必须包含项目链接 {url}"""
    
    return task, url

def publish_to_discord(contents: List[Dict]):
    """发布到Discord"""
    print("\n" + "="*60)
    print("📤 发布到 Discord")
    print("="*60)
    
    from publishers import create_publisher
    
    # 创建论坛发布模块
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
    
    # 发布
    return publisher.publish_batch(contents)

def main():
    """主流程"""
    print("\n" + "="*60)
    print("🎯 AiTrend 自动发布流程")
    print("="*60)
    
    # 1. 获取候选项目
    candidates = fetch_candidates()
    
    if not candidates:
        print("❌ 未发现候选项目")
        return
    
    # 2. 生成内容（手动调用大模型）
    print("\n" + "="*60)
    print("📝 请手动调用大模型生成内容")
    print("="*60)
    
    generated_contents = []
    
    for i, candidate in enumerate(candidates, 1):
        name = candidate.get('name', '')
        url = candidate.get('url', '')
        
        print(f"\n{i}. {name}")
        print(f"   URL: {url}")
        
        task, project_url = build_llm_task(candidate)
        
        print(f"\n   请使用 sessions_spawn 调用大模型生成内容")
        print(f"   项目链接: {project_url}")
        
        # 保存任务到文件
        task_file = f'/tmp/aitrend_task_{name}.txt'
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(task)
        
        print(f"   任务已保存到: {task_file}")
        
        # 收集生成的内容（这里需要手动输入或从其他地方获取）
        # 实际使用时，需要等待大模型生成完成
        generated_contents.append({
            'name': name,
            'url': project_url,
            'source': 'GitHub',
            'content': ''  # 待填充
        })
    
    print("\n" + "="*60)
    print("⏳ 请完成大模型生成后，调用 publish 函数发布")
    print("="*60)
    
    return generated_contents

def publish_with_content(contents: List[Dict]):
    """
    发布已生成的内容
    确保每个内容都包含链接
    """
    print("\n" + "="*60)
    print("📤 发布内容到 Discord")
    print("="*60)
    
    # 确保每个内容都包含链接
    for content in contents:
        url = content.get('url', '')
        text = content.get('content', '')
        
        # 如果内容中没有链接，附加链接
        if url and url not in text:
            content['content'] = text + f"\n\n{url}"
    
    # 发布
    return publish_to_discord(contents)

if __name__ == '__main__':
    main()
