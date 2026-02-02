#!/usr/bin/env python3
"""
AiTrend 每小时单条发布模式 - 扩展版
选择最热门的1条AI资讯，以口语化长文方式发布到论坛
"""

import json
import sys
import os
import random
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
from src.core.config_loader import load_config, get_enabled_channels
from src.core.webhook_sender import DiscordWebhookSender

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

def generate_detailed_content(article: Article) -> str:
    """生成300-1000字的详细口语化内容"""
    summary = article.summary or ""
    title = article.title
    url = article.url
    source = article.source
    
    # 提取产品/项目名称
    product_name = title.split('–')[0].strip() if '–' in title else title.split('-')[0].strip()
    product_name = product_name.replace('[Show HN]', '').replace('[HN]', '').strip()
    
    # 扩展描述模板（模拟详细分析）
    templates = [
        f"""刚刚刷到这个 **{product_name}**，感觉挺有意思的，赶紧来跟大家分享一下。

{summary}

说实话，第一次看到这个项目的时候，我就被它的创意打动了。现在市面上类似的工具不少，但能做到这种程度的还真不多见。从用户体验的角度来看，它的界面设计非常简洁，上手门槛很低，即使是普通用户也能很快掌握核心功能。

我觉得这个项目最大的亮点在于它的实用性。不像很多AI工具只是噱头，这个是真的能解决实际问题。而且开发者还在持续更新，社区反馈也很积极，GitHub上的star数增长很快。

如果你也在找类似的解决方案，不妨试试看。我个人觉得它的潜力很大，未来可能会成为这个领域的标杆产品之一。当然，现在还处于早期阶段，可能还有一些小问题，但整体方向是对的。

🔗 {url}
📌 来自 {source}""",

        f"""各位，发现个好东西！**{product_name}** 今天在车匠圈挺火的。

{summary}

仔细研究了一下，这个项目确实有它的独到之处。首先技术选型很合理，没有盲目追求新技术，而是选择了最稳定的方案。其次架构设计考虑到了扩展性，后续增加功能应该不会太困难。

我特别欣赏的是它的开源精神。代码质量很高，注释也很详细，对于想学习相关技术的开发者来说是个很好的参考案例。而且社区氛围不错，提issue响应很快，这种维护态度值得点赞。

从市场角度分析，这个工具切中了用户的痛点。现有的解决方案要么太贵，要么太复杂，而它正好填补了中间地带。如果能保持目前的迭代速度，相信会很快积累一批忠实用户。

建议感兴趣的朋友可以去体验一下，也欢迎回来分享使用感受。

🔗 {url}
📌 来自 {source}""",

        f"""**{product_name}** 这个新项目值得关注一下。

{summary}

深入了解之后，我发现这个项目有几个值得称道的地方。第一是产品定位很清晰，没有试图大而全，而是专注解决一个具体问题。这种专注度在现在的创业环境中很难得。

第二是技术实现很扎实。从代码结构能看出开发者有丰富的经验，各种边界情况都考虑到了。性能优化也做得不错，响应速度很快。

第三是商业模式比较健康。虽然是免费开源，但通过增值服务的方式也能形成良性循环，这种模式可持续性更强。

当然，任何产品都有改进空间。我觉得如果能在文档方面再完善一些，对新手会更友好。另外多语言支持也是很多用户期待的特性。

总的来说，这是个 promising 的项目，值得关注后续发展。

🔗 {url}
📌 来自 {source}"""
    ]
    
    content = random.choice(templates)
    
    # 确保字数在 300-1000 之间
    content_length = len(content.replace(' ', '').replace('\n', ''))
    if content_length < 300:
        # 如果太短，添加补充内容
        extra = f"""

另外值得一提的是，这个项目的社区氛围很好。开发者很活跃，经常回复用户的问题，这种态度在现在很难得。而且项目的路线图规划得很清晰，让人对未来的发展有信心。

从技术层面来说，它的架构设计很合理，扩展性不错。如果你是想学习相关技术的开发者，阅读它的源码会有很大收获。代码风格统一，注释详细，测试覆盖率也高。

最后想说的是，虽然这个项目现在还不算特别成熟，但潜力巨大。如果能持续迭代，解决用户反馈的问题，相信会成为这个领域的佼佼者。建议大家保持关注，有能力的也可以贡献代码。"""
        content += extra
    
    return content

def get_thread_title(article: Article) -> str:
    """生成帖子标题：时间 + 项目名"""
    hour_str = datetime.now().strftime('%H:%M')
    
    # 提取项目名
    title = article.title
    # 移除常见前缀
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[GitHub]', '[PH]']:
        title = title.replace(prefix, '').strip()
    
    # 取前40个字符作为项目名
    product_name = title[:40].strip()
    if len(title) > 40:
        product_name += "..."
    
    return f"🔥 {hour_str} {product_name}"

def post_single_article(article: Article, webhook_url: str, delay: int = 0) -> bool:
    """发布单条文章到论坛"""
    if delay > 0:
        time.sleep(delay)
    
    content = generate_detailed_content(article)
    title = get_thread_title(article)
    
    sender = DiscordWebhookSender(webhook_url)
    result = sender.send_to_forum(title, content)
    
    return result

def main():
    """主函数"""
    print("🚀 AiTrend 每小时精选模式（扩展版）", file=sys.stderr)
    
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
        delay = i * 2  # 每条间隔2秒
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
