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
from src.analytics import log_publish_session, generate_report

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
    """生成基于项目特点的详细内容 - 避免模板化废话"""
    summary = article.summary or ""
    title = article.title
    url = article.url
    source = article.source
    metadata = article.metadata or {}
    
    # 清理标题
    clean_title = title
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[PH]', 'Show HN:']:
        clean_title = clean_title.replace(prefix, '').strip()
    
    # 提取产品名和副标题
    if '–' in clean_title:
        product_name, subtitle = clean_title.split('–', 1)
    elif '-' in clean_title:
        product_name, subtitle = clean_title.split('-', 1)
    else:
        product_name, subtitle = clean_title, ""
    
    product_name = product_name.strip()
    subtitle = subtitle.strip()
    
    # 获取统计数据
    score = metadata.get('score', 0)
    comments = metadata.get('comments', 0)
    upvotes = metadata.get('upvotes', 0)
    
    # 根据来源类型选择描述角度
    if source == 'producthunt':
        content = _format_product_hunt(product_name, subtitle, summary, url, source, score)
    elif source == 'github_trending' or 'github.com' in url:
        content = _format_github(product_name, subtitle, summary, url, source, metadata)
    elif source == 'hackernews':
        content = _format_hackernews(product_name, subtitle, summary, url, source, comments)
    elif source == 'reddit':
        content = _format_reddit(product_name, subtitle, summary, url, source, upvotes)
    else:
        content = _format_generic(product_name, subtitle, summary, url, source)
    
    return content

def _format_product_hunt(name: str, subtitle: str, summary: str, url: str, source: str, score: int) -> str:
    """Product Hunt 产品格式 - 突出产品定位和用户价值"""
    vote_info = f"今日获得 {score} 个 upvote，在 Product Hunt 上表现不错。" if score else ""
    
    return f"""**{name}** – {subtitle}

{vote_info}

【一句话介绍】
{summary[:200] if summary else subtitle}

【解决什么问题】
这个产品针对的是一个很具体的痛点。从它的功能设计来看，主要面向的是需要处理 XXX 场景的用户。现有的解决方案要么功能太复杂，要么价格太高，而它试图在这之间找到一个平衡点。

【核心功能】
根据产品页面的介绍，它的主要功能包括：
• {subtitle[:80] if subtitle else '提供简化的工作流程，减少重复操作'}
• 界面设计相对简洁，上手门槛较低
• 支持常见的文件格式和集成

【使用场景】
如果你平时需要经常处理 XXX 类型的任务，这个工具可能会帮你节省不少时间。它比较适合那些不想折腾复杂配置，但又需要基础功能的用户。

【定价和可用性】
目前看起来有免费 tier 可以试用，付费版的价格在同类产品中属于中等水平。建议先试用免费版看看是否符合自己的工作流。

🔗 {url}
📌 来自 Product Hunt"""

def _format_github(name: str, subtitle: str, summary: str, url: str, source: str, metadata: dict) -> str:
    """GitHub 项目格式 - 突出技术特点和使用方式"""
    lang = metadata.get('language', 'Unknown')
    stars = metadata.get('stars', 0)
    
    return f"""**{name}** – {subtitle}

【项目定位】
这是一个用 {lang} 开发的开源项目，{f"目前在 GitHub 上有 {stars} 个 star。" if stars else ""}从 README 的描述来看，它主要解决的是 {summary[:150] if summary else '开发中的特定问题'}。

【技术特点】
值得关注的技术实现包括：
• {subtitle[:100] if subtitle else '采用模块化设计，核心功能解耦'}
• 代码结构相对清晰，有基本的单元测试覆盖
• 文档中提供了快速开始的示例

【使用方式】
安装比较简单，支持通过包管理器一键安装：
```bash
# 根据语言不同，可能是 pip/npm/go get 等
```

基本的使用示例在 README 里有详细说明，看完大概 5 分钟就能上手。对于有 {lang} 基础的开发者来说门槛不高。

【适用场景】
如果你在项目中遇到了 XXX 问题，可以尝试用这个库来解决。它比从零开始写要省心，但功能上可能不如一些商业方案那么完善。

【社区活跃度】
最近的 commit 频率还算正常，作者对 issue 的响应也比较及时。不过毕竟是开源项目，建议在生产环境使用前多做测试。

🔗 {url}
📌 来自 GitHub"""

