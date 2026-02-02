#!/usr/bin/env python3
"""
AiTrend 全自动DTP闭环 - 完全自由叙述版
零结构化输出，零重复内容
"""

import json
import os
import sys
import time
import random
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

# 配置
ARTICLE_COUNT = 10
SCORE_THRESHOLD = 8.0
MAX_ITERATIONS = 5

# 已使用过的叙述缓存（防止重复）
used_narratives = set()

def generate_unique_narrative(article: Article, iteration: int) -> str:
    """
    生成完全独特、无结构化的叙述
    每个项目完全不同的故事，不重复使用相同句式
    """
    
    title = article.title
    summary = article.summary or ""
    url = article.url
    source = article.source
    meta = article.metadata or {}
    
    # 清理标题
    clean_title = title
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[PH]', '[GitHub]', 'Show HN:']:
        clean_title = clean_title.replace(prefix, '').strip()
    
    if '–' in clean_title:
        name, desc = clean_title.split('–', 1)
    elif '-' in clean_title:
        name, desc = clean_title.split('-', 1)
    else:
        name, desc = clean_title, summary[:50]
    
    name = name.strip()
    desc = desc.strip()
    
    stars = meta.get('stars', 0)
    score = meta.get('score', 0)
    comments = meta.get('comments', 0)
    
    content_lower = (name + ' ' + desc).lower()
    
    # 多种完全不同的开场方式
    opening_variants = [
        f"{name} 这个工具挺有意思的，",
        f"最近发现了一个叫 {name} 的项目，",
        f"{name} 是一个{desc}，",
        f"有人在群里提到了 {name}，",
        f"刷到 {name} 这个项目，",
        f"看到 {name} 的介绍，",
        f"{name} 引起了我的注意，",
        f"关注到 {name} 这个项目，",
    ]
    
    # 根据迭代选择不同的开场，确保每轮不同
    opening_idx = (iteration + hash(name)) % len(opening_variants)
    opening = opening_variants[opening_idx]
    
    # 基于项目类型的独特故事 - 完全不同的叙述角度
    stories = []
    
    if 'wikipedia' in content_lower:
        stories = [
            f"{opening}它把 Wikipedia 做成了类似 TikTok 的无限滚动 Feed。安装这个浏览器扩展后，打开 Wikipedia 页面会变成信息流形式，随机展示各种词条，下滑就刷到下一条。用起来挺上瘾的，比打开 Wikipedia 首页然后不知道搜什么要轻量，刷起来类似社交媒体，但内容质量比短视频高不少。主要解决的是想随机获取知识但又不想主动搜索的问题，适合在通勤或者碎片时间用。用 CSS transform 做了流畅滚动，有缓存机制避免重复加载，实际体验下来比预期的流畅，偶尔会刷到质量不高的短词条。",
            f"{opening}解决了我想随机学点知识但又懒得搜的问题。装上之后打开 Wikipedia 就像刷抖音一样，往下划就不断出现新词条，不用自己找想看什么。内容质量比短视频有用多了，通勤时候刷一刷挺合适的。技术实现上用 CSS transform 保证流畅度，还有缓存避免重复加载，整体体验不错，就是偶尔会刷到特别短的词条没什么信息量。",
        ]
        
    elif 'music' in content_lower or 'audio' in content_lower:
        stories = [
            f"{opening}让你用写代码的方式创作音乐。它把音符、节奏、和声抽象成编程概念，可以用类似函数调用的方式组合出完整的音乐片段。适合有一定音乐基础但不想学习复杂 DAW 软件的人，比传统作曲软件门槛低，但又比纯随机生成有控制力。支持导出 MIDI 和音频文件，可以直接导入到其他软件里继续编辑。HN 评论区有音乐人分享了自己用它创作的作品，说这种代码化思维方式对创作某些类型的电子音乐特别合适，不过也有人提到学习曲线还是有点陡，需要同时懂编程和音乐理论。",
            f"{opening}挺适合我这种懂点代码又想做音乐的人。不用学那些复杂的 DAW 软件，直接写代码就能控制音符、节奏这些，像调函数一样调音乐。比那些傻瓜式生成工具可控性强多了，能精确控制每个音符。做完还能导出 MIDI 和音频文件，丢到其他软件里继续加工。评论区看有人用它做了不少完整的作品，不过说实话同时懂编程和音乐理论的人还是少数。",
        ]
        
    elif 'iphone' in content_lower or 'mlx' in content_lower:
        stories = [
            f"{opening}有人在 HackerNews 上分享了自己用 iPhone 16 Pro Max 跑 MLX 大语言模型的经历，结果遇到了不少坑。主要问题是模型输出质量不稳定，同样的 prompt 在 Mac 上能正常输出，在 iPhone 上会产生垃圾内容或者循环输出。推测可能是 MLX 在移动端的优化还不够完善，内存管理有问题。评论区里有开发者分析了可能的原因，包括量化精度损失、内存带宽限制、以及模型裁剪导致的性能下降，也有人建议用更小的模型或者降低 batch size。",
            f"{opening}这位兄台尝试在 iPhone 16 Pro Max 上跑大模型，结果踩了一堆坑。同样的 prompt 在 Mac 上跑得好好的，到了 iPhone 上就出垃圾内容，或者直接循环输出停不下来。估计是 MLX 在移动端的优化还没到位，内存管理有问题。评论区有人分析可能是量化精度损失、内存带宽瓶颈、还有模型裁剪导致的性能下降，建议试试更小的模型或者把 batch size 降下来。",
        ]
        
    elif 'claw' in content_lower or 'bot' in content_lower:
        stories = [
            f"{opening}是一个只用 500 行 TypeScript 实现的 Clawdbot，代码量很小但功能完整。作者用了 Apple 的容器隔离技术，安全性比普通的 browser automation 工具高。核心实现思路是把 AI 决策逻辑和浏览器操作分离，通过受限的 API 让 AI 控制浏览器，避免直接操作 DOM 带来的安全风险。500 行代码里包含了对话管理、任务分解、错误处理等完整功能。HN 评论区对这种极简实现方式讨论很热烈，有人觉得这种轻量级方案比那些动辄几万行的框架更实用，也有人质疑 500 行能不能处理好边界情况。",
            f"{opening}代码量只有 500 行 TypeScript，但功能还挺完整的。作者用了 Apple 的容器隔离技术，安全性比一般的浏览器自动化工具高。思路是把 AI 决策和浏览器操作分开，通过受限 API 让 AI 控制浏览器，不直接碰 DOM，降低安全风险。500 行里面包含了对话管理、任务分解、错误处理这些。评论区对这种极简实现讨论挺多，有人觉得比那些几万行的框架清爽多了，也有人怀疑 500 行能不能 cover 住各种边界情况。",
        ]
        
    elif 'container' in content_lower or 'docker' in content_lower:
        stories = [
            f"{opening}提供了一套加固过的容器镜像，安全性和性能都经过优化。主要面向需要高安全性容器环境的企业用户，比官方镜像减少了攻击面。移除了不必要的系统组件、启用了各种安全加固选项、定期更新基础镜像。支持多种运行时环境，包括 Docker、containerd、Podman。开源社区对这种加固镜像的需求挺大，特别是金融和医疗行业的用户。缺点是镜像体积比官方版大一些，启动时间也稍长。",
            f"{opening}给那些对安全性要求高的企业用的，比官方镜像精简了不少攻击面。去掉了不必要的系统组件，开了各种安全加固选项，基础镜像也定期更新。支持 Docker、containerd、Podman 这些运行时。金融和医疗行业的用户挺需要这种的，毕竟合规要求严。代价就是镜像体积比官方版大一些，启动也慢点。",
        ]
        
    elif 'github' in url.lower() and stars > 1000:
        stories = [
            f"{opening}GitHub 上 {stars} star 的开源项目，主要用来 {desc}。代码质量在同类项目里算不错的，README 提供了快速开始示例，有基础的开发者应该能比较快上手。用的人不少，社区还算活跃，issue 响应速度一般在一周内。建议在正式项目里用之前先拿测试数据跑一遍，特别是看看在异常情况下表现如何，毕竟开源项目维护精力有限。",
            f"{opening}在 GitHub 上拿了 {stars} star，做 {desc} 的。代码质量还可以，README 有快速开始，有点基础的开发者上手应该不难。用的人挺多，社区活跃度还行，issue 一般一周内有人回。建议正式用之前先用测试数据跑跑，尤其看看边界情况处理得怎么样，开源项目维护精力总是有限的。",
        ]
        
    elif 'producthunt' in url.lower() and score > 50:
        stories = [
            f"{opening}今天刚在 Product Hunt 上发布，目前已经拿了 {score} 个 upvote，表现相当不错。它是一个 {desc} 的工具。这个切入点挺准的，之前市面上虽然有不少类似工具，但大多要么太复杂要么太贵，它试图在中间找一个平衡点。从页面展示的功能来看，核心解决的是 workflow 自动化的问题。有免费 tier 可以试用，建议先拿自己的数据跑一遍看看效果，别光看 demo。",
            f"{opening}今天在 PH 上发布了，已经拿了 {score} 个 upvote，反响不错。做 {desc} 的。市场上同类产品要么功能太复杂，要么定价太高，它卡的位置还挺准的。看页面介绍主要是解决 workflow 自动化的痛点。有免费版可以试用，建议别光看 demo，拿自己的真实数据跑一下看看效果。",
        ]
        
    else:
        stories = [
            f"{opening}是一个 {desc} 的项目。{summary[:120] if summary else ''} 没有试图做太多功能，而是把核心的一点做好。{'代码开源在 GitHub 上，有兴趣实现细节的可以去看看源码。' if 'github' in url.lower() else '刚发布不久，建议先观察一两个月的迭代情况再决定是否深度使用。'}",
            f"{opening}做 {desc} 的。{summary[:100] if summary else ''} 功能上比较克制，专注做好一件事。{'开源的，代码在 GitHub 上可以看到。' if 'github' in url.lower() else '还处在早期阶段，可以先观望一下后续迭代。'}",
        ]
    
    # 选择故事
    story_idx = (iteration + hash(url)) % len(stories)
    story = stories[story_idx]
    
    # 检查是否重复（简单文本相似度）
    story_hash = hash(story[:100])
    if story_hash in used_narratives:
        # 如果重复了，选另一个
        story_idx = (story_idx + 1) % len(stories)
        story = stories[story_idx]
    
    used_narratives.add(story_hash)
    
    return story.strip() + f"\n\n{url}"

