#!/usr/bin/env python3
"""
AiTrend - 纯数据收集器
输出结构化 AI 热点数据，供 OpenClaw 处理和总结
"""

import json
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sources import create_sources
from src.sources.base import Article
from src.core.deduplicator import ArticleDeduplicator
from typing import List, Dict, Any

def collect_data(config: Dict[str, Any]) -> List[Article]:
    """从所有数据源收集数据"""
    sources_config = config.get("sources", {})
    sources = create_sources(sources_config)
    
    all_articles = []
    for source in sources:
        if source.is_enabled():
            try:
                articles = source.fetch()
                all_articles.extend(articles)
            except Exception as e:
                print(f"数据源 {source.name} 错误: {e}", file=sys.stderr)
    
    return all_articles

def format_output(articles: List[Article]) -> str:
    """格式化为结构化输出"""
    data = []
    for article in articles[:20]:  # 最多20条
        data.append({
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "metadata": article.metadata
        })
    
    return json.dumps({
        "count": len(data),
        "articles": data
    }, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    # 读取配置
    config = {
        "sources": {
            "reddit": {"enabled": True},
            "hackernews": {"enabled": True},
            "github_trending": {
                "enabled": True,
                "languages": ["python", "typescript", "rust", "go"]
            },
            "tavily": {
                "enabled": True,
                "api_key": os.getenv("TAVILY_API_KEY", ""),
                "queries": [
                    "latest AI tools launch 2026",
                    "new AI models released this week"
                ]
            },
            "twitter": {"enabled": False},
            "producthunt": {"enabled": False}
        }
    }
    
    # 初始化去重器
    deduplicator = ArticleDeduplicator()
    
    # 收集数据
    articles = collect_data(config)
    
    # 去重：过滤掉24小时内已发送的文章
    articles = deduplicator.filter_new_articles(articles)
    
    # 额外去重：同一URL只保留一条（基于本次收集的数据）
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    articles = unique_articles
    
    # 记录本次将要发送的文章
    deduplicator.record_sent_articles(articles)
    
    # 输出去重后的数据
    output = format_output(articles)
    print(output)

if __name__ == '__main__':
    main()
