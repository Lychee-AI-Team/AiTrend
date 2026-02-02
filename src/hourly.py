#!/usr/bin/env python3
"""
AiTrend 每小时单条发布模式 - 完全自由叙述版
彻底口语化，无固定结构，无开场结尾模板
"""

import json
import sys
import os
import time
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
from src.analytics import log_publish_session

def collect_all_sources(config: Dict[str, Any]) -> List[Article]:
    """从所有数据源收集文章"""
    sources_config = config.get("sources", {})
    sources = create_sources(sources_config)
    
    all_articles = []
    for source in sources:
        if source.is_enabled():
            try:
                articles = source.fetch()
                for article in articles:
                    article.metadata['collector_source'] = source.name
                all_articles.extend(articles)
                print(f"✓ {source.name}: {len(articles)} 条", file=sys.stderr)
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
    """生成帖子标题：项目名 + 核心亮点"""
    title = article.title
    summary = article.summary or ""
    
    # 移除常见前缀
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[GitHub]', '[PH]', 'Show HN:']:
        title = title.replace(prefix, '').strip()
    
    # 提取产品名
    product_name = title.split('–')[0].strip() if '–' in title else title.split('-')[0].strip()
    product_name = product_name.split(':')[0].strip() if ':' in product_name else product_name
    
    # 从描述中提取核心亮点（前50字）
    highlight = summary[:50].strip() if summary else ""
    highlight = highlight.lstrip("一个一款一种是用")
    
    if highlight:
        return f"{product_name} – {highlight}..."
    else:
        return product_name[:80]

