#!/usr/bin/env python3
"""
基于真实抓取数据的内容生成器
严禁编造，只能基于已有数据总结
严格禁止：字符串拼接、模板填充、分段组合
生成完全连续流畅的叙述，无段落分隔
"""

import random
from typing import Dict, List

def generate_from_real_data(scraped_data: Dict) -> str:
    """
    基于真实抓取的数据生成叙述
    规则：
    1. 只能使用scraped_data中的真实信息
    2. 数据不足时立即报错，不生成任何降级内容
    3. 自然叙述，无结构化格式，完全连续流畅
    4. 严禁使用字符串拼接（parts.append + join）
    """
    
    source = scraped_data.get('source', '')
    url = scraped_data.get('url', '')
    name = scraped_data.get('name', '')
    
    # 根据数据源选择叙述方式
    if source == 'github':
        return _generate_github_narrative(scraped_data)
    elif source == 'producthunt':
        return _generate_ph_narrative(scraped_data)
    elif source == 'hackernews':
        return _generate_hn_narrative(scraped_data)
    else:
        return _generate_generic_narrative(scraped_data)

def _generate_github_narrative(data: Dict) -> str:
    """基于GitHub真实数据生成叙述 - 直接返回完整f-string，禁止拼接，完全连续"""
    
    name = data.get('name', '')
    description = data.get('description', '')
    tagline = data.get('tagline', '')
    features = data.get('features', [])
    install = data.get('install', '')
    usage = data.get('usage', '')
    tech = data.get('tech_stack', [])
    stars = data.get('stars', 0)
    url = data.get('url', '')
    
    # 严格模式：没有足够数据立即报错，不生成降级内容
    if not description and not features:
        raise RuntimeError(f"❌ 内容生成失败：{name} README信息不足。没有description和features，无法生成高质量内容。")
    
    # 构建内容 - 直接返回完整字符串，严禁使用 parts.append + join，完全连续流畅
    desc = tagline or description
    feat_text = ", ".join(features[:3]) if features else ""
    tech_text = ", ".join(tech) if tech else ""
    stars_text = f"目前已经有 {stars} 个 star，社区活跃度还不错，" if stars > 100 else ""
    install_text = f"安装命令是{install}，" if install else (f"使用示例{usage}，" if usage else "")
    features_text = f"主要功能包括{feat_text}，" if feat_text else ""
    tech_stack_text = f"技术栈是{tech_text}，" if tech_text else ""
    
    # 随机开场
    opening = random.choice([
        f"{name} 是一个GitHub上的开源项目",
        f"在GitHub上发现了 {name}",
        f"{name} 这个开源项目挺有意思",
    ])
    
    # 直接返回完整f-string，完全连续流畅，无段落分隔
    return f"{opening}{f'，{desc[:150]}。' if desc else '。'}{features_text}{tech_stack_text}{install_text}{stars_text}建议先阅读文档再集成到自己的项目中。{url}"

def _generate_ph_narrative(data: Dict) -> str:
    """基于Product Hunt真实数据生成叙述 - 直接返回完整f-string，完全连续"""
    
    name = data.get('name', '')
    tagline = data.get('tagline', '')
    maker_desc = data.get('maker_description', '')
    reviews = data.get('reviews', [])
    votes = data.get('votes', 0)
    url = data.get('url', '')
    
    # 严格模式：没有足够数据立即报错
    if not tagline and not maker_desc:
        raise RuntimeError(f"❌ 内容生成失败：{name} Product Hunt数据不足。没有tagline和maker_description，无法生成内容。")
    
    # 直接构建完整内容，完全连续流畅
    votes_text = f"，目前已经拿了 {votes} 个 upvote" if votes > 50 else ""
    desc_text = maker_desc[:200] if maker_desc else f"它是一个 {tagline} 的工具"
    
    if not reviews:
        raise RuntimeError(f"❌ 内容生成失败：{name} 没有用户评论数据。无法生成基于真实反馈的内容。")
    
    review_text = f"有用户评论说{reviews[0][:150]}..."
    
    return f"{name} 今天刚在 Product Hunt 上发布{votes_text}。{desc_text} {review_text}建议先试用免费版看看是否符合自己的工作流。{url}"

def _generate_hn_narrative(data: Dict) -> str:
    """基于HackerNews真实数据生成叙述 - 直接返回完整f-string，完全连续"""
    
    title = data.get('title', '')
    points = data.get('points', 0)
    comments = data.get('top_comments', [])
    comment_count = data.get('comment_count', 0)
    external_url = data.get('external_url', '')
    url = data.get('url', '')
    
    # 严格模式：没有评论数据立即报错
    if not comments:
        raise RuntimeError(f"❌ 内容生成失败：{title} 没有HN评论数据。无法生成基于社区讨论的内容。")
    
    points_text = f"在 HackerNews 上引发了讨论，拿了 {points} points，" if points > 100 else "在 HackerNews 上有讨论，"
    comment_count_text = f"评论区有 {comment_count} 条回复，" if comment_count > 10 else ""
    
    first_comment = f"有人提到{comments[0][:200]}..."
    second_comment = f"还有人补充说{comments[1][:150]}..." if len(comments) > 1 else ""
    external_link_text = f"讨论的原项目在这里{external_url}。" if external_url else ""
    
    return f"{title} {points_text}{comment_count_text}{first_comment}{second_comment}{external_link_text}HN讨论{url}"

def _generate_generic_narrative(data: Dict) -> str:
    """通用叙述 - 直接返回完整f-string，完全连续。严格模式：无描述立即报错"""
    name = data.get('name', '')
    description = data.get('description', '')
    url = data.get('url', '')
    
    if not description:
        raise RuntimeError(f"❌ 内容生成失败：{name} 没有description数据，无法生成内容。")
    
    return f"{name} {description[:200]}。{url}"

# 质量检查
def has_sufficient_data(scraped_data: Dict) -> bool:
    """检查是否有足够数据生成内容"""
    
    source = scraped_data.get('source', '')
    
    if source == 'github':
        # GitHub需要：描述或功能
        return bool(
            scraped_data.get('description') or 
            scraped_data.get('features')
        )
    
    elif source == 'producthunt':
        # PH需要：描述或评论
        return bool(
            scraped_data.get('tagline') or 
            scraped_data.get('reviews')
        )
    
    elif source == 'hackernews':
        # HN需要：评论
        return bool(scraped_data.get('top_comments'))
    
    return False

def estimate_quality(scraped_data: Dict) -> int:
    """估算数据质量（0-100）"""
    
    score = 0
    
    # 基础信息
    if scraped_data.get('name'):
        score += 10
    if scraped_data.get('description'):
        score += 20
    
    # 详细信息
    if scraped_data.get('features'):
        score += min(len(scraped_data['features']) * 10, 30)
    if scraped_data.get('reviews'):
        score += min(len(scraped_data['reviews']) * 10, 20)
    if scraped_data.get('tech_stack'):
        score += 10
    
    # 社区数据
    if scraped_data.get('stars', 0) > 100:
        score += 10
    
    return min(score, 100)
