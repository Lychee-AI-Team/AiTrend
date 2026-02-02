#!/usr/bin/env python3
"""
AiTrend 流程控制器 - 手动调用OpenClaw大模型版

使用方法：
1. 运行此脚本抓取项目
2. 脚本会输出每个项目的提示词
3. 您手动调用大模型生成内容
4. 收集结果后发布
"""

import os
import yaml
import json
from typing import List, Dict, Any
from datetime import datetime

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
        'max_candidates': 10,
        'growth_threshold': 0.3
    }
    
    source = GithubTrend(config)
    candidates = source.discover()
    
    for c in candidates:
        c['source_name'] = 'github_trend'
    
    print(f"\n✅ 发现 {len(candidates)} 个候选项目")
    return candidates

def fetch_readme(url: str) -> str:
    """抓取README"""
    import requests
    
    parts = url.replace('https://', '').replace('http://', '').split('/')
    if len(parts) < 3:
        return ""
    
    repo_path = f"{parts[1]}/{parts[2]}"
    
    urls = [
        f"https://raw.githubusercontent.com/{repo_path}/main/README.md",
        f"https://raw.githubusercontent.com/{repo_path}/master/README.md",
    ]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    for readme_url in urls:
        try:
            response = session.get(readme_url, timeout=10)
            if response.status_code == 200:
                return response.text[:2000]
        except:
            continue
    
    return ""

def extract_readme_preview(readme: str) -> str:
    """提取README预览"""
    lines = readme.split('\n')
    preview_lines = []
    
    for line in lines[:25]:
        line = line.strip()
        if line.startswith('```'):
            continue
        if line and not line.startswith('#') and len(line) > 10:
            preview_lines.append(line[:100])
        if line.startswith('- ') or line.startswith('* '):
            preview_lines.append(line[:100])
        
        if len('\n'.join(preview_lines)) > 400:
            break
    
    return '\n'.join(preview_lines[:8])

def build_prompt(candidate: Dict) -> str:
    """构建大模型提示词"""
    
    name = candidate.get('name', '')
    description = candidate.get('description', '')
    url = candidate.get('url', '')
    stars = candidate.get('stars', 0)
    language = candidate.get('language', '')
    
    # 抓取README
    readme = fetch_readme(url)
    readme_preview = extract_readme_preview(readme) if readme else ""
    
    context_parts = [f"项目名称: {name}"]
    
    if description:
        context_parts.append(f"项目描述: {description}")
    
    if stars:
        context_parts.append(f"GitHub Stars: {stars}")
    
    if language:
        context_parts.append(f"主要语言: {language}")
    
    if readme_preview:
        context_parts.append(f"README预览:\n{readme_preview}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""请用自然叙述的方式介绍以下项目：

{context}

要求：
1. 不要列表、不要序号、不要用 bullet points
2. 禁止空话套话（如"针对痛点"、"功能设计"、"架构清晰"、"旨在解决"）
3. 像跟朋友介绍一样口语化、流畅
4. 突出产品特点、亮点、为什么值得关注
5. 控制在400字以内
6. 直接输出内容，不要标题，不要"好的"、"明白"等确认词

项目链接: {url}"""
    
    return prompt

def main():
    """主流程"""
    print("\n" + "="*60)
    print("🎯 AiTrend 流程控制器")
    print("="*60)
    
    # 获取候选项目
    candidates = fetch_candidates()
    
    if not candidates:
        print("❌ 未发现候选项目")
        return
    
    # 为每个项目生成提示词
    print("\n" + "="*60)
    print("📝 生成大模型提示词")
    print("="*60)
    
    prompts = []
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"\n{i}. {candidate.get('name', 'Unknown')}")
        prompt = build_prompt(candidate)
        prompts.append({
            'name': candidate.get('name', ''),
            'url': candidate.get('url', ''),
            'prompt': prompt
        })
    
    # 保存提示词到文件
    output_file = '/tmp/aitrend_prompts.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 提示词已保存到: {output_file}")
    print(f"\n请手动调用大模型生成内容，使用以下提示词：")
    
    # 输出第一个提示词作为示例
    if prompts:
        print("\n" + "="*60)
        print(f"示例 - {prompts[0]['name']}:")
        print("="*60)
        print(prompts[0]['prompt'])
    
    return prompts

if __name__ == '__main__':
    main()
