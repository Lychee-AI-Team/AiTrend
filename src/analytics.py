#!/usr/bin/env python3
"""
AiTrend 发布日志分析工具
用于观察发布内容质量和来源分布
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'memory', 'sent_articles.json')
QUALITY_LOG = os.path.join(os.path.dirname(__file__), '..', 'memory', 'publish_quality.json')

def load_logs():
    """加载发布日志"""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"articles": []}

def load_quality_log():
    """加载质量日志"""
    try:
        with open(QUALITY_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"sessions": []}

def analyze_sources(articles):
    """分析来源分布"""
    sources = defaultdict(int)
    for article in articles:
        # 从标题或URL推断来源
        title = article.get('title', '')
        url = article.get('url', '')
        
        if 'Product Hunt' in title or 'producthunt' in url.lower():
            sources['Product Hunt'] += 1
        elif 'HackerNews' in title or 'news.ycombinator' in url:
            sources['HackerNews'] += 1
        elif 'github' in url.lower():
            sources['GitHub'] += 1
        elif 'reddit' in url.lower():
            sources['Reddit'] += 1
        elif 'tavily' in str(article.get('metadata', {})).lower():
            sources['Tavily'] += 1
        else:
            sources['Other'] += 1
    
    return sources

def analyze_time_distribution(articles):
    """分析时间分布"""
    hours = defaultdict(int)
    for article in articles:
        sent_time = datetime.fromtimestamp(article['sent_at'])
        hour_key = sent_time.strftime('%H:00')
        hours[hour_key] += 1
    
    return sorted(hours.items())

def generate_report():
    """生成分析报告"""
    data = load_logs()
    articles = data.get('articles', [])
    
    print("📊 AiTrend 发布质量报告")
    print("=" * 70)
    print(f"\n📈 总计发布: {len(articles)} 条")
    
    # 24小时统计
    twenty_four_hours_ago = datetime.now().timestamp() - 86400
    recent_articles = [a for a in articles if a['sent_at'] > twenty_four_hours_ago]
    print(f"📅 24小时内: {len(recent_articles)} 条")
    
    # 7天统计
    seven_days_ago = datetime.now().timestamp() - 604800
    week_articles = [a for a in articles if a['sent_at'] > seven_days_ago]
    print(f"📆 7天内: {len(week_articles)} 条")
    
    # 来源分析
    print("\n📌 来源分布:")
    sources = analyze_sources(articles)
    total = sum(sources.values())
    for source, count in sorted(sources.items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"  {source:15} {count:3}条 ({pct:5.1f}%) {bar}")
    
    # 时间分布（最近24小时）
    if recent_articles:
        print("\n🕐 今日发布时段:")
        hours = defaultdict(int)
        for a in recent_articles:
            sent_time = datetime.fromtimestamp(a['sent_at'])
            hour_key = sent_time.strftime('%H:00')
            hours[hour_key] += 1
        
        for hour, count in sorted(hours.items()):
            bar = "●" * count
            print(f"  {hour}: {bar} ({count})")
    
    # 最近发布详情
    print("\n📝 最近5条发布:")
    for article in articles[-5:]:
        sent_time = datetime.fromtimestamp(article['sent_at']).strftime('%m-%d %H:%M')
        title = article['title'][:45] + "..." if len(article['title']) > 45 else article['title']
        print(f"  {sent_time} | {title}")
    
    # 重复内容检查
    urls = [a['url'] for a in articles]
    duplicates = len(urls) - len(set(urls))
    if duplicates > 0:
        print(f"\n⚠️ 重复内容: {duplicates} 条")
    else:
        print("\n✅ 无重复内容")
    
    # 质量评分（基于标题长度和来源多样性）
    avg_title_len = sum(len(a['title']) for a in articles) / len(articles) if articles else 0
    source_diversity = len(sources) / len(articles) * 100 if articles else 0
    
    print(f"\n📊 质量指标:")
    print(f"  平均标题长度: {avg_title_len:.0f} 字符")
    print(f"  来源多样性: {len(sources)} 个来源")
    print(f"  平均发布频率: {len(articles) / max(len(set([datetime.fromtimestamp(a['sent_at']).strftime('%Y-%m-%d') for a in articles])), 1):.1f} 条/天")
    
    print("\n" + "=" * 70)

def log_publish_session(articles, success_count, duration_ms):
    """记录发布会话"""
    quality_data = load_quality_log()
    
    session = {
        "timestamp": datetime.now().isoformat(),
        "total_selected": len(articles),
        "success_count": success_count,
        "duration_ms": duration_ms,
        "sources": list(set(a.source for a in articles)),
        "titles": [a.get('title', '') for a in articles]
    }
    
    quality_data["sessions"].append(session)
    
    # 只保留最近30天的记录
    thirty_days_ago = datetime.now() - timedelta(days=30)
    quality_data["sessions"] = [
        s for s in quality_data["sessions"]
        if datetime.fromisoformat(s["timestamp"]) > thirty_days_ago
    ]
    
    with open(QUALITY_LOG, 'w', encoding='utf-8') as f:
        json.dump(quality_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    generate_report()
