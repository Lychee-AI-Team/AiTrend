#!/usr/bin/env python3
"""
Product Hunt 流程 - 直接发布到论坛
禁止结构化描述，避免重复开头
"""

import os
import sys
import json
import time
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
from publishers import create_publisher

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

def generate_with_llm(candidate: Dict, index: int) -> str:
    """使用大模型生成内容 - 禁止结构化"""
    name = candidate.get('name', '')
    tagline = candidate.get('tagline', '')
    description = candidate.get('description', '')
    votes = candidate.get('votes', 0)
    url = candidate.get('url', '')
    makers = candidate.get('makers', [])
    
    logger.info(f"📝 生成内容: {name}")
    
    # 构建上下文
    context_parts = []
    
    if name:
        context_parts.append(f"产品名: {name}")
    
    if tagline:
        context_parts.append(f" Slogan: {tagline}")
    
    if description:
        context_parts.append(f"介绍: {description[:400]}")
    
    if votes:
        context_parts.append(f"投票: {votes}")
    
    if makers:
        context_parts.append(f"团队: {', '.join(makers[:2])}")
    
    context = "\n".join(context_parts)
    
    # 开头多样化提示
    opening_styles = [
        "直接切入产品",
        "从产品解决的问题切入", 
        "从使用场景切入",
        "从独特之处切入",
        "从对比传统方式切入"
    ]
    
    style = opening_styles[index % len(opening_styles)]
    
    task = f"""写一段产品介绍，基于以下信息：

{context}

核心要求（严格遵守）：
1. ❌ 禁止开头用"最近发现"、"今天看到"、"我找到一个"等套话
2. ❌ 禁止用第一第二、首先其次等序号
3. ❌ 禁止用列表符号（- * •）
4. ❌ 禁止重复用词和句式（重复性惩罚）
5. ❌ 禁止空话："针对痛点"、"功能设计"、"架构清晰"、"旨在解决"
6. ✅ 直接描述产品是什么、能做什么、为什么值得用
7. ✅ 连续段落，流畅自然
8. ✅ 控制在300字以内
9. ✅ 最后必须包含链接: {url}

开头风格提示: 使用"{style}"的方式开头"""
    
    # 使用 subprocess 调用 OpenClaw
    import subprocess
    import tempfile
    
    # 写入任务文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(task)
        task_file = f.name
    
    # 写入输出文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        output_file = f.name
    
    # 创建脚本调用 sessions_spawn
    script_content = f'''
import sys
sys.path.insert(0, '.')

with open("{task_file}", "r", encoding="utf-8") as f:
    task = f.read()

from tools import sessions_spawn

result = sessions_spawn(task=task, timeout_seconds=120)

with open("{output_file}", "w", encoding="utf-8") as f:
    f.write(result if result else "")

print("Done")
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_file = f.name
    
    # 执行
    try:
        result = subprocess.run(
            ['python3', script_file],
            capture_output=True,
            text=True,
            timeout=180,
            cwd='/home/ubuntu/.openclaw/workspace/AiTrend'
        )
        
        # 读取输出
        content = ""
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        
        # 清理
        for f in [task_file, output_file, script_file]:
            try:
                if os.path.exists(f):
                    os.unlink(f)
            except:
                pass
        
        if content:
            # 确保链接在内容中
            if url not in content:
                content = content.strip() + f"\n\n{url}"
            
            logger.info(f"   ✅ 生成成功 ({len(content)} 字符)")
            return content
        else:
            logger.error(f"   ❌ 生成失败: 无输出")
            return ""
            
    except Exception as e:
        logger.error(f"   ❌ 生成失败: {e}")
        return ""

def publish_contents(contents: List[Dict]) -> int:
    """直接发布到 Discord 论坛"""
    logger.section("📤 直接发布到 Discord 论坛")
    
    config = {
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
        'thread_name': '{name} – {source}',
        'username': 'AiTrend',
        'delay': 2
    }
    
    publisher = create_publisher('forum', config)
    
    if not publisher:
        logger.error("❌ 创建发布模块失败")
        return 0
    
    # 验证链接
    for content in contents:
        url = content.get('url', '')
        text = content.get('content', '')
        if url and url not in text:
            content['content'] = text.strip() + f"\n\n{url}"
    
    return publisher.publish_batch(contents)

def main():
    """主流程"""
    logger.section("🎯 Product Hunt 直接发布流程")
    
    # 1. 获取产品
    candidates = fetch_from_producthunt()
    
    if not candidates:
        logger.error("❌ 未获取到产品")
        return
    
    # 2. 生成内容（前3个）
    logger.section("📝 生成内容（禁止结构化描述）")
    
    generated_contents = []
    for i, candidate in enumerate(candidates[:3], 1):
        content_text = generate_with_llm(candidate, i-1)  # 传递索引用于多样化开头
        if content_text:
            generated_contents.append({
                'name': candidate.get('name', ''),
                'content': content_text,
                'url': candidate.get('url', ''),
                'source': 'Product Hunt'
            })
        time.sleep(2)
    
    logger.info(f"✅ 成功生成 {len(generated_contents)} 条内容")
    
    # 3. 直接发布到论坛（不发送到当前对话）
    if generated_contents:
        published = publish_contents(generated_contents)
        logger.section(f"✅ 流程完成！已发布 {published} 条到论坛")
    else:
        logger.warning("⚠️ 没有内容可发布")

if __name__ == '__main__':
    main()
