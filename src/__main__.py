#!/usr/bin/env python3
"""
AiTrend - AI 热点资讯收集器
支持多渠道输出：Console、Discord、Feishu、Telegram
"""

import json
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sources import create_sources
from src.sources.base import Article
from src.core.deduplicator import ArticleDeduplicator
from src.core.config_loader import load_config, get_enabled_channels
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

def format_output(articles: List[Article]) -> Dict[str, Any]:
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
    
    return {
        "count": len(data),
        "articles": data
    }

def format_markdown(articles: List[Article], language: str = "zh") -> str:
    """格式化为 Markdown 格式，便于直接发送"""
    titles = {
        "zh": "🔥 今日 AI 热点",
        "en": "🔥 Today's AI Hotspots",
        "ja": "🔥 今日のAIホットニュース",
        "ko": "🔥 오늘의 AI 핫이슈",
        "es": "🔥 Tendencias de IA Hoy"
    }
    
    header = titles.get(language, titles["zh"])
    lines = [f"{header}\n", "═══════════════════\n"]
    
    for i, article in enumerate(articles[:10], 1):
        lines.append(f"{i}. **{article.title}**")
        lines.append(f"   {article.summary[:300]}...")
        lines.append(f"   🔗 {article.url}")
        lines.append(f"   📌 来源: {article.source}\n")
    
    lines.append("━━━━━━━━━━━━━━━")
    lines.append("🤖 由 AiTrend 自动生成")
    
    return "\n".join(lines)

def main():
    """主函数"""
    # 加载配置文件
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        print("请复制 config/config.example.json 到 config/config.json 并配置", file=sys.stderr)
        sys.exit(1)
    
    # 获取语言设置
    language = config.get("language", "zh")
    
    # 初始化去重器
    deduplicator = ArticleDeduplicator()
    
    # 收集数据
    articles = collect_data(config)
    
    # 去重：过滤掉24小时内已发送的文章
    articles = deduplicator.filter_new_articles(articles)
    
    # 额外去重：同一URL只保留一条
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    articles = unique_articles
    
    # 记录本次将要发送的文章
    deduplicator.record_sent_articles(articles)
    
    # 准备输出数据
    structured_data = format_output(articles)
    markdown_content = format_markdown(articles, language)
    
    # 获取启用的渠道
    channels_config = get_enabled_channels(config)
    
    # 如果没有配置任何渠道，默认使用 console
    if not channels_config:
        channels_config = {"console": {"enabled": True}}
    
    # 构建输出
    output = {
        "data": structured_data,
        "formatted_content": markdown_content,
        "language": language,
        "channels": list(channels_config.keys())
    }
    
    # 输出 JSON 格式（供 OpenClaw 处理）
    print(json.dumps(output, ensure_ascii=False))
    
    return output

if __name__ == '__main__':
    main()
