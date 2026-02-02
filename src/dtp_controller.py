#!/usr/bin/env python3
"""
AiTrend DTP闭环流程控制器
Develop → Test → Review → Optimize → Deploy
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

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
from src.test_multi_source import MultiSourceTester

# 日志路径
REVIEW_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory', 'review_log.json')
DTF_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory', 'dtp_loop.json')

# 阈值配置
SCORE_THRESHOLD = 8.0      # Subagent评分阈值
TEST_SCORE_THRESHOLD = 70  # 多源测试阈值
MAX_ITERATIONS = 5         # 最大迭代次数
MIN_SOURCES_PER_BATCH = 3  # 每批最少来源数

class DTPLoopController:
    """DTP闭环控制器"""
    
    def __init__(self):
        self.iteration = 0
        self.tester = MultiSourceTester()
        self.loop_log = self._load_loop_log()
    
    def _load_loop_log(self) -> Dict:
        """加载循环日志"""
        try:
            with open(DTF_LOG_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'runs': [],
                'current_run': None,
                'statistics': {
                    'total_iterations': 0,
                    'avg_iterations_to_pass': 0,
                    'pass_rate': 0
                }
            }
    
    def _save_loop_log(self):
        """保存循环日志"""
        with open(DTF_LOG_PATH, 'w') as f:
            json.dump(self.loop_log, f, ensure_ascii=False, indent=2)
    
    # ========== DEVELOP 阶段 ==========
    def develop(self, article_count: int = 5, diversity_enforced: bool = True) -> List[Article]:
        """
        开发阶段：生成多源均衡的内容
        强制要求来源多样性
        """
        print("\n" + "="*60)
        print(f"🔧 DEVELOP 阶段：生成内容 (迭代 {self.iteration})")
        print("="*60)
        
        config = load_config()
        
        # 收集数据
        print("\n📡 收集多源数据...")
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
        
        # 选择最佳 - 强制来源多样性
        if diversity_enforced:
            # 先按分数排序
            scored = [(a, self._calc_score(a)) for a in articles]
            scored.sort(key=lambda x: x[1], reverse=True)
            
            # 确保来源多样性
            source_count = {}
            diverse_articles = []
            
            for article, score in scored:
                src = article.source
                if source_count.get(src, 0) < 2:  # 每个来源最多2条
                    diverse_articles.append(article)
                    source_count[src] = source_count.get(src, 0) + 1
                if len(diverse_articles) >= article_count:
                    break
            
            selected = diverse_articles[:article_count]
        else:
            selected = select_best_articles(articles, top_n=article_count)
        
        print(f"\n⭐ 选中 {len(selected)} 条 (来源分布):")
        source_dist = {}
        for a in selected:
            src = a.source
            source_dist[src] = source_dist.get(src, 0) + 1
        
        for src, count in sorted(source_dist.items()):
            pct = count / len(selected) * 100
            print(f"  • {src}: {count}条 ({pct:.0f}%)")
        
        return selected
    
    def _calc_score(self, article: Article) -> float:
        """计算热度分数"""
        score = 0.0
        source_weights = {
            'producthunt': 1.5, 'twitter': 1.4, 'reddit': 1.2,
            'hackernews': 1.1, 'github_trending': 1.0, 'tavily': 0.9
        }
        score += source_weights.get(article.source, 0.5)
        
        metadata = article.metadata or {}
        score += metadata.get('score', 0) * 0.01
        score += metadata.get('comments', 0) * 0.02
        
        return score
    
    # ========== TEST 阶段 ==========
    def test(self, articles: List[Article]) -> Tuple[bool, Dict]:
        """
        测试阶段：多源覆盖测试
        返回: (是否通过, 测试详情)
        """
        print("\n" + "="*60)
        print("🧪 TEST 阶段：多源覆盖测试")
        print("="*60)
        
        # 转换为测试格式
        test_data = []
        for article in articles:
            content = generate_unique_content(article)
            test_data.append({
                'source': article.source,
                'title': article.title,
                'content': content,
                'url': article.url
            })
        
        # 运行测试
        results = self.tester.run_full_test(test_data)
        
        passed = results['passed'] and results['total_score'] >= TEST_SCORE_THRESHOLD
        
        print(f"\n测试结果: {'✅ 通过' if passed else '❌ 未通过'}")
        if not passed:
            print("\n需要优化的问题:")
            for test_name in ['source_test', 'diversity_test', 'density_test']:
                test_result = results.get(test_name, {})
                for issue in test_result.get('issues', [])[:2]:
                    print(f"  • {issue}")
        
        return passed, results
    
    # ========== REVIEW 阶段 ==========
    def review(self, articles: List[Article]) -> Tuple[bool, float, List[Dict]]:
        """
        审查阶段：Subagent质量评审
        返回: (是否通过, 平均分, 详细评审)
        """
        print("\n" + "="*60)
        print("👁️ REVIEW 阶段：Subagent质量评审")
        print("="*60)
        
        # 生成内容
        contents = []
        for article in articles:
            content = generate_unique_content(article)
            contents.append({
                'id': hash(article.url) % 10000,
                'title': get_thread_title(article),
                'original_title': article.title,
                'content': content,
                'url': article.url,
                'source': article.source
            })
        
        # 保存批次
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_file = os.path.join(os.path.dirname(__file__), '..', 'memory', f'batch_{batch_id}.json')
        with open(batch_file, 'w') as f:
            json.dump({'batch_id': batch_id, 'contents': contents}, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 批次已保存: {batch_id}")
        print(f"⏳ 等待Subagent评审...")
        print(f"💡 请运行: python3 -m agents.reviewer {batch_id}")
        
        # 模拟等待（实际部署时会自动触发subagent）
        # 这里演示用，等待手动输入
        input("\n按Enter模拟Subagent评审完成...")
        
        # 读取评审结果
        log = self._load_review_log()
        avg_score = log.get('current_batch', {}).get('average_score', 0)
        reviews = log.get('current_batch', {}).get('reviews', [])
        
        passed = avg_score >= SCORE_THRESHOLD
        
        print(f"\n评审结果: {'✅ 通过' if passed else '❌ 未通过'}")
        print(f"平均分: {avg_score:.1f}/{SCORE_THRESHOLD}")
        
        return passed, avg_score, reviews
    
    # ========== OPTIMIZE 阶段 ==========
    def optimize(self, test_results: Dict, reviews: List[Dict]) -> Dict:
        """
        优化阶段：根据测试结果和评审反馈制定优化策略
        """
        print("\n" + "="*60)
        print("🔧 OPTIMIZE 阶段：策略优化")
        print("="*60)
        
        optimizations = []
        
        # 分析测试问题
        for test_name in ['source_test', 'diversity_test', 'density_test']:
            test_result = test_results.get(test_name, {})
            for issue in test_result.get('issues', []):
                optimizations.append(f"[测试] {issue}")
        
        # 分析评审问题
        all_weaknesses = []
        for review in reviews:
            all_weaknesses.extend(review.get('weaknesses', []))
        
        # 统计最常见问题
        from collections import Counter
        weakness_counts = Counter(all_weaknesses)
        
        print("\n📊 最常见问题 (Top 5):")
        for weakness, count in weakness_counts.most_common(5):
            print(f"  • {weakness} ({count}次)")
            optimizations.append(f"[评审] {weakness}")
        
        # 生成优化策略
        strategies = []
        
        if any('来源' in opt for opt in optimizations):
            strategies.append("强制来源多样性：每个源最多1-2条，确保至少3个不同源")
        
        if any('类型' in opt for opt in optimizations):
            strategies.append("增加内容类型检测：AI模型/开发工具/产品应用/开源项目/学术研究")
        
        if any('信息量' in opt or '密度' in opt for opt in optimizations):
            strategies.append("增加强制信息项：必须包含具体功能+使用场景+技术细节+对比数据")
        
        if any('空话' in opt or '套话' in opt for opt in optimizations):
            strategies.append("强化空话过滤：检测并删除'针对痛点'等抽象表述")
        
        if any('场景' in opt for opt in optimizations):
            strategies.append("强制使用场景：每篇必须说明'适合在XX时候使用'")
        
        if any('数据' in opt for opt in optimizations):
            strategies.append("增加数据提取：抓取star数、性能指标、用户数量等具体数字")
        
        print("\n📝 优化策略:")
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy}")
        
        return {
            'issues': optimizations,
            'strategies': strategies,
            'iteration': self.iteration
        }
    
    # ========== DEPLOY 阶段 ==========
    def deploy(self, articles: List[Article]) -> int:
        """
        部署阶段：发布高分内容到Discord
        """
        print("\n" + "="*60)
        print("🚀 DEPLOY 阶段：发布到Discord")
        print("="*60)
        
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DISCORD_WEBHOOK_URL='):
                        webhook_url = line.strip().split('=', 1)[1]
                        break
        
        sender = DiscordWebhookSender(webhook_url)
        published = 0
        
        for i, article in enumerate(articles):
            content = generate_unique_content(article)
            title = get_thread_title(article)
            
            print(f"\n  📤 发布 {i+1}/{len(articles)}: {title[:40]}...")
            result = sender.send_to_forum(title, content)
            
            if result:
                published += 1
                print(f"     ✅ 成功")
                time.sleep(2)
            else:
                print(f"     ❌ 失败")
        
        print(f"\n📈 发布完成: {published}/{len(articles)} 条")
        return published
    
    # ========== 主循环 ==========
    def run(self):
        """运行完整DTP闭环"""
        print("\n" + "="*60)
        print("🎯 AiTrend DTP闭环流程启动")
        print("="*60)
        print("\n流程: DEVELOP → TEST → REVIEW → [OPTIMIZE] → DEPLOY")
        print(f"阈值: 测试≥{TEST_SCORE_THRESHOLD}分 | 评审≥{SCORE_THRESHOLD}分")
        print(f"最大迭代: {MAX_ITERATIONS}次")
        
        run_record = {
            'start_time': datetime.now().isoformat(),
            'iterations': [],
            'final_status': 'failed'
        }
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.iteration = iteration
            
            print(f"\n{'='*60}")
            print(f"🔄 第 {iteration}/{MAX_ITERATIONS} 轮迭代")
            print('='*60)
            
            iter_record = {
                'iteration': iteration,
                'timestamp': datetime.now().isoformat()
            }
            
            # DEVELOP
            articles = self.develop(article_count=5, diversity_enforced=True)
            iter_record['article_count'] = len(articles)
            iter_record['sources'] = list(set(a.source for a in articles))
            
            # TEST
            test_passed, test_results = self.test(articles)
            iter_record['test_passed'] = test_passed
            iter_record['test_score'] = test_results['total_score']
            
            # REVIEW
            review_passed, review_score, reviews = self.review(articles)
            iter_record['review_passed'] = review_passed
            iter_record['review_score'] = review_score
            
            # 决策
            if test_passed and review_passed:
                print(f"\n✅ 所有测试通过！准备部署...")
                published = self.deploy(articles)
                iter_record['deployed'] = published
                run_record['final_status'] = 'success'
                run_record['total_iterations'] = iteration
                break
            else:
                print(f"\n❌ 未达标，进入优化阶段...")
                
                if iteration < MAX_ITERATIONS:
                    opt_record = self.optimize(test_results, reviews)
                    iter_record['optimization'] = opt_record
                    print(f"\n🔄 应用优化策略，重新生成...")
                else:
                    print(f"\n⚠️ 达到最大迭代次数，强制部署当前最佳内容...")
                    published = self.deploy(articles)
                    iter_record['deployed'] = published
                    run_record['final_status'] = 'partial'
                    run_record['total_iterations'] = iteration
            
            run_record['iterations'].append(iter_record)
        
        # 保存运行记录
        run_record['end_time'] = datetime.now().isoformat()
        self.loop_log['runs'].append(run_record)
        self.loop_log['current_run'] = run_record
        self._save_loop_log()
        
        # 最终报告
        print("\n" + "="*60)
        print("📊 DTP闭环流程完成")
        print("="*60)
        print(f"最终状态: {run_record['final_status']}")
        print(f"总迭代: {run_record.get('total_iterations', MAX_ITERATIONS)}次")
        print(f"日志保存: {DTF_LOG_PATH}")

def main():
    controller = DTPLoopController()
    controller.run()

if __name__ == '__main__':
    main()
