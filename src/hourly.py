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
import hashlib
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

def generate_ati_id() -> str:
    """生成 ATI 内容 ID - 格式: ATI-YYYYMMDD-[6字符十六进制]"""
    import hashlib
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    # 使用当前时间戳生成6字符十六进制哈希
    hash_input = f"{now.timestamp()}{random.randint(1000, 9999)}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:6].upper()
    return f"ATI-{date_str}-{short_hash}"

def generate_unique_content(article: Article, is_test: bool = False) -> str:
    """
    基于项目具体信息生成完全独特的内容
    使用LLM生成，禁止模板化文字
    
    Args:
        article: 文章数据
        is_test: 是否为测试模式，测试模式会添加ATI ID
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
    
    content = generator.generate(article_data)
    
    # 测试模式添加 ATI ID（与真实内容格式完全一致）
    if is_test:
        ati_id = generate_ati_id()
        # 将 ATI ID 添加到内容末尾（在URL之后）
        content = f"{content}\n\nATI ID: {ati_id}"
    
    return content

def post_single_article(article: Article, webhook_url: str, delay: int = 0, is_test: bool = False) -> bool:
    """发布单条文章到论坛
    
    Args:
        article: 文章数据
        webhook_url: Webhook URL
        delay: 延迟秒数
        is_test: 是否为测试模式
    """
    if delay > 0:
        time.sleep(delay)
    
    content = generate_unique_content(article, is_test=is_test)
    title = get_thread_title(article)
    
    sender = DiscordWebhookSender(webhook_url)
    result = sender.send_to_forum(title, content)
    
    return result

def main():
    """主函数
    
    支持参数:
        --test: 测试模式（跳过去重，添加ATI ID）
        python3 -m src.hourly --test
    """
    start_time = time.time()
    
    # 检查是否为测试模式或全量测试模式
    is_test_mode = '--test' in sys.argv or os.getenv('AITREND_TEST_MODE') == '1'
    is_full_test_mode = '--full-test' in sys.argv or os.getenv('AITREND_FULL_TEST_MODE') == '1'
    
    if is_full_test_mode:
        print("🧪🔥 AiTrend 全量测试模式（所有数据源，最大化输出，跳过去重）", file=sys.stderr)
    elif is_test_mode:
        print("🧪 AiTrend 测试模式（跳过去重，添加ATI ID）", file=sys.stderr)
    else:
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
    
    # 去重（测试模式跳过）
    deduplicator = ArticleDeduplicator()  # 始终创建，测试模式不使用
    if is_test_mode:
        articles = all_articles
        print(f"🧪 测试模式: 跳过去重检查", file=sys.stderr)
    else:
        articles = deduplicator.filter_new_articles(all_articles)
        print(f"🔍 去重后: {len(articles)} 条", file=sys.stderr)
    
    # URL去重（保持URL唯一性，即使是测试模式）
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article.url and article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)
    articles = unique_articles
    
    if not is_test_mode:
        print(f"🔍 去重后: {len(articles)} 条", file=sys.stderr)
    
    if not articles:
        print("⚠️ 无新内容", file=sys.stderr)
        sys.exit(0)
    
    # 选择文章（全量测试模式输出所有，普通模式限制数量）
    if is_full_test_mode:
        # 全量测试：输出所有收集到的内容（按热度排序）
        top_articles = select_best_articles(articles, top_n=len(articles))
        print(f"\n🔥 全量测试模式: 选中 {len(top_articles)} 条 (最大化输出)", file=sys.stderr)
    else:
        # 普通模式：选择最热门的3条，确保多样性
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
    
    if not is_full_test_mode:
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
    mode_str = ""
    if is_full_test_mode:
        mode_str = "全量测试"
    elif is_test_mode:
        mode_str = "测试"
    
    print(f"\n📤 正在发布{mode_str}内容...", file=sys.stderr)
    results = []
    
    for i, article in enumerate(top_articles):
        delay = i * 2
        # 全量测试或测试模式都添加ATI ID
        is_test_flag = is_test_mode or is_full_test_mode
        result = post_single_article(article, webhook_url, delay=delay, is_test=is_test_flag)
        results.append({
            'title': article.title[:40],
            'source': article.source,
            'success': result,
            'is_test': is_test_flag
        })
        status = "✅" if result else "❌"
        test_mark = " [TEST]" if is_test_flag else ""
        print(f"   {status} 第{i+1}条{test_mark}发布{'成功' if result else '失败'}", file=sys.stderr)
    
    # 记录已发送（测试模式不记录）
    if not is_test_mode and not is_full_test_mode:
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
