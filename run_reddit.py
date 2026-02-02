#!/usr/bin/env python3
"""
Reddit 流程 - 直接发布到论坛
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

def fetch_from_reddit() -> List[Dict]:
    """从 Reddit (Pushshift) 获取热门帖子"""
    logger.section("📡 从 Reddit (Pushshift) 挖掘热门帖子")
    
    from modules.sources.reddit import Reddit
    
    config = {
        'subreddits': ['MachineLearning', 'LocalLLaMA', 'artificial', 'technology'],
        'min_upvotes': 50,
        'min_comments': 10,
        'max_candidates': 5,
        'time_window': 7
    }
    
    source = Reddit(config)
    candidates = source.discover()
    
    for c in candidates:
        c['source_name'] = 'Reddit'
    
    return candidates

def build_prompt(candidate: Dict, index: int) -> str:
    """构建LLM提示词"""
    name = candidate.get('name', '')
    title = candidate.get('title', '')
    url = candidate.get('url', '')
    reddit_url = candidate.get('reddit_url', '')
    upvotes = candidate.get('upvotes', 0)
    comments = candidate.get('comments', 0)
    subreddit = candidate.get('subreddit', '')
    top_comments = candidate.get('top_comments', [])
    
    # 构建上下文
    context_parts = [f"标题: {title}"]
    
    if upvotes:
        context_parts.append(f"Reddit 投票: {upvotes}")
    
    if comments:
        context_parts.append(f"评论数: {comments}")
    
    if subreddit:
        context_parts.append(f"社区: r/{subreddit}")
    
    if top_comments:
        context_parts.append(f"热评: {top_comments[0][:200]}")
    
    context = "\n".join(context_parts)
    
    # 多样化开头
    styles = ["从社区反响切入", "从实际用途切入", "从技术亮点切入"]
    style = styles[index % len(styles)]
    
    return f"""介绍以下 Reddit 热门帖子：

{context}

要求：
1. ❌ 禁止"最近发现"、"今天看到"等套话开头
2. ❌ 禁止第一第二、首先其次等序号
3. ❌ 禁止列表符号（- * •）
4. ❌ 禁止重复用词
5. ❌ 禁止空话：针对痛点、功能设计、架构清晰、旨在解决
6. ✅ 直接描述内容是什么、Reddit社区为什么讨论它
7. ✅ 提及r/{subreddit}社区的特点
8. ✅ 连续段落，300字以内
9. ✅ 最后必须包含内容链接和Reddit讨论链接

内容链接: {url}
Reddit讨论: {reddit_url}

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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            task_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            output_file = f.name
        
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
            
            for f in [task_file, output_file, script_file]:
                try:
                    if os.path.exists(f):
                        os.unlink(f)
                except:
                    pass
            
            if result:
                url = candidate.get('url', '')
                reddit_url = candidate.get('reddit_url', '')
                
                if url and url not in result:
                    result += f"\n\n{url}"
                if reddit_url and reddit_url not in result:
                    result += f"\nReddit: {reddit_url}"
                
                logger.info(f"   ✅ 生成成功 ({len(result)} 字符)")
                generated.append({
                    'name': name,
                    'content': result,
                    'url': url,
                    'source': 'Reddit'
                })
            else:
                logger.error(f"   ❌ 生成失败: 无输出")
        except Exception as e:
            logger.error(f"   ❌ 生成失败: {e}")
        
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
    logger.section("🎯 Reddit 流程启动")
    
    # 1. 获取帖子
    candidates = fetch_from_reddit()
    
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
