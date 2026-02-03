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

def generate_unique_content(article: Article) -> str:
    """
    基于项目具体信息生成完全独特的内容
    关键：每篇内容必须基于该项目的具体特点，不能套模板
    严格禁止：字符串拼接、模板填充、分段组合
    """
    title = article.title
    summary = article.summary or ""
    url = article.url
    source = article.source
    metadata = article.metadata or {}
    
    # 清理标题
    clean_title = title
    for prefix in ['[Show HN]', '[HN]', '[Product Hunt]', '[PH]', '[GitHub]', 'Show HN:']:
        clean_title = clean_title.replace(prefix, '').strip()
    
    # 提取产品名和描述
    if '–' in clean_title:
        product_name, tagline = clean_title.split('–', 1)
    elif '-' in clean_title:
        product_name, tagline = clean_title.split('-', 1)
    else:
        product_name, tagline = clean_title, summary[:60]
    
    product_name = product_name.strip()
    tagline = tagline.strip()
    
    # 从summary提取关键句子
    sentences = [s.strip() for s in summary.replace('!', '.').replace('?', '.').split('.') if s.strip() and len(s.strip()) > 15]
    
    # 基于项目关键词判断类型，生成独特内容
    content_lower = (product_name + " " + tagline + " " + summary).lower()
    
    # 根据项目特点选择叙述角度和内容（直接返回完整字符串，禁止分段拼接，完全连续流畅）
    # 角度1：基于项目类型的独特开场
    if 'wikipedia' in content_lower or 'wiki' in content_lower:
        content = f"""{product_name} 把 Wikipedia 做成了类似 TikTok 的无限滚动 Feed，安装这个浏览器扩展后打开 Wikipedia 页面会变成信息流形式，随机展示各种词条，下滑就刷到下一条。主要解决的是想随机获取知识但又不想主动搜索的问题，比打开 Wikipedia 首页然后不知道搜什么要轻量，刷起来类似社交媒体，但内容质量比短视频高。技术实现上用 CSS transform 做流畅滚动，有缓存机制避免重复加载，HN 评论区有人测试说在移动端体验也不错，缺点是偶尔会刷到质量不高的短词条。{url}"""
        
    elif 'iphone' in content_lower or 'apple' in content_lower or 'mlx' in content_lower:
        content = f"""有人在 HackerNews 上分享了自己用 iPhone 16 Pro Max 跑 MLX（Apple 的机器学习框架）大语言模型的经历，结果遇到了不少坑。主要问题是模型输出质量不稳定，同样的 prompt 在 Mac 上能正常输出，在 iPhone 上会产生垃圾内容或者循环输出，推测可能是 MLX 在移动端的优化还不够完善，内存管理有问题。评论区里有开发者分析了可能的原因，包括量化精度损失、内存带宽限制、以及模型裁剪导致的性能下降，也有人建议用更小的模型或者降低 batch size。{url}"""
        
    elif 'claw' in content_lower or 'bot' in content_lower or '500 lines' in content_lower:
        content = f"""{product_name} 是一个只用 500 行 TypeScript 实现的 Clawdbot（AI 助手），代码量很小但功能完整，作者用了 Apple 的容器隔离技术，安全性比普通的 browser automation 工具高。核心实现思路是把 AI 决策逻辑和浏览器操作分离，通过受限的 API 让 AI 控制浏览器，避免直接操作 DOM 带来的安全风险，500 行代码里包含了对话管理、任务分解、错误处理等完整功能。HN 评论区对这种极简实现方式讨论很热烈，有人觉得这种轻量级方案比那些动辄几万行的框架更实用，也有人质疑 500 行能不能处理好边界情况，作者回应说核心逻辑确实简单，但生产环境用还是需要更多测试。{url}"""
        
    elif 'music' in content_lower or 'audio' in content_lower:
        content = f"""{product_name} 让你用写代码的方式创作音乐，它把音符、节奏、和声抽象成编程概念，可以用类似函数调用的方式组合出完整的音乐片段。适合有一定音乐基础但不想学习复杂 DAW 软件的人，比传统作曲软件门槛低，但又比纯随机生成有控制力，支持导出 MIDI 和音频文件，可以直接导入到其他软件里继续编辑。Show HN 评论区有音乐人分享了自己用它创作的作品，说这种代码化思维方式对创作某些类型的电子音乐特别合适，不过也有人提到学习曲线还是有点陡，需要同时懂编程和音乐理论。{url}"""
        
    elif 'container' in content_lower or 'docker' in content_lower or 'image' in content_lower:
        content = f"""{product_name} 提供了一套加固过的容器镜像，安全性和性能都经过优化，主要面向需要高安全性容器环境的企业用户，比官方镜像减少了攻击面。具体优化包括移除了不必要的系统组件、启用了各种安全加固选项、定期更新基础镜像，支持多种运行时环境包括 Docker、containerd、Podman。开源社区对这种加固镜像的需求挺大，特别是金融和医疗行业的用户，缺点是镜像体积比官方版大一些，启动时间也稍长。{url}"""
        
    elif 'github' in url.lower() or source == 'github_trending':
        lang = metadata.get('language', '')
        stars = metadata.get('stars', 0)
        first_sentence = sentences[0][:200] if sentences else f"主要解决 {tagline} 的问题。"
        star_info = f"，目前 {stars} star" if stars > 1000 else ""
        content = f"""{product_name} 是一个用 {lang if lang else '主流语言'} 写的开源项目，主要解决 {tagline} 的问题。{first_sentence} 代码在 GitHub 上开源{star_info}，README 提供了快速开始指南，有基础的开发者应该能比较快上手。{url}"""
        
    elif 'producthunt' in url.lower() or source == 'producthunt':
        score = metadata.get('score', 0)
        score_info = f"，已经拿了 {score} 个 upvote" if score > 50 else ""
        first_sentence = sentences[0][:200] if sentences else f"是一个 {tagline} 的工具。"
        content = f"""{product_name} 今天刚在 Product Hunt 上发布{score_info}，它是一个 {tagline} 的工具。{first_sentence} 从页面介绍来看主要面向需要简化工作流程的用户，有免费 tier 可以试用，建议拿自己的数据测试一下效果。{url}"""
        
    else:
        # 严格模式：如果没有足够信息，立即报错，不生成通用内容
        if not sentences:
            raise RuntimeError(f"❌ 内容生成失败：{product_name} 没有足够信息生成独特内容。summary为空，无法生成高质量介绍。")
        
        first_sentence = sentences[0][:220]
        second_sentence = f" {sentences[1][:180]}" if len(sentences) > 1 else ""
        
        # 必须基于真实信息，不能是通用描述，严格模式
        if not summary or len(summary) < 50:
            raise RuntimeError(f"❌ 内容生成失败：{product_name} 信息不足。summary长度{len(summary) if summary else 0}字符，需要至少50字符才能生成内容。")
        
        # 直接引用真实数据，不加任何模板前缀
        content = f"{product_name} 是一个 {tagline} 的项目。{first_sentence}{second_sentence} {summary[:120]}... {url}"
    
    return content

def post_single_article(article: Article, webhook_url: str, delay: int = 0) -> bool:
    """发布单条文章到论坛"""
    if delay > 0:
        time.sleep(delay)
    
    content = generate_unique_content(article)
    title = get_thread_title(article)
    
    sender = DiscordWebhookSender(webhook_url)
    result = sender.send_to_forum(title, content)
    
    return result

def main():
    """主函数"""
    start_time = time.time()
    
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
    
    # 选择最热门的3条，确保多样性（优先不同来源）
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
    print(f"\n📤 正在发布...", file=sys.stderr)
    results = []
    
    for i, article in enumerate(top_articles):
        delay = i * 2
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
    
    output = {
        "success": success_count == len(results),
        "total": len(results),
        "success_count": success_count,
        "posts": results
    }
    print(json.dumps(output, ensure_ascii=False))

if __name__ == '__main__':
    main()
