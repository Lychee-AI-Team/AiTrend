#!/usr/bin/env python3
"""
Product Hunt 流程控制器
抓取产品 → 输出提示词 → 手动LLM生成 → 发布
"""

import os
import sys
import json
from typing import List, Dict, Any

sys.path.insert(0, '.')

# 加载环境变量
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from modules.logger import get_logger

logger = get_logger()

def fetch_from_producthunt() -> List[Dict]:
    """从 Product Hunt 获取产品"""
    logger.section("📡 从 Product Hunt 挖掘产品")
    
    from modules.sources.producthunt import Producthunt
    
    config = {
        'categories': ['AI', 'Developer Tools', 'Productivity'],
        'min_votes': 50,
        'time_period': 'daily',
        'max_candidates': 5
    }
    
    source = Producthunt(config)
    
    if not source.is_enabled():
        logger.error("❌ Product Hunt 模块未启用")
        return []
    
    candidates = source.discover()
    
    for c in candidates:
        c['source_name'] = 'Product Hunt'
    
    return candidates

def build_llm_task(candidate: Dict) -> str:
    """构建LLM任务"""
    name = candidate.get('name', '')
    tagline = candidate.get('tagline', '')
    description = candidate.get('description', '')
    votes = candidate.get('votes', 0)
    url = candidate.get('url', '')
    makers = candidate.get('makers', [])
    
    context_parts = [f"产品名称: {name}"]
    
    if tagline:
        context_parts.append(f"一句话描述: {tagline}")
    
    if description:
        context_parts.append(f"详细描述: {description[:400]}")
    
    if votes:
        context_parts.append(f"Product Hunt 投票数: {votes}")
    
    if makers:
        context_parts.append(f"制作者: {', '.join(makers[:3])}")
    
    context = "\n\n".join(context_parts)
    
    task = f"""请用自然叙述的方式介绍以下 Product Hunt 产品：

{context}

要求：
1. 不要列表、不要序号、不要用 bullet points
2. 禁止空话套话（如"针对痛点"、"功能设计"、"架构清晰"、"旨在解决"）
3. 像跟朋友推荐一个好产品一样口语化、流畅
4. 突出产品特点、亮点、为什么值得关注
5. 控制在400字以内
6. 直接输出内容，不要标题，不要"好的"、"明白"等确认词
7. 最后必须包含产品链接

产品链接: {url}"""
    
    return task

def main():
    """主流程"""
    logger.section("🎯 Product Hunt 流程启动")
    
    # 获取产品
    candidates = fetch_from_producthunt()
    
    if not candidates:
        logger.error("❌ 未获取到产品")
        return
    
    # 生成提示词（前3个用于测试）
    logger.section("📝 生成LLM提示词（前3个产品）")
    
    tasks = []
    for i, candidate in enumerate(candidates[:3], 1):
        name = candidate.get('name', '')
        logger.info(f"\n{i}. {name}")
        
        task = build_llm_task(candidate)
        tasks.append({
            'name': name,
            'url': candidate.get('url', ''),
            'task': task
        })
    
    # 保存到文件
    output_file = '/tmp/producthunt_tasks.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ 提示词已保存到: {output_file}")
    logger.info("\n请使用 sessions_spawn 调用大模型生成内容")
    
    # 显示第一个示例
    if tasks:
        logger.section(f"示例 - {tasks[0]['name']}:")
        print(tasks[0]['task'])
    
    return tasks

if __name__ == '__main__':
    main()
