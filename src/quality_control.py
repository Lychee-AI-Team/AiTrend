#!/usr/bin/env python3
"""
AiTrend 质量控制系统 - 主流程
生成内容 → Subagent评审 → 优化循环 → 发布高分内容
"""

import json
import os
import sys
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
from src.hourly import select_best_articles, generate_unique_content, get_thread_title

REVIEW_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory', 'review_log.json')
SCORE_THRESHOLD = 8.0  # 高分阈值
MAX_ITERATIONS = 5     # 最大优化次数

def load_review_log() -> Dict:
    """加载评审日志"""
    try:
        with open(REVIEW_LOG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "review_sessions": [],
            "current_batch": {"batch_id": None, "articles": [], "reviews": [], "average_score": 0, "status": "pending"},
            "optimization_history": [],
            "threshold": SCORE_THRESHOLD
        }

def save_review_log(log: Dict):
    """保存评审日志"""
    with open(REVIEW_LOG_PATH, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def generate_batch(article_count: int = 5) -> List[Article]:
    """生成一批候选内容"""
    print(f"\n{'='*60}")
    print(f"🔄 生成新批次内容 (目标: {article_count} 条)")
    print('='*60)
    
    config = load_config()
    
    # 收集数据
    print("\n📡 收集数据源...")
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
                print(f"  ✓ {source.name}: {len(articles)} 条")
            except Exception as e:
                print(f"  ✗ {source.name}: {e}")
    
    print(f"\n📊 共收集 {len(all_articles)} 条")
    
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
    
    print(f"🔍 去重后: {len(articles)} 条")
    
    if len(articles) < article_count:
        print(f"⚠️ 可用内容不足 {article_count} 条，将生成 {len(articles)} 条")
        article_count = len(articles)
    
    # 选择最佳
    top_articles = select_best_articles(articles, top_n=article_count)
    
    print(f"\n⭐ 选中 {len(top_articles)} 条:")
    for i, article in enumerate(top_articles, 1):
        print(f"  {i}. [{article.source}] {article.title[:50]}...")
    
    return top_articles

def prepare_content_for_review(articles: List[Article]) -> List[Dict]:
    """准备内容供评审"""
    contents = []
    for article in articles:
        content = generate_unique_content(article)
        contents.append({
            "id": hash(article.url) % 10000,
            "title": get_thread_title(article),
            "original_title": article.title,
            "content": content,
            "url": article.url,
            "source": article.source,
            "metadata": article.metadata
        })
    return contents

def save_batch_for_review(contents: List[Dict]) -> str:
    """保存批次到日志，供subagent评审"""
    log = load_review_log()
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log["current_batch"] = {
        "batch_id": batch_id,
        "articles": contents,
        "reviews": [],
        "average_score": 0,
        "status": "pending_review",
        "created_at": datetime.now().isoformat()
    }
    
    save_review_log(log)
    
    # 同时保存到单独文件供subagent读取
    batch_file = os.path.join(os.path.dirname(__file__), '..', 'memory', f'batch_{batch_id}.json')
    with open(batch_file, 'w') as f:
        json.dump({"batch_id": batch_id, "contents": contents}, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 批次已保存: {batch_id}")
    print(f"📄 评审文件: {batch_file}")
    
    return batch_id

def check_reviews_complete(batch_id: str) -> bool:
    """检查评审是否完成"""
    log = load_review_log()
    if log["current_batch"]["batch_id"] != batch_id:
        return False
    return log["current_batch"]["status"] == "reviewed"

def get_average_score(batch_id: str) -> float:
    """获取平均评分"""
    log = load_review_log()
    if log["current_batch"]["batch_id"] != batch_id:
        return 0.0
    return log["current_batch"].get("average_score", 0.0)

def get_reviews(batch_id: str) -> List[Dict]:
    """获取评审详情"""
    log = load_review_log()
    if log["current_batch"]["batch_id"] != batch_id:
        return []
    return log["current_batch"].get("reviews", [])

def publish_high_score_contents(contents: List[Dict], reviews: List[Dict]):
    """发布高分内容到Discord"""
    print(f"\n{'='*60}")
    print("📤 发布高分内容到Discord")
    print('='*60)
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('DISCORD_WEBHOOK_URL='):
                    webhook_url = line.strip().split('=', 1)[1]
                    break
    
    sender = DiscordWebhookSender(webhook_url)
    published = 0
    
    for content, review in zip(contents, reviews):
        score = review.get('total_score', 0)
        if score >= SCORE_THRESHOLD:
            print(f"\n  ✅ 发布 (评分: {score}): {content['title'][:40]}...")
            result = sender.send_to_forum(content['title'], content['content'])
            if result:
                published += 1
                time.sleep(2)
        else:
            print(f"\n  ❌ 跳过 (评分: {score}): {content['title'][:40]}...")
    
    print(f"\n📈 发布完成: {published}/{len(contents)} 条")
    return published

def optimize_and_regenerate(weaknesses: List[str]) -> List[Article]:
    """根据弱点优化并重新生成"""
    print(f"\n{'='*60}")
    print("🔧 根据评审反馈优化策略")
    print('='*60)
    
    print("\n📋 评审发现的主要问题:")
    for i, weakness in enumerate(weaknesses[:5], 1):
        print(f"  {i}. {weakness}")
    
    print("\n📝 应用优化策略...")
    # 这里可以根据weaknesses调整生成参数
    # 例如：如果多次提到"缺少技术细节"，增加技术描述权重
    
    # 重新生成一批
    return generate_batch(article_count=5)

def print_review_summary(reviews: List[Dict]):
    """打印评审汇总"""
    print(f"\n{'='*60}")
    print("📊 评审结果汇总")
    print('='*60)
    
    total_score = 0
    for i, review in enumerate(reviews, 1):
        score = review.get('total_score', 0)
        total_score += score
        status = "✅ 高分" if score >= SCORE_THRESHOLD else "❌ 低分"
        print(f"\n  {i}. {status} {score}/10")
        print(f"     {review.get('title', 'Unknown')[:45]}...")
        print(f"     亮点: {', '.join(review.get('strengths', [])[:2])}")
        print(f"     问题: {', '.join(review.get('weaknesses', [])[:2])}")
    
    avg = total_score / len(reviews) if reviews else 0
    print(f"\n📈 平均分: {avg:.1f}/10")
    print(f"🎯 阈值: {SCORE_THRESHOLD}/10")
    print(f"📊 状态: {'✅ 达标' if avg >= SCORE_THRESHOLD else '❌ 未达标，需要优化'}")

def main():
    """主流程：生成 → 评审 → 优化循环 → 发布"""
    print("\n" + "="*60)
    print("🎯 AiTrend 质量控制系统启动")
    print("="*60)
    print(f"\n配置:")
    print(f"  • 评分阈值: {SCORE_THRESHOLD}/10")
    print(f"  • 最大优化次数: {MAX_ITERATIONS}")
    print(f"  • 每批生成: 5条内容")
    
    iteration = 0
    current_batch = None
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"🔄 第 {iteration}/{MAX_ITERATIONS} 轮迭代")
        print('='*60)
        
        # 步骤1: 生成内容
        if iteration == 1 or not current_batch:
            articles = generate_batch(article_count=5)
            current_batch = prepare_content_for_review(articles)
        else:
            # 优化后重新生成
            articles = optimize_and_regenerate(all_weaknesses)
            current_batch = prepare_content_for_review(articles)
        
        # 步骤2: 保存批次，等待评审
        batch_id = save_batch_for_review(current_batch)
        
        print(f"\n⏳ 等待Subagent完成评审...")
        print(f"💡 Subagent应读取: memory/batch_{batch_id}.json")
        print(f"💡 评审后保存到: memory/review_log.json")
        
        # 在实际运行中，这里会等待subagent完成
        # 为了演示，我们先模拟等待状态
        print(f"\n⚠️ 当前实现需要手动触发Subagent评审")
        print(f"⚠️ 请运行: python3 -m agents.reviewer {batch_id}")
        
        # 实际部署时会轮询检查
        # while not check_reviews_complete(batch_id):
        #     time.sleep(10)
        
        # 模拟：假设评审完成
        input("\n按Enter键模拟评审完成 (实际部署时会自动检测)...")
        
        # 步骤3: 检查评审结果
        avg_score = get_average_score(batch_id)
        reviews = get_reviews(batch_id)
        
        print_review_summary(reviews)
        
        # 步骤4: 判断是否达标
        if avg_score >= SCORE_THRESHOLD:
            print(f"\n✅ 评分达标！准备发布...")
            publish_high_score_contents(current_batch, reviews)
            break
        else:
            print(f"\n❌ 评分未达标，收集问题并优化...")
            all_weaknesses = []
            for review in reviews:
                all_weaknesses.extend(review.get('weaknesses', []))
            
            if iteration < MAX_ITERATIONS:
                print(f"\n🔄 进入下一轮优化...")
            else:
                print(f"\n⚠️ 已达到最大迭代次数，发布当前最高分内容...")
                publish_high_score_contents(current_batch, reviews)
    
    print(f"\n{'='*60}")
    print("✅ 质量控制系统运行完成")
    print('='*60)

if __name__ == '__main__':
    main()
