#!/usr/bin/env python3
"""
AiTrend 每小时单条发布模式
选择最热门的1条AI资讯，以口语化方式发布到论坛
"""

import json
import sys
import os
import random
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sources import create_sources
from src.sources.base import Article
from src.core.deduplicator import ArticleDeduplicator
from src.core.config_loader import load_config
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
                # 标记来源
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
    
    # 基础分：根据来源权重
    source_weights = {
        'producthunt': 1.5,  # 新产品优先级高
        'twitter': 1.4,
        'reddit': 1.2,
        'hackernews': 1.1,
        'github_trending': 1.0,
        'tavily': 0.9
    }
    score += source_weights.get(article.source, 0.5)
    
    # 互动分
    metadata = article.metadata or {}
    score += metadata.get('score', 0) * 0.01  # HN/Reddit 分数
    score += metadata.get('comments', 0) * 0.02  # 评论权重更高
    score += metadata.get('upvotes', 0) * 0.01
    
    # 时效性：越新越好
    try:
        if 'published_at' in metadata:
            pub_time = datetime.fromisoformat(metadata['published_at'].replace('Z', '+00:00'))
            hours_ago = (datetime.now(pub_time.tzinfo) - pub_time).total_seconds() / 3600
            if hours_ago < 1:
                score += 2.0  # 1小时内 +2分
            elif hours_ago < 6:
                score += 1.0  # 6小时内 +1分
            elif hours_ago < 24:
                score += 0.5  # 24小时内 +0.5分
    except:
        pass
    
    return score

def select_best_article(articles: List[Article]) -> Article:
    """选择最热门的单条"""
    # 计算每条的热度
    scored_articles = [(article, calculate_hot_score(article)) for article in articles]
    
    # 按分数排序
    scored_articles.sort(key=lambda x: x[1], reverse=True)
    
    # 返回最高分
    return scored_articles[0][0] if scored_articles else None

def format_casual_content(article: Article) -> str:
    """格式化为口语化内容"""
    date_str = datetime.now().strftime('%m-%d')
    hour_str = datetime.now().strftime('%H:%M')
    
    # 口语化开场
    openings = [
        f"刚刚发现个有意思的！{article.title}",
        f"这个挺火的，{article.title}",
        f"各位看看这个～ {article.title}",
        f"新鲜出炉！{article.title}",
        f"这个值得关注：{article.title}",
    ]
    
    opening = random.choice(openings)
    
    # 正文描述（口语化）
    summary = article.summary or ""
    if len(summary) > 400:
        summary = summary[:400] + "..."
    
    # 构建内容
    lines = [
        f"🔥 **{opening}**",
        "",
        summary,
        "",
        f"🔗 {article.url}",
        f"📌 来自 {article.source}",
        "",
        f"_发布时间：{hour_str} | AiTrend 每小时精选_"
    ]
    
    return "\n".join(lines)

def main():
    """主函数"""
    print("🚀 AiTrend 每小时精选模式", file=sys.stderr)
    
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
        print("⚠️ 无数据，跳过本次", file=sys.stderr)
        sys.exit(0)
    
    # 去重
    deduplicator = ArticleDeduplicator()
    articles = deduplicator.filter_new_articles(all_articles)
    
    # 过滤：24小时内已发的不重复
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    articles = unique_articles
    
    print(f"🔍 去重后: {len(articles)} 条", file=sys.stderr)
    
    if not articles:
        print("⚠️ 无新内容，跳过本次", file=sys.stderr)
        sys.exit(0)
    
    # 选择最热门的一条
    best_article = select_best_article(articles)
    
    if not best_article:
        print("⚠️ 无法选择最佳文章", file=sys.stderr)
        sys.exit(1)
    
    print(f"\n⭐ 选中: {best_article.title}", file=sys.stderr)
    print(f"   来源: {best_article.source}", file=sys.stderr)
    
    # 记录已发送
    deduplicator.record_sent_articles([best_article])
    
    # 格式化内容
    content = format_casual_content(best_article)
    
    # 获取 Webhook URL
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DISCORD_WEBHOOK_URL='):
                    webhook_url = line.strip().split('=', 1)[1]
                    break
    
    # 发布到论坛
    print(f"\n📤 正在发布到论坛...", file=sys.stderr)
    sender = DiscordWebhookSender(webhook_url)
    
    date_str = datetime.now().strftime('%m-%d')
    hour_str = datetime.now().strftime('%H:%M')
    thread_title = f"🔥 {hour_str} AI 热点"
    
    result = sender.send_to_forum(thread_title, content)
    
    if result:
        print(f"✅ 成功发布！", file=sys.stderr)
        # 输出JSON供调用者使用
        output = {
            "success": True,
            "title": best_article.title,
            "source": best_article.source,
            "url": best_article.url,
            "published_at": f"{date_str} {hour_str}"
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        print(f"❌ 发布失败", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
