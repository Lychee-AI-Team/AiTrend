#!/usr/bin/env python3
"""
AiTrend 评审员Agent - 以AI学习者视角评审内容质量
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志 - 同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('reviewer.log', encoding='utf-8')  # 文件输出
    ]
)
logger = logging.getLogger(__name__)

REVIEW_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory', 'review_log.json')
BATCH_DIR = os.path.join(os.path.dirname(__file__), '..', 'memory')

def load_batch(batch_id: str) -> Dict:
    """加载批次内容"""
    batch_file = os.path.join(BATCH_DIR, f'batch_{batch_id}.json')
    with open(batch_file, 'r') as f:
        return json.load(f)

def load_review_log() -> Dict:
    """加载评审日志"""
    try:
        with open(REVIEW_LOG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"review_sessions": [], "current_batch": {}, "optimization_history": []}

def save_review_log(log: Dict):
    """保存评审日志"""
    with open(REVIEW_LOG_PATH, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def review_content(content: Dict) -> Dict:
    """
    以AI学习者视角评审单条内容
    返回详细评分和建议
    """
    title = content.get('title', '')
    text = content.get('content', '')
    source = content.get('source', '')
    url = content.get('url', '')
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📄 评审: {title[:50]}...")
    logger.info('='*60)
    
    # 分析内容结构
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    word_count = len(text.replace(' ', '').replace('\n', ''))
    
    logger.info(f"字数: {word_count} | 段落数: {len(paragraphs)}")
    
    # 初始化评分维度
    scores = {
        "information": 0,      # 信息量 (4分)
        "practicality": 0,     # 实用性 (3分)
        "credibility": 0,      # 可信度 (2分)
        "experience": 0        # 阅读体验 (1分)
    }
    
    strengths = []
    weaknesses = []
    suggestions = []
    
    # ========== 1. 信息量评分 (4分) ==========
    logger.info("分析信息量...")
    
    # 检查是否说明了"是什么"
    if any(keyword in text.lower() for keyword in ['是一个', '是一款', '是用于', '主要解决', '提供']):
        scores["information"] += 1
        strengths.append("清楚说明了这是什么工具/项目")
    else:
        weaknesses.append("没有清楚说明这是什么")
        suggestions.append("开头应明确：这是一个XX，用于YY")
    
    # 检查是否说明了"能做什么"
    if any(keyword in text.lower() for keyword in ['功能包括', '可以做', '能够', '支持', '提供了']):
        scores["information"] += 1
        strengths.append("说明了核心功能")
    else:
        weaknesses.append("缺少核心功能说明")
        suggestions.append("增加具体功能列表：支持XX、能够YY")
    
    # 检查是否有技术/实现细节
    if any(keyword in text.lower() for keyword in ['使用', '基于', '采用', '实现', '技术', '代码', '架构']):
        scores["information"] += 1
        strengths.append("包含技术实现细节")
    else:
        weaknesses.append("缺少技术细节")
        suggestions.append("增加技术实现：使用XX技术，基于YY架构")
    
    # 检查是否有使用方式
    if any(keyword in text.lower() for keyword in ['安装', '使用', '配置', '运行', '开始', '上手']):
        scores["information"] += 1
        strengths.append("说明了使用方式")
    else:
        weaknesses.append("缺少使用方式说明")
        suggestions.append("增加使用方式：安装方法、配置步骤")
    
    # 扣分：空话检测
    empty_phrases = [
        '针对痛点', '解决需求', '功能设计', '务实', '专注',
        '讨论的焦点', '关注点主要', '从...来看', '整体来说'
    ]
    empty_count = sum(1 for phrase in empty_phrases if phrase in text)
    if empty_count > 2:
        scores["information"] = max(0, scores["information"] - 1)
        weaknesses.append(f"包含{empty_count}处空话套话")
        suggestions.append("删除'针对痛点'等抽象表述，改为具体描述")
    
    # ========== 2. 实用性评分 (3分) ==========
    logger.info("分析实用性...")
    
    # 检查是否有具体场景
    if any(keyword in text.lower() for keyword in [
        '场景', '时候', '情况', '用于', '适合', '当', '如果'
    ]):
        scores["practicality"] += 1.5
        strengths.append("说明了适用场景")
    else:
        weaknesses.append("没有说明什么时候会用到")
        suggestions.append("增加使用场景：适合在XX时候使用，当YY情况下")
    
    # 检查是否有对比优势
    if any(keyword in text.lower() for keyword in [
        '比', '相比', '优势', '更好', '更快', '更轻量', '区别'
    ]):
        scores["practicality"] += 1
        strengths.append("说明了与替代方案的对比")
    else:
        weaknesses.append("没有说明为什么选这个而不是其他的")
        suggestions.append("增加对比：比XX快YY%，比ZZ轻量")
    
    # 检查是否适合"我"
    if any(keyword in text.lower() for keyword in [
        '用户', '开发者', '普通人', '新手', '个人', '团队'
    ]):
        scores["practicality"] += 0.5
    else:
        suggestions.append("明确目标用户：适合XX人群使用")
    
    # ========== 3. 可信度评分 (2分) ==========
    logger.info("分析可信度...")
    
    # 检查是否有数据支撑
    has_numbers = any(char.isdigit() for char in text)
    if has_numbers:
        scores["credibility"] += 0.5
        strengths.append("包含具体数据")
    else:
        weaknesses.append("缺少具体数据（如性能指标、用户数）")
        suggestions.append("增加数据：如'处理速度提升50%'、'已有1万用户'")
    
    # 检查是否有用户反馈/来源引用
    if any(keyword in text.lower() for keyword in [
        '评论区', '有人', '用户', '反馈', '说', '提到', '作者'
    ]):
        scores["credibility"] += 1
        strengths.append("引用了用户反馈或讨论")
    else:
        weaknesses.append("没有引用用户实际反馈")
        suggestions.append("增加HN/Reddit评论区反馈：有人提到XX")
    
    # 检查是否有局限性说明
    if any(keyword in text.lower() for keyword in [
        '缺点', '问题', '不足', '限制', '坑', '注意', '小心'
    ]):
        scores["credibility"] += 0.5
        strengths.append("提到了潜在问题或限制")
    else:
        suggestions.append("增加客观评价：存在的问题或适用限制")
    
    # ========== 4. 阅读体验评分 (1分) ==========
    logger.info("分析阅读体验...")
    
    # 检查是否有固定套路
    template_phrases = [
        '第一', '第二', '第三', '首先', '其次', '最后',
        '从...来看', '综上所述', '总的来说', '综上所述'
    ]
    template_count = sum(1 for phrase in template_phrases if phrase in text)
    
    if template_count == 0 and empty_count <= 1:
        scores["experience"] = 1
        strengths.append("阅读流畅，像自然对话")
    elif template_count <= 2:
        scores["experience"] = 0.5
        weaknesses.append("有轻微套路痕迹")
        suggestions.append("减少'第一/第二'等结构化表达")
    else:
        scores["experience"] = 0
        weaknesses.append("明显套路化，像模板填空")
        suggestions.append("完全重写：像给朋友介绍一样自然叙述")
    
    # 计算总分
    total_score = sum(scores.values())
    
    # 学习者视角总结
    if total_score >= 8:
        perspective = f"作为想提升效率的普通人，这篇内容让我清楚知道{title[:20]}是什么、能做什么、什么时候用。信息很实在，没有废话，值得收藏。"
    elif total_score >= 6:
        perspective = f"大概知道是什么东西，但{weaknesses[0] if weaknesses else '有些细节不清楚'}。读完有点用，但还要自己去搜更多信息。"
    else:
        perspective = f"读完还是一头雾水，不知道这玩意儿具体能干啥、对我有什么用。感觉看了等于没看。"
    
    # 组装评审结果
    review = {
        "content_id": content.get('id'),
        "title": title,
        "url": url,
        "source": source,
        "total_score": round(total_score, 1),
        "breakdown": {
            "information": round(scores["information"], 1),
            "practicality": round(scores["practicality"], 1),
            "credibility": round(scores["credibility"], 1),
            "experience": round(scores["experience"], 1)
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "learner_perspective": perspective,
        "reviewed_at": datetime.now().isoformat()
    }
    
    # 打印评审结果
    logger.info(f"评分结果: {total_score}/10")
    logger.info(f"  信息量: {scores["information"]}/4 | 实用性: {scores["practicality"]}/3")
    logger.info(f"  可信度: {scores["credibility"]}/2 | 体验: {scores["experience"]}/1")
    
    if strengths:
        logger.info(f"优点:")
        for s in strengths[:3]:
            logger.info(f"  • {s}")
    
    if weaknesses:
        logger.info(f"问题:")
        for w in weaknesses[:3]:
            logger.info(f"  • {w}")
    
    if suggestions:
        logger.info(f"建议:")
        for s in suggestions[:3]:
            logger.info(f"  → {s}")
    
    logger.info(f"学习者视角: {perspective[:100]}...")
    
    return review

def review_batch(batch_id: str):
    """评审整个批次"""
    logger.info("="*60)
    logger.info(f"AiTrend 内容评审员启动")
    logger.info("="*60)
    logger.info(f"角色：AI学习者 | 目标：找到真正能提升效率的工具")
    logger.info(f"批次: {batch_id}")
    
    # 加载批次
    batch_data = load_batch(batch_id)
    contents = batch_data.get('contents', [])
    
    logger.info(f"待评审内容: {len(contents)} 条")
    
    # 逐条评审
    reviews = []
    total_score = 0
    
    for i, content in enumerate(contents, 1):
        logger.info("="*60)
        logger.info(f"评审进度: {i}/{len(contents)}")
        review = review_content(content)
        reviews.append(review)
        total_score += review['total_score']
    
    # 计算平均分
    avg_score = total_score / len(reviews) if reviews else 0
    
    # 保存评审结果
    log = load_review_log()
    log["current_batch"] = {
        "batch_id": batch_id,
        "articles": contents,
        "reviews": reviews,
        "average_score": round(avg_score, 1),
        "status": "reviewed",
        "reviewed_at": datetime.now().isoformat()
    }
    
    # 添加到历史记录
    log["review_sessions"].append({
        "batch_id": batch_id,
        "average_score": round(avg_score, 1),
        "reviewed_at": datetime.now().isoformat()
    })
    
    save_review_log(log)
    
    # 打印汇总
    logger.info("="*60)
    logger.info("评审完成汇总")
    logger.info('='*60)
    logger.info(f"总平均分: {avg_score:.1f}/10")
    logger.info(f"高分内容(≥8): {sum(1 for r in reviews if r["total_score"] >= 8)}/{len(reviews)}")
    logger.info(f"状态: {'建议发布' if avg_score >= 8 else '建议优化'}")
    
    # 生成优化建议汇总
    all_weaknesses = []
    all_suggestions = []
    for review in reviews:
        all_weaknesses.extend(review.get('weaknesses', []))
        all_suggestions.extend(review.get('suggestions', []))
    
    # 统计最常见问题
    from collections import Counter
    weakness_counts = Counter(all_weaknesses)
    
    logger.info(f"最常见问题 (Top 3):")
    for weakness, count in weakness_counts.most_common(3):
        logger.info(f"  • {weakness} ({count}次)")
    
    logger.info(f"评审结果已保存到: {REVIEW_LOG_PATH}")
    logger.info(f"主流程可以读取评分并决定是否优化")

def main():
    """主入口"""
    if len(sys.argv) < 2:
        logger.info("用法: python3 -m agents.reviewer <batch_id>")
        logger.info("示例: python3 -m agents.reviewer 20250202_193000")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    review_batch(batch_id)

if __name__ == '__main__':
    main()
