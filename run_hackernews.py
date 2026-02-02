#!/usr/bin/env python3
"""
HackerNews 流程 - 直接发布到论坛
"""

import os
import sys
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

def fetch_from_hackernews() -> List[Dict]:
    """从 HackerNews 获取热门帖子"""
    logger.section("📡 从 HackerNews 挖掘热门帖子")
    
    from modules.sources.hackernews import Hackernews
    
    config = {
        'min_points': 100,
        'min_comments': 20,
        'max_candidates': 5,
        'keywords': ['AI', 'machine learning', 'open source', 'github', 'developer']
    }
    
    source = Hackernews(config)
    candidates = source.discover()
    
    for c in candidates:
        c['source_name'] = 'HackerNews'
    
    return candidates

def build_prompt(candidate: Dict, index: int) -> str:
    """构建LLM提示词"""
    name = candidate.get('name', '')
    title = candidate.get('title', '')
    url = candidate.get('url', '')
    hn_url = candidate.get('hn_url', '')
    points = candidate.get('points', 0)
    comments = candidate.get('comments', 0)
    top_comments = candidate.get('top_comments', [])
    
    # 构建上下文
    context_parts = [f"标题: {title}"]
    
    if points:
        context_parts.append(f"HackerNews 分数: {points}")
    
    if comments:
        context_parts.append(f"评论数: {comments}")
    
    if top_comments:
        context_parts.append(f"热评: {top_comments[0][:200]}")
    
    context = "\n".join(context_parts)
    
    # 多样化开头
    styles = ["直接切入式", "从讨论热度切入", "从社区反馈切入"]
    style = styles[index % len(styles)]
    
    return f"""介绍以下 HackerNews 热门帖子：

{context}

要求：
1. ❌ 禁止"最近发现"、"今天看到"等套话开头
2. ❌ 禁止第一第二、首先其次等序号
3. ❌ 禁止列表符号（- * •）
4. ❌ 禁止重复用词
5. ❌ 禁止空话：针对痛点、功能设计、架构清晰、旨在解决
6. ✅ 直接描述项目是什么、HN社区为什么关注它
7. ✅ 提及HN讨论的价值（如评论观点）
8. ✅ 连续段落，300字以内
9. ✅ 最后必须包含项目链接和HN讨论链接

项目链接: {url}
HN讨论: {hn_url}

开头风格: {style}"""

def generate_contents(candidates: List[Dict]) -> List[Dict]:
    """使用大模型生成内容"""
    logger.section("📝 生成内容（前3个帖子）")
    
    generated = []
    
    for i, candidate in enumerate(candidates[:3], 1):
        name = candidate.get('name', '')
        logger.info(f"\n{i}. {name}")
        
        prompt = build_prompt(candidate, i-1)
        
        # 调用大模型（使用 subprocess）
        import subprocess
        import tempfile
        
        # 写入任务文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            task_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            output_file = f.name
        
        # 创建脚本
        script_content = f'''
import sys
sys.path.insert(0, '.')

with open("{task_file}", "r", encoding="utf-8") as f:
    task = f.read()

from tools import sessions_spawn

result = sessions_spawn(task=task, timeout_seconds=120)

with open("{output_file}", "w", encoding="utf-8") as f:
    f.write(result if result else "")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            script_file = f.name
        
        # 执行
        try:
            subprocess.run(
                ['python3', script_file],
                capture_output=True,
                text=True,
                timeout=180,
                cwd='/home/ubuntu/.openclaw/workspace/AiTrend'
            )
            
            with open(output_file, 'r', encoding='utf-8') as f:
                result = f.read().strip()
            
            # 清理
            for f in [task_file, output_file, script_file]:
                try:
                    if os.path.exists(f):
                        os.unlink(f)
                except:
                    pass
        except Exception as e:
            logger.error(f"   调用失败: {e}")
            result = ""
        
        if result:
            # 确保链接在内容中
            url = candidate.get('url', '')
            hn_url = candidate.get('hn_url', '')
            
            if url and url not in result:
                result += f"\n\n项目: {url}"
            if hn_url and hn_url not in result:
                result += f"\nHN讨论: {hn_url}"
            
            logger.info(f"   ✅ 生成成功 ({len(result)} 字符)")
            generated.append({
                'name': name,
                'content': result,
                'url': url,
                'source': 'HackerNews'
            })
        else:
            logger.error(f"   ❌ 生成失败")
        
        time.sleep(2)
    
    return generated

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
    
    return publisher.publish_batch(contents)

def main():
    """主流程"""
    logger.section("🎯 HackerNews 流程启动")
    
    # 1. 获取帖子
    candidates = fetch_from_hackernews()
    
    if not candidates:
        logger.error("❌ 未获取到帖子")
        return
    
    # 2. 生成内容
    generated = generate_contents(candidates)
    
    logger.info(f"\n✅ 成功生成 {len(generated)} 条内容")
    
    # 3. 直接发布到论坛
    if generated:
        published = publish_contents(generated)
        logger.section(f"✅ 流程完成！已发布 {published} 条到论坛")
    else:
        logger.warning("⚠️ 没有内容可发布")

if __name__ == '__main__':
    main()
