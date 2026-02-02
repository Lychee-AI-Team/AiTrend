"""
Twitter 内容质量筛选处理器

使用 LLM 评估推文内容质量，筛选精华内容。

评估维度：
1. 内容价值：是否有独特见解、技术深度
2. 信息密度：是否包含实质性信息（非空洞内容）
3. 专业度：是否来自可信来源、表达是否专业
4. 时效性：是否是当前热点、是否有时效价值
"""

import subprocess
import json
from typing import Dict, Any, Optional


class TwitterQualityFilter:
    """Twitter 内容质量筛选器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_quality_score = self.config.get('min_quality_score', 7)  # 最低质量分（满分10）
    
    def process(self, tweet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        评估推文质量
        
        Args:
            tweet: 推文数据
            
        Returns:
            如果通过质量筛选返回推文数据，否则返回None
        """
        # 构建评估提示词
        prompt = self._build_quality_prompt(tweet)
        
        try:
            # 调用OpenClaw进行质量评估
            result = self._evaluate_with_openclaw(prompt)
            
            if result and result.get('is_quality_content', False):
                # 添加质量评分到推文数据
                tweet['quality_score'] = result.get('score', 0)
                tweet['quality_reason'] = result.get('reason', '')
                return tweet
            else:
                print(f"  ⚠️ 内容质量不足 (评分: {result.get('score', 0)}/10)")
                return None
                
        except Exception as e:
            print(f"  ❌ 质量评估失败: {e}")
            # 评估失败时，保守起见返回None（可以改为返回原始数据）
            return None
    
    def _build_quality_prompt(self, tweet: Dict[str, Any]) -> str:
        """构建质量评估提示词"""
        text = tweet.get('text', '')
        author = tweet.get('author_name', 'Unknown')
        username = tweet.get('author_username', 'unknown')
        views = tweet.get('view_count', 0)
        retweets = tweet.get('retweets', 0)
        likes = tweet.get('likes', 0)
        
        prompt = f"""请评估以下Twitter推文的内容质量：

【推文内容】
{text}

【作者信息】
- 用户名: @{username}
- 显示名: {author}
- 阅读量: {views}
- 转发: {retweets}
- 点赞: {likes}

请从以下维度评估（满分10分）：
1. 内容价值：是否有独特见解、技术深度、实用信息
2. 信息密度：是否包含实质性内容（非空洞口号）
3. 专业度：表达是否专业、可信
4. 时效性：是否是当前AI领域热点

请以JSON格式回复：
{{
    "score": 整数评分(1-10),
    "is_quality_content": 是否高质量(bool, >=7分为true),
    "reason": "简要评价理由(20字内)"
}}

注意：
- 营销号、垃圾信息、纯表情符号内容直接给低分
- 需要有一定技术深度或独特见解才能给高分
- 仅当评分>=7分时，is_quality_content才为true"""

        return prompt
    
    def _evaluate_with_openclaw(self, prompt: str) -> Optional[Dict]:
        """
        使用OpenClaw/LLM评估内容质量
        
        这里使用sessions_spawn方式调用大模型
        """
        try:
            # 简单的关键词启发式评估（备用方案）
            # 实际应该调用大模型，这里先用规则模拟
            
            text_lower = prompt.lower()
            
            # 负面信号（营销/垃圾内容特征）
            negative_signals = [
                '🚀', '📈', '💰', '💎', 'moon', 'pump', '100x', 
                'guaranteed', 'urgent', 'limited time', 'spam'
            ]
            
            # 正面信号（技术内容特征）
            positive_signals = [
                'model', 'architecture', 'training', 'benchmark', 
                'dataset', 'paper', 'research', 'open source',
                'implementation', 'performance', 'accuracy',
                'transformer', 'llm', 'fine-tuning', 'inference'
            ]
            
            negative_count = sum(1 for s in negative_signals if s in text_lower)
            positive_count = sum(1 for s in positive_signals if s in text_lower)
            
            # 基础分5分
            score = 5
            
            # 正面信号加分
            score += min(positive_count * 0.5, 3)
            
            # 负面信号减分
            score -= min(negative_count * 1, 3)
            
            # 根据互动数据调整（但权重较低）
            views_idx = text_lower.find('阅读量:')
            if views_idx != -1:
                # 阅读量高说明受欢迎，适度加分
                score += 0.5
            
            # 确保分数在1-10范围内
            score = max(1, min(10, int(score)))
            
            # 生成理由
            if score >= 8:
                reason = "技术内容丰富，具有参考价值"
            elif score >= 7:
                reason = "内容质量尚可，有一定信息量"
            elif score >= 5:
                reason = "内容一般，缺乏深度"
            else:
                reason = "疑似营销或低质量内容"
            
            return {
                'score': score,
                'is_quality_content': score >= self.min_quality_score,
                'reason': reason
            }
            
        except Exception as e:
            print(f"评估出错: {e}")
            return None


if __name__ == "__main__":
    # 测试
    test_tweets = [
        {
            'text': 'Just released a new vision model that achieves SOTA on ImageNet. The key innovation is a novel attention mechanism that reduces computation by 40%. Paper and code: github.com/example',
            'author_name': 'Researcher',
            'author_username': 'researcher_ai',
            'view_count': 150000,
            'retweets': 1200,
            'likes': 3500
        },
        {
            'text': '🚀🚀 NEW AI TOOL LAUNCH!!! Get 100x returns!!! 🚀🚀 Limited time only! DM me for access 💎💰',
            'author_name': 'Crypto Bro',
            'author_username': 'crypto_bro_123',
            'view_count': 50000,
            'retweets': 10,
            'likes': 25
        }
    ]
    
    filter_processor = TwitterQualityFilter()
    
    for i, tweet in enumerate(test_tweets, 1):
        print(f"\n测试推文 {i}:")
        print(f"  内容: {tweet['text'][:60]}...")
        result = filter_processor.process(tweet)
        if result:
            print(f"  ✅ 通过筛选 (评分: {result['quality_score']}/10)")
            print(f"  理由: {result['quality_reason']}")
        else:
            print(f"  ❌ 未通过筛选")
