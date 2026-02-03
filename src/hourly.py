#!/usr/bin/env python3
"""
AiTrend 每小时单条发布模式 - 完全独特叙述版
每篇内容基于项目具体信息生成，确保独特性
"""

import json
import sys
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from src.sources import create_sources
from src.sources.base import Article
from src.core.deduplicator import ArticleDeduplicator
from src.core.config_loader import load_config
from src.core.webhook_sender import DiscordWebhookSender

def collect_all_sources(config: Dict[str, Any]) -> List[Article]:
    """从所有数据源收集文章，每个数据源最多 30 秒"""
    import signal
    
    sources_config = config.get("sources", {})
    sources = create_sources(sources_config)
    
    all_articles = []
    for source in sources:
        if source.is_enabled():
            articles = []
            try:
                # 使用信号设置硬性超时（仅 Unix/Linux）
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"{source.name} 超时")
                
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)  # 30 秒超时
                
                try:
                    articles = source.fetch()
                finally:
                    signal.alarm(0)  # 取消闹钟
                    signal.signal(signal.SIGALRM, old_handler)
                
                for article in articles:
                    article.metadata['collector_source'] = source.name
                all_articles.extend(articles)
                print(f"✓ {source.name}: {len(articles)} 条", file=sys.stderr)
            except TimeoutError as e:
                print(f"✗ {source.name}: 超时 (30s)", file=sys.stderr)
            except Exception as e:
                print(f"✗ {source.name}: {e}", file=sys.stderr)
    
    return all_articles

def calculate_hot_score(article: Article) -> float:
    """计算热度分数"""
    score = 0.0
    
    source_weights = {
        'producthunt': 1.5,
        'twitter': 1.4,
        'reddit': 1.2,
        'hackernews': 1.1,
        'github_trending': 1.0,
        'tavily': 0.9
    }
    score += source_weights.get(article.source, 0.5)
    
    metadata = article.metadata or {}
    score += metadata.get('score', 0) * 0.01
    score += metadata.get('comments', 0) * 0.02
    score += metadata.get('upvotes', 0) * 0.01
    
    try:
        if 'published_at' in metadata:
            pub_time = datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00'))
            hours_ago = (datetime.now(pub_time.tzinfo) - pub_time).total_seconds() / 3600
            if hours_ago < 1:
                score += 2.0
            elif hours_ago < 6:
                score += 1.0
            elif hours_ago < 24:
                score += 0.5
    except:
        pass
    
    return score

def select_best_articles(articles: List[Article], top_n: int = 3) -> List[Article]:
    """选择最热门的多条"""
    scored_articles = [(article, calculate_hot_score(article)) for article in articles]
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    return [a[0] for a in scored_articles[:top_n]]

def get_thread_title(article: Article) -> str:
    """生成帖子标题"""
    title = article.title
    summary = article.summary or ""
    
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[GitHub]', '[PH]', 'Show HN:']:
        title = title.replace(prefix, '').strip()
    
    product_name = title.split('–')[0].strip() if '–' in title else title.split('-')[0].strip()
    product_name = product_name.split(':')[0].strip() if ':' in product_name else product_name
    
    # 从summary提取核心功能（前50字）
    highlight = summary[:50].strip() if summary else ""
    highlight = highlight.lstrip("一个一款一种是用可以")
    
    if highlight:
        return f"{product_name} – {highlight}..."
    else:
        return product_name[:80]

def generate_unique_content(article: Article) -> str:
    """
    基于项目具体信息生成完全独特的内容
    使用LLM生成，禁止模板化文字
    """
    from .llm_content_generator import get_llm_generator
    
    # 使用LLM生成独特内容
    generator = get_llm_generator()
    
    article_data = {
        'title': article.title,
        'summary': article.summary or '',
        'url': article.url,
        'source': article.source,
        'metadata': article.metadata or {}
    }
    
    return generator.generate(article_data)

def post_single_article(article: Article, webhook_url: str, delay: int = 0) -> bool:
    """发布单条文章到论坛"""
    if delay > 0:
        time.sleep(delay)
    
    content = generate_unique_content(article)
    title = get_thread_title(article)
    
    sender = DiscordWebhookSender(webhook_url)
    result = sender.send_to_forum(title, content)
    
    return result

def main():
    """主函数"""
    start_time = time.time()
    
    print("🚀 AiTrend 每小时精选模式（完全独特叙述版）", file=sys.stderr)
    
    # 加载配置
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 收集数据
    print("\n📡 正在收集各数据源...", file=sys.stderr)
    all_articles = collect_all_sources(config)
    print(f"\n📊 共收集 {len(all_articles)} 条", file=sys.stderr)
    
    if not all_articles:
        print("⚠️ 无数据", file=sys.stderr)
        sys.exit(0)
    
    # 去重
    deduplicator = ArticleDeduplicator()
    articles = deduplicator.filter_new_articles(all_articles)
    
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    articles = unique_articles
    
    print(f"🔍 去重后: {len(articles)} 条", file=sys.stderr)
    
    if not articles:
        print("⚠️ 无新内容", file=sys.stderr)
        sys.exit(0)
    
    # 选择最热门的3条，确保多样性（优先不同来源）
    top_articles = select_best_articles(articles, top_n=5)  # 先选5条
    
    # 确保来源多样性
    source_count = {}
    diverse_articles = []
    for article in top_articles:
        src = article.source
        if source_count.get(src, 0) < 2:  # 每个来源最多2条
            diverse_articles.append(article)
            source_count[src] = source_count.get(src, 0) + 1
        if len(diverse_articles) >= 3:
            break
    
    top_articles = diverse_articles[:3]
    
    print(f"\n⭐ 选中 {len(top_articles)} 条 (已优化来源多样性):", file=sys.stderr)
    for i, article in enumerate(top_articles, 1):
        print(f"   {i}. [{article.source}] {article.title[:45]}...", file=sys.stderr)
    
    # 获取 Webhook URL
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DISCORD_WEBHOOK_URL='):
                    webhook_url = line.strip().split('=', 1)[1]
                    break
    
    # 发布到论坛
    print(f"\n📤 正在发布...", file=sys.stderr)
    results = []
    
    for i, article in enumerate(top_articles):
        delay = i * 2
        result = post_single_article(article, webhook_url, delay=delay)
        results.append({
            'title': article.title[:40],
            'source': article.source,
            'success': result
        })
        status = "✅" if result else "❌"
        print(f"   {status} 第{i+1}条发布{'成功' if result else '失败'}", file=sys.stderr)
    
    # 记录已发送
    deduplicator.record_sent_articles(top_articles)
    
    # 输出结果
    success_count = sum(1 for r in results if r['success'])
    print(f"\n📈 发布完成: {success_count}/{len(results)} 条成功", file=sys.stderr)
    
    output = {
        "success": success_count == len(results),
        "total": len(results),
        "success_count": success_count,
        "posts": results
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == '__main__':
    main()
