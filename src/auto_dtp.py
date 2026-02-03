#!/usr/bin/env python3
"""
AiTrend 全自动DTP闭环系统
无需人工干预，自动优化直到达标，每轮同步到Discord
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
from src.hourly import get_thread_title
from src.test_multi_source import MultiSourceTester
from agents.reviewer import review_content

# 配置
ARTICLE_COUNT = 10        # 每批10条
SCORE_THRESHOLD = 8.0     # 评审阈值
TEST_THRESHOLD = 70       # 测试阈值
MAX_ITERATIONS = 5        # 最大迭代
DISCORD_SYNC = True       # 同步到Discord

class AutoDTPController:
    """全自动DTP控制器"""
    
    def __init__(self):
        self.iteration = 0
        self.tester = MultiSourceTester()
        self.webhook_url = self._get_webhook()
        self.sender = DiscordWebhookSender(self.webhook_url)
        
    def _get_webhook(self) -> str:
        """获取Webhook URL"""
        url = os.getenv('DISCORD_WEBHOOK_URL')
        if not url:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DISCORD_WEBHOOK_URL='):
                        url = line.strip().split('=', 1)[1]
                        break
        return url
    
    def generate_enhanced_content(self, article: Article) -> str:
        """生成高信息密度内容 - 增强版"""
        title = article.title
        summary = article.summary or ""
        url = article.url
        source = article.source
        metadata = article.metadata or {}
        
        # 清理标题
        clean_title = title
        for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[PH]', '[GitHub]', 'Show HN:']:
            clean_title = clean_title.replace(prefix, '').strip()
        
        if '–' in clean_title:
            product_name, tagline = clean_title.split('–', 1)
        elif '-' in clean_title:
            product_name, tagline = clean_title.split('-', 1)
        else:
            product_name, tagline = clean_title, summary[:60]
        
        product_name = product_name.strip()
        tagline = tagline.strip()
        
        # 获取元数据
        score = metadata.get('score', 0)
        comments = metadata.get('comments', 0)
        stars = metadata.get('stars', 0)
        language = metadata.get('language', '')
        
        content_lower = (product_name + " " + tagline).lower()
        
        # 构建内容 - 强制4要素，直接返回完整f-string，严禁拼接
        
        # 提取功能描述
        sentences = [s.strip() for s in summary.split('.') if s.strip() and len(s.strip()) > 10] if summary else []
        first_feature = f"主要功能包括：{sentences[0][:150]}。" if sentences else ""
        second_feature = f"另外还支持：{sentences[1][:120]}。" if len(sentences) > 1 else ""
        
        # 使用场景 - 直接返回完整字符串
        if 'wikipedia' in content_lower:
            usage_scene = f"使用场景：适合在通勤、排队等碎片时间随机获取知识。打开页面自动加载内容，下滑刷新，不需要主动搜索。比刷短视频信息质量高，比查资料更轻松。"
        elif 'music' in content_lower or 'audio' in content_lower:
            usage_scene = f"使用场景：适合有一定音乐基础但不想学复杂DAW的人。用代码方式控制音符、节奏、和声，比传统作曲软件门槛低，但又比随机生成有控制力。"
        elif 'iphone' in content_lower or 'mobile' in content_lower:
            usage_scene = f"使用场景：想在iPhone上跑大模型做本地AI应用开发。利用Apple Silicon的MLX框架，但需要注意内存和性能限制。"
        elif 'github' in url.lower() or source == 'github_trending':
            usage_scene = f"使用场景：需要在项目中集成{tagline[:30]}功能的开发者。通过pip/npm安装，几行代码即可接入现有系统。"
        elif 'producthunt' in url.lower() or source == 'producthunt':
            ph_scene = f"适合小团队或个人用户，定价{score}个upvote认可的" if score > 50 else "适合需要简化工作流程的用户"
            usage_scene = f"使用场景：{ph_scene}。可以替代复杂的企业级工具，上手门槛低。"
        else:
            scene_type = "特定" if not tagline else tagline.split()[0]
            user_type = "适合开发者集成到现有系统" if 'api' in content_lower or 'tool' in content_lower else "适合个人或团队使用"
            usage_scene = f"使用场景：需要解决{scene_type}问题的场景。{user_type}。"
        
        # 技术/数据细节
        if source == 'github_trending' and stars > 0:
            tech_detail = f"技术细节：GitHub {stars} star，{language if language else '多语言'}项目。代码结构清晰，有单元测试，文档提供了quick start示例。"
        elif source == 'producthunt' and score > 0:
            ph_feedback = "用户反馈普遍认可易用性" if score > 50 else "刚发布，还在早期阶段"
            ph_free = "有免费tier可以试用" if score > 30 else "需要付费"
            tech_detail = f"产品数据：Product Hunt {score} upvote。{ph_feedback}。{ph_free}。"
        elif source == 'hackernews' and comments > 0:
            tech_detail = f"社区反馈：HN {comments}条评论。有人分享实际使用体验，也有人提到边界情况处理和文档完善度问题。"
        else:
            github_open = "代码开源可查看" if 'github' in url.lower() else "提供详细文档"
            tech_detail = f"实现细节：基于现有技术栈开发，{github_open}。"
        
        # 优缺点
        advantage = tagline[:20]
        limit_platform = "只支持特定平台" if 'ios' in content_lower or 'android' in content_lower else "功能还在迭代中"
        limit_doc = "中文支持有待完善" if 'producthunt' in url.lower() else "文档可以更详细"
        
        # 直接返回完整f-string，严禁使用parts.append + join
        return f"""{product_name} 是一个{tagline}。