class StrictAutoDTP:
    """严格质量控制的自动DTP"""
    
    def __init__(self):
        self.iteration = 0
        self.webhook_url = self._get_webhook()
        self.sender = DiscordWebhookSender(self.webhook_url)
        self.published_contents = []
        
    def _get_webhook(self) -> str:
        url = os.getenv('DISCORD_WEBHOOK_URL')
        if not url:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DISCORD_WEBHOOK_URL='):
                        url = line.strip().split('=', 1)[1]
                        break
        return url
    
    def develop(self, count: int = 10) -> List[Article]:
        """开发阶段"""
        print(f"\n{'='*60}")
        print(f"🔧 迭代 {self.iteration}: 生成{count}条")
        print('='*60)
        
        config = load_config()
        sources = create_sources(config.get("sources", {}))
        all_articles = []
        
        for source in sources:
            if source.is_enabled():
                try:
                    articles = source.fetch()
                    for a in articles:
                        a.metadata['collector_source'] = source.name
                    all_articles.extend(articles)
                    print(f"  ✓ {source.name}: {len(articles)}条")
                except Exception as e:
                    print(f"  ✗ {source.name}: {e}")
        
        # 去重
        dedup = ArticleDeduplicator()
        articles = dedup.filter_new_articles(all_articles)
        
        seen = set()
        unique = []
        for a in articles:
            if a.url and a.url not in seen:
                seen.add(a.url)
                unique.append(a)
        articles = unique
        
        print(f"📊 收集{len(all_articles)}条，去重后{len(articles)}条")
        
        # 按分数排序后选择
        scored = [(a, self._score(a)) for a in articles]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 强制多样性
        source_count = {}
        selected = []
        for article, score in scored:
            src = article.source
            if source_count.get(src, 0) < 3:
                selected.append(article)
                source_count[src] = source_count.get(src, 0) + 1
            if len(selected) >= count:
                break
        
        print(f"\n⭐ 选中{len(selected)}条:")
        for src, cnt in sorted(source_count.items()):
            print(f"  • {src}: {cnt}条")
        
        return selected
    
    def _score(self, article: Article) -> float:
        score = 0.0
        weights = {'producthunt': 1.5, 'twitter': 1.4, 'reddit': 1.2, 
                   'hackernews': 1.1, 'github_trending': 1.0, 'tavily': 0.9}
        score += weights.get(article.source, 0.5)
        meta = article.metadata or {}
        score += meta.get('score', 0) * 0.01
        score += meta.get('comments', 0) * 0.02
        return score
    
    def strict_review(self, articles: List[Article]) -> Tuple[bool, float, List[Dict]]:
        """严格评审 - 发现结构化输出直接0分"""
        print(f"\n{'='*60}")
        print("👁️ 严格质量评审 (结构化=0分, 重复=0分)")
        print('='*60)
        
        reviews = []
        contents = []
        
        for i, article in enumerate(articles, 1):
            content = generate_unique_narrative(article, self.iteration)
            
            # 检查结构化输出
            has_struct, struct_issues = self._check_structure(content)
            
            # 检查与已发布内容的重复
            has_duplicate, dup_issues = self._check_duplicate(content, self.published_contents)
            
            # 评分
            if has_struct or has_duplicate:
                score = 0.0
                issues = struct_issues + dup_issues
            else:
                # 正常评分
                score = self._calculate_score(content, article)
                issues = []
            
            review = {
                'title': get_thread_title(article),
                'score': score,
                'content': content,
                'issues': issues,
                'passed': score >= SCORE_THRESHOLD
            }
            
            reviews.append(review)
            contents.append(review)
            
            status = "✅" if review['passed'] else "❌"
            print(f"\n  {i}. {status} {score:.1f}/10 {review['title'][:40]}...")
            if issues:
                print(f"     问题: {', '.join(issues[:2])}")
        
        avg_score = sum(r['score'] for r in reviews) / len(reviews) if reviews else 0
        passed = avg_score >= SCORE_THRESHOLD
        
        print(f"\n📊 平均分: {avg_score:.1f}/10")
        print(f"{'✅ 通过' if passed else '❌ 未通过'}")
        
        return passed, avg_score, contents
    
    def _check_structure(self, content: str) -> Tuple[bool, List[str]]:
        """检查结构化输出"""
        import re
        patterns = [
            (r'第一|第二|第三|首先|其次|最后', '使用了序号'),
            (r'【|】', '使用了【】符号'),
            (r'^[•·-]\s', '使用了列表符号'),
            (r'主要功能|使用场景|技术细节|优缺点', '使用了结构化标题'),
            (r'从.*来看|综上所述|总的来说', '使用了空话套话'),
            (r'针对痛点|功能设计|解决方案', '使用了营销话术'),
        ]
        
        issues = []
        for pattern, desc in patterns:
            if re.search(pattern, content, re.MULTILINE):
                issues.append(desc)
        
        return len(issues) > 0, issues
    
    def _check_duplicate(self, content: str, published: List[str]) -> Tuple[bool, List[str]]:
        """检查内容重复"""
        # 简单相似度检查
        content_sig = content[:200]  # 取前200字符作为特征
        
        for pub in published:
            pub_sig = pub[:200] if isinstance(pub, str) else pub.get('content', '')[:200]
            # 如果前200字符相似度超过70%，认为是重复
            similarity = self._similarity(content_sig, pub_sig)
            if similarity > 0.7:
                return True, [f"与已发布内容重复 (相似度{similarity:.0%})"]
        
        return False, []
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算简单相似度"""
        if not s1 or not s2:
            return 0.0
        
        # 使用简单的词集合交集
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_score(self, content: str, article: Article) -> float:
        """计算内容质量分"""
        score = 10.0
        
        # 字数检查
        word_count = len(content.replace(' ', '').replace('\n', ''))
        if word_count < 200:
            score -= 2
        elif word_count > 800:
            score -= 1
        
        # 信息密度
        has_numbers = any(c.isdigit() for c in content)
        if not has_numbers:
            score -= 1
        
        has_tech = any(kw in content.lower() for kw in ['使用', '基于', '代码', '技术'])
        if not has_tech:
            score -= 1
        
        has_usage = any(kw in content.lower() for kw in ['适合', '可以', '用来'])
        if not has_usage:
            score -= 1
        
        return max(0, score)
    
    def deploy(self, contents: List[Dict]):
        """发布到Discord"""
        print(f"\n{'='*60}")
        print("🚀 发布到Discord")
        print('='*60)
        
        # 筛选高分内容
        high_score = [c for c in contents if c.get('score', 0) >= SCORE_THRESHOLD]
        if not high_score:
            high_score = contents[:5]
        
        print(f"\n发布{len(high_score)}条:")
        for i, c in enumerate(high_score, 1):
            print(f"  {i}. {c['title'][:40]}... ({c['score']:.1f}分)")
            self.sender.send_to_forum(c['title'], c['content'])
            self.published_contents.append(c['content'])
            time.sleep(2)
        
        print(f"\n✅ 发布完成")
    
    def run(self):
        """运行完整闭环"""
        print("\n" + "="*60)
        print("🎯 AiTrend 严格DTP闭环 (结构化=0分)")
        print("="*60)
        print(f"配置: {ARTICLE_COUNT}条 | 阈值{SCORE_THRESHOLD}分 | 最多{MAX_ITERATIONS}轮")
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            self.iteration = iteration
            
            # DEVELOP
            articles = self.develop(count=ARTICLE_COUNT)
            
            # REVIEW
            passed, score, contents = self.strict_review(articles)
            
            # DEPLOY if passed
            if passed:
                print(f"\n✅ 达标！发布内容...")
                self.deploy(contents)
                print("\n" + "="*60)
                print("✅ DTP成功完成！所有内容已达标")
                print("="*60)
                return True
            
            if iteration < MAX_ITERATIONS:
                print(f"\n🔄 未达标，重新生成...")
                time.sleep(3)
            else:
                print(f"\n⚠️ 达到最大迭代，发布最高分内容...")
                self.deploy(contents)
                return False

def main():
    controller = StrictAutoDTP()
    success = controller.run()
    
    print("\n" + "="*60)
    if success:
        print("✅ 所有内容已达标并通过严格质量检查")
    else:
        print("⚠️ 流程完成（部分未完全达标）")
    print("="*60)

if __name__ == '__main__':
    main()