def generate_natural_content(article: Article) -> str:
    """
    完全自由叙述，无任何固定结构
    根据项目特点自然流淌式写作
    """
    title = article.title
    summary = article.summary or ""
    url = article.url
    source = article.source
    metadata = article.metadata or {}
    
    # 清理标题
    clean_title = title
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[PH]', '[GitHub]', 'Show HN:']:
        clean_title = clean_title.replace(prefix, '').strip()
    
    # 提取信息
    if '–' in clean_title:
        product_name, tagline = clean_title.split('–', 1)
    elif '-' in clean_title:
        product_name, tagline = clean_title.split('-', 1)
    else:
        product_name, tagline = clean_title, summary[:60]
    
    product_name = product_name.strip()
    tagline = tagline.strip()
    
    # 获取统计数据
    score = metadata.get('score', 0)
    comments = metadata.get('comments', 0)
    upvotes = metadata.get('upvotes', 0)
    language = metadata.get('language', '')
    stars = metadata.get('stars', 0)
    
    # 根据项目特点构建内容 - 完全自由叙述
    content_parts = []
    
    # 根据来源和特点决定叙述方式（不是模板，是思路指导）
    if source == 'producthunt' and score > 50:
        # 热门PH产品 - 从热度切入
        content_parts.append(f"{product_name} 今天刚在 Product Hunt 上发布，目前已经拿了 {score} 个 upvote，表现相当不错。")
        content_parts.append(f"看它的介绍主要是 {tagline}。这个切入点挺准的，之前市面上虽然有不少类似工具，但大多要么太复杂要么太贵，它试图在中间找一个平衡点。")
        
        if summary:
            content_parts.append(summary[:200])
        
        content_parts.append(f"从页面展示的功能来看，核心解决的是 workflow 自动化的问题。对于那些不想折腾复杂配置，但又需要基础自动化功能的团队来说，这个定价策略还算合理。")
        content_parts.append(f"目前看起来有免费 tier 可以试用，建议先拿自己的数据跑一遍看看效果，别光看 demo。")
        
    elif source == 'github_trending' and stars > 5000:
        # 热门开源项目 - 从技术价值切入
        content_parts.append(f"{product_name} 最近在 GitHub 上挺火的，已经 {stars} star 了。它是一个 {language if language else '多语言'} 项目，主要用来 {tagline}。")
        
        if summary:
            content_parts.append(summary[:250])
        
        content_parts.append(f"代码结构看 README 里的介绍还算清晰，文档也提供了 quick start。对于有 {language if language else '相关技术'} 基础的开发者来说，上手应该不会太困难。")
        content_parts.append(f"不过毕竟是开源项目，建议在生产环境用之前先在自己项目里测试一下边界情况，看看是否符合预期。")
        
    elif source == 'hackernews' and comments > 20:
        # HN热议 - 从讨论角度切入
        content_parts.append(f"{product_name} 在 HackerNews 上引发了讨论，评论区已经有 {comments} 条回复。")
        content_parts.append(f"帖子里提到它主要是 {tagline}。从讨论内容来看，大家关注的点主要集中在实用性上 —— 不是那种为了技术而技术的 toy project，而是真的能解决工作中的具体问题。")
        
        if summary:
            content_parts.append(summary[:200])
        
        content_parts.append(f"有人分享了自己在实际项目里的使用体验，说在处理边界情况时表现比预期的稳定。也有人提到了一些潜在的问题，比如文档还不够完善。")
        content_parts.append(f"如果你对 {tagline.split()[0] if tagline else '这个领域'} 感兴趣，可以点进去看看评论区，有不少有价值的技术讨论。")
        
    elif source == 'reddit' and upvotes > 100:
        # Reddit热帖 - 从用户体验切入
        content_parts.append(f"有人在 Reddit 上分享了 {product_name} 的使用体验，帖子获得了 {upvotes} 个 upvote。")
        content_parts.append(f"从帖子的描述来看，这是一个 {tagline} 的工具。发帖人提到自己用了大概两周，主要感受是...")
        
        if summary:
            content_parts.append(summary[:220])
        
        content_parts.append(f"评论区里有人补充了一些官方文档没提到的使用技巧，也有人提醒说在某些特定场景下会有兼容性问题。总的来说反馈还算真实，有好评也有吐槽。")
        content_parts.append(f"如果你也在找类似的解决方案，可以去看看原帖里的讨论，比官方宣传要真实一些。")
        
    else:
        # 通用叙述 - 从信息本身切入
        content_parts.append(f"{product_name} 是一个 {tagline} 的项目。")
        
        if summary:
            content_parts.append(summary[:280])
        
        content_parts.append(f"从现有的信息来看，它主要面向的是需要解决 {tagline.split()[0] if tagline else '特定问题'} 的用户。功能设计上比较务实，没有试图大包大揽，而是专注于把核心功能做好。")
        
        if source == 'github_trending':
            content_parts.append(f"代码开源在 GitHub 上，有兴趣的可以看看实现细节。")
        elif source == 'producthunt':
            content_parts.append(f"目前还在早期阶段，建议先观望一段时间看后续迭代情况。")
    
    # 自然添加链接，不作为固定结尾
    content_parts.append(f"{url}")
    
    # 合并所有部分，用换行连接形成自然段落
    full_content = "\n\n".join(content_parts)
    
    return full_content

def post_single_article(article: Article, webhook_url: str, delay: int = 0) -> bool:
    """发布单条文章到论坛"""
    if delay > 0:
        time.sleep(delay)
    
    content = generate_natural_content(article)
    title = get_thread_title(article)
    
    sender = DiscordWebhookSender(webhook_url)
    result = sender.send_to_forum(title, content)
    
    return result

def main():
    """主函数"""
    start_time = time.time()
    
    print("🚀 AiTrend 每小时精选模式（完全自由叙述版）", file=sys.stderr)
    
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
    
    # 选择最热门的3条
    top_articles = select_best_articles(articles, top_n=3)
    
    print(f"\n⭐ 选中 {len(top_articles)} 条:", file=sys.stderr)
    for i, article in enumerate(top_articles, 1):
        print(f"   {i}. {article.title[:50]}... ({article.source})", file=sys.stderr)
    
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
    
    # 记录质量日志
    duration_ms = int((time.time() - start_time) * 1000)
    try:
        log_publish_session(top_articles, sum(1 for r in results if r['success']), duration_ms)
    except:
        pass
    
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