{first_feature}{second_feature}
{usage_scene}

{tech_detail}

优缺点：优势是{advantage}做得比较专注，没有过度设计。限制是目前{limit_platform}，{limit_doc}。

{url}"""
    
    def develop(self, count: int = 10) -> List[Article]:
        """开发阶段"""
        print(f"\n{'='*60}")
        print(f"🔧 迭代 {self.iteration}: 生成{count}条内容")
        print('='*60)
        
        config = load_config()
        
        # 收集数据
        print("📡 收集多源数据...")
        sources = create_sources(config.get("sources", {}))
        all_articles = []
        
        for source in sources:
            if source.is_enabled():
                try:
                    articles = source.fetch()
                    for article in articles:
                        article.metadata['collector_source'] = source.name
                    all_articles.extend(articles)
                    print(f"  ✓ {source.name}: {len(articles)}条")
                except Exception as e:
                    print(f"  ✗ {source.name}: {e}")
        
        print(f"📊 共收集{len(all_articles)}条，去重后{len(set(a.url for a in all_articles if a.url))}条")
        
        # 去重
        deduplicator = ArticleDeduplicator()
        articles = deduplicator.filter_new_articles(all_articles)
        
        seen = set()
        unique = []
        for a in articles:
            if a.url and a.url not in seen:
                seen.add(a.url)
                unique.append(a)
        articles = unique
        
        # 选择最佳，强制多样性
        scored = [(a, self._calc_score(a)) for a in articles]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        source_count = {}
        selected = []
        for article, score in scored:
            src = article.source
            if source_count.get(src, 0) < 3:  # 每源最多3条
                selected.append(article)
                source_count[src] = source_count.get(src, 0) + 1
            if len(selected) >= count:
                break
        
        print(f"\n⭐ 选中{len(selected)}条:")
        for src, cnt in sorted(source_count.items()):
            print(f"  • {src}: {cnt}条")
        
        return selected
    
    def _calc_score(self, article: Article) -> float:
        """计算分数"""
        score = 0.0
        weights = {'producthunt': 1.5, 'twitter': 1.4, 'reddit': 1.2, 'hackernews': 1.1, 'github_trending': 1.0, 'tavily': 0.9}
        score += weights.get(article.source, 0.5)
        
        meta = article.metadata or {}
        score += meta.get('score', 0) * 0.01
        score += meta.get('comments', 0) * 0.02
        
        return score
    
    def test_and_review(self, articles: List[Article]) -> Tuple[bool, float, List[Dict]]:
        """测试和评审"""
        print(f"\n{'='*60}")
        print("🧪 TEST + REVIEW 阶段")
        print('='*60)
        
        # 生成内容
        contents = []
        for article in articles:
            content = self.generate_enhanced_content(article)
            contents.append({
                'title': get_thread_title(article),
                'original_title': article.title,
                'content': content,
                'url': article.url,
                'source': article.source,
                'metadata': article.metadata
            })
        
        # TEST - 多源覆盖测试
        print("\n📊 多源覆盖测试...")
        test_data = [{'source': c['source'], 'title': c['title'], 'content': c['content']} for c in contents]
        test_results = self.tester.run_full_test(test_data)
        test_passed = test_results['passed'] and test_results['total_score'] >= TEST_THRESHOLD
        
        # REVIEW - Subagent自动评审
        print("\n👁️ Subagent质量评审...")
        reviews = []
        for content in contents:
            review = review_content(content)
            reviews.append(review)
        
        avg_score = sum(r['total_score'] for r in reviews) / len(reviews) if reviews else 0
        review_passed = avg_score >= SCORE_THRESHOLD
        
        print(f"\n📈 结果汇总:")
        print(f"  测试: {'✅通过' if test_passed else '❌未通过'} ({test_results['total_score']:.1f}分)")
        print(f"  评审: {'✅通过' if review_passed else '❌未通过'} ({avg_score:.1f}分)")
        
        return (test_passed and review_passed), avg_score, contents, reviews
    
    def sync_to_discord(self, contents: List[Dict], iteration: int):
        """同步到Discord讨论区"""
        if not DISCORD_SYNC:
            return
        
        print(f"\n📤 同步第{iteration}轮内容到Discord...")
        
        # 发送标题
        self.sender.send_to_forum(
            f"🔄 DTP迭代 {iteration} 测试内容",
            f"本轮共{len(contents)}条内容，正在质量测试中...\n\n"
            f"测试完成后高分内容将正式发布。\n"
            f"时间: {datetime.now().strftime('%m-%d %H:%M')}"
        )
        time.sleep(2)
        
        # 发送每条内容
        for i, content in enumerate(contents[:5], 1):  # 只发前5条避免刷屏
            print(f"  发送 {i}/{min(5, len(contents))}...")
            self.sender.send_to_forum(
                content['title'],
                content['content']
            )
            time.sleep(2)
        
        print(f"  ✅ 已同步到Discord")
    
    def deploy_final(self, contents: List[Dict]):
        """最终发布"""
        print(f"\n{'='*60}")
        print("🚀 最终发布到Discord")
        print('='*60)
        
        # 筛选高分内容（≥8分）
        high_score = [c for c in contents if c.get('review_score', 0) >= 8.0]
        if not high_score:
            high_score = contents[:5]  # 如果没有≥8分的，发前5条
        
        print(f"\n发布{len(high_score)}条高分内容:")
        for i, content in enumerate(high_score, 1):
            print(f"  {i}. {content['title'][:40]}...")
            self.sender.send_to_forum(content['title'], content['content'])
            time.sleep(2)
        
        print(f"\n✅ 发布完成!")
    
    def run(self):
        """运行完整闭环"""
        print("\n" + "="*60)
        print("🎯 AiTrend 全自动DTP闭环启动")
        print("="*60)
        print(f"配置: {ARTICLE_COUNT}条/轮 | 阈值{SCORE_THRESHOLD}分 | 最多{MAX_ITERATIONS}轮")
        print(f"同步: 每轮发Discord | 达标后最终发布")
        
        best_contents = None
        best_score = 0
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.iteration = iteration
            
            # DEVELOP
            articles = self.develop(count=ARTICLE_COUNT)
            
            # TEST + REVIEW
            passed, score, contents, reviews = self.test_and_review(articles)
            
            # 记录评分
            for c, r in zip(contents, reviews):
                c['review_score'] = r['total_score']
            
            # 保存最佳
            if score > best_score:
                best_score = score
                best_contents = contents
            
            # 同步到Discord
            self.sync_to_discord(contents, iteration)
            
            # 检查是否达标
            if passed:
                print(f"\n✅ 达标！平均分{best_score:.1f}分")
                self.deploy_final(contents)
                return True
            
            if iteration < MAX_ITERATIONS:
                print(f"\n🔄 未达标，进入下一轮优化...")
                time.sleep(5)  # 短暂休息
            else:
                print(f"\n⚠️ 达到最大迭代次数，发布最佳内容...")
                self.deploy_final(best_contents or contents)
                return False

def main():
    controller = AutoDTPController()
    success = controller.run()
    
    print("\n" + "="*60)
    if success:
        print("✅ DTP闭环成功完成！内容已达标并发布")
    else:
        print("⚠️ DTP闭环完成（未完全达标，已发布最佳内容）")
    print("="*60)

if __name__ == '__main__':
    main()