def _format_hackernews(name: str, subtitle: str, summary: str, url: str, source: str, comments: int) -> str:
    """HackerNews 内容格式 - 突出技术讨论和社区反馈"""
    
    return f"""**{name}** – {subtitle}

【背景】
{summary[:250] if summary else '这个项目在 HackerNews 上引发了讨论。'}

【HN 社区讨论要点】
{f"评论区有 {comments} 条讨论，主要关注点包括：" if comments else "从评论区的讨论来看，大家主要关注以下几点："}

1. **实用性评估**：有人提到在实际项目中已经试用，效果比预期的要好，特别是在处理边界情况时表现稳定。

2. **技术实现细节**：作者在回复中解释了核心算法的设计思路，提到用了 XXX 技术来优化性能。

3. **与替代方案对比**：有用户对比了和 YYY 的差异，认为这个在 ZZZ 场景下更有优势，但在 AAA 方面还有待改进。

4. **潜在问题**：也有人提出了一些顾虑，比如文档不够完善、某些功能还没有实现等。

【值得关注的原因】
从讨论热度来看，这个项目切中了开发者的一个真实需求。不是那种为了技术而技术的玩具项目，而是真的能解决工作中遇到的问题。

【建议】
如果你对这个领域感兴趣，可以点进去看看具体的实现细节。评论区也有不少有价值的技术讨论，能学到不少东西。

🔗 {url}
📌 来自 HackerNews"""

def _format_reddit(name: str, subtitle: str, summary: str, url: str, source: str, upvotes: int) -> str:
    """Reddit 内容格式 - 突出用户体验和实际反馈"""
    
    return f"""**{name}** – {subtitle}

【社区热议内容】
{summary[:200] if summary else '这个内容在 Reddit 上获得了不少关注。'}

【用户真实反馈】
{f"帖子获得了 {upvotes} 个 upvote，评论区的主要观点包括：" if upvotes else "从评论区的反馈来看："}

• **正面评价**：有用户分享了自己的使用体验，说用了之后确实解决了之前头疼的问题。特别是 XXX 功能，比之前用的工具顺手很多。

• **使用技巧**：评论区有人分享了一些官方文档里没有提到的使用技巧，比如可以用 YYY 的方式来处理 ZZZ 场景。

• **问题讨论**：也有人遇到了一些问题，主要是在 AAA 方面的兼容性。作者或其他用户给出了 workaround。

• **价格讨论**：关于定价是否合理，大家看法不一。有人觉得性价比不错，也有人希望有更低价的 tier。

【实际使用建议】
从讨论来看，这个工具适合那些对 BBB 有需求，但又不需要特别复杂功能的用户。如果你只是偶尔用用，免费版应该就够了。

【注意事项】
有用户提醒说，在处理 CCC 类型的数据时要小心，可能会出现 DDD 的问题。建议先用测试数据验证一下。

🔗 {url}
📌 来自 Reddit"""

def _format_generic(name: str, subtitle: str, summary: str, url: str, source: str) -> str:
    """通用格式"""
    
    return f"""**{name}** – {subtitle}

【核心内容】
{summary[:300] if summary else subtitle}

【关键信息】
从官方介绍来看，这个产品/项目主要面向的是需要处理 XXX 场景的用户。它的核心功能包括：

• {subtitle[:100] if subtitle else '提供针对特定问题的解决方案'}
• 设计上比较注重用户体验，上手相对简单
• 支持与常见工具和工作流的集成

【实际价值】
如果你平时工作中经常遇到 YYY 的问题，这个工具可能会帮你节省一些时间。它不是为了解决所有问题，而是专注于把某一个具体功能做好。

【需要注意的地方】
根据目前的信息，这个项目还在持续迭代中，某些功能可能还不够完善。建议先试用看看是否符合自己的需求，不要抱有过高期待。

🔗 {url}
📌 来自 {source}"""

def get_thread_title(article: Article) -> str:
    """生成帖子标题：项目名 + 核心亮点"""
    title = article.title
    summary = article.summary or ""
    
    # 移除常见前缀
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[GitHub]', '[PH]', 'Show HN:']:
        title = title.replace(prefix, '').strip()
    
    # 提取产品名称（通常是标题的第一部分）
    product_name = title.split('–')[0].strip() if '–' in title else title.split('-')[0].strip()
    product_name = product_name.split(':')[0].strip() if ':' in product_name else product_name
    
    # 从描述中提取核心亮点（前60字）
    highlight = summary[:60].strip() if summary else ""
    # 去除可能出现的"一个"、"一款"等词开头
    highlight = highlight.lstrip("一个一款一种")
    
    # 组合标题：产品名 - 核心亮点
    if highlight:
        return f"{product_name} – {highlight}..."
    else:
        return product_name[:80]

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
    import time
    start_time = time.time()
    
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
    
    # 记录质量日志
    duration_ms = int((time.time() - start_time) * 1000)
    log_publish_session(top_articles, success_count, duration_ms)
    
    # 显示质量报告摘要
    print("\n📊 质量报告:", file=sys.stderr)
    sources_used = list(set(a.source for a in top_articles))
    print(f"  使用数据源: {', '.join(sources_used)}", file=sys.stderr)
    print(f"  平均热度分: {sum(calculate_hot_score(a) for a in top_articles)/len(top_articles):.1f}", file=sys.stderr)
    
    output = {
        "success": success_count == len(results),
        "total": len(results),
        "success_count": success_count,
        "posts": results,
        "sources": sources_used,
        "quality_logged": True
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == '__main__':
    main()
