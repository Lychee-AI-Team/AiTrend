#!/usr/bin/env python3
"""
自然叙述合成模块（带大模型融合）
将多个信息片段融合成自然、无结构化的叙述
"""

import random
from typing import Dict, Any, List
from ..llm_client import get_llm_client

class NarrativeComposer:
    """
    自然叙述合成器（LLM增强版）
    
    输入：多个信息整理模块的内容片段（每个都是自然叙述）
    输出：单条流畅的自然叙述
    
    使用大模型融合多个片段，确保：
    1. 内容连贯流畅
    2. 无结构化痕迹
    3. 信息密度高
    4. 产品特点清晰
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_length = config.get('min_length', 200)
        self.max_length = config.get('max_length', 600)
        self.llm = get_llm_client()
    
    def compose(self, candidate: Dict[str, Any], fragments: List[str]) -> str:
        """
        合成最终内容
        
        策略：
        1. 使用大模型融合多个片段
        2. 添加项目元数据
        3. 确保流畅自然
        """
        
        name = candidate.get('name', '')
        source = candidate.get('source_name', '')
        url = candidate.get('url', '')
        stars = candidate.get('stars', 0)
        language = candidate.get('language', '')
        growth_rate = candidate.get('growth_rate', 0)
        
        # 构建融合提示
        context = self._build_fusion_context(name, fragments, stars, language, growth_rate)
        
        # 调用大模型融合
        system_prompt = """你是一个专业的技术内容编辑，擅长将多个信息源融合成流畅的叙述。

重要约束：
1. 禁止任何结构化输出 - 绝对不要列表、序号、bullet points、分点说明
2. 禁止空话套话 - 不要"针对痛点"、"功能设计"、"架构清晰"、"旨在解决"
3. 必须自然叙述 - 像写博客一样，段落流畅，有起承转合
4. 突出产品特点 - 具体是什么、能做什么、为什么值得关注
5. 突出亮点 - 最特别的功能、最实用的点、用户为什么喜欢
6. 信息密度高 - 每句话都有价值，不重复不废话
7. 开头吸引人 - 用有趣的方式引入产品
8. 结尾有建议 - 适合什么场景、怎么尝试

输出风格：
- 一个或两个自然段落
- 用"它"来指代产品
- 直接说功能，不要"该产品提供了XXX功能"
- 用具体例子，不要抽象描述
- 控制在500字以内"""
        
        prompt = f"""请将以下关于「{name}」的信息融合成一篇流畅的自然叙述：

{context}

要求：
1. 融合所有关键信息，不要遗漏重要点
2. 用自然叙述，绝对不要列表、不要序号
3. 突出产品特点和亮点
4. 开头吸引人，结尾有使用建议
5. 控制在500字以内
6. 直接输出内容，不要标题"""
        
        composed = self.llm.generate(prompt, system_prompt, temperature=0.6, max_tokens=800)
        
        if not composed:
            # LLM失败，使用简单拼接
            composed = self._fallback_compose(name, fragments)
        
        # 添加URL
        composed = self._clean_and_finalize(composed, url)
        
        return composed
    
    def _build_fusion_context(self, name: str, fragments: List[str], 
                              stars: int, language: str, growth_rate: float) -> str:
        """构建融合上下文"""
        
        parts = [f"项目名称: {name}"]
        
        if stars:
            parts.append(f"GitHub Stars: {stars}")
        
        if language:
            parts.append(f"主要语言: {language}")
        
        if growth_rate:
            parts.append(f"增长率: {growth_rate} stars/天")
        
        parts.append("\n信息片段:")
        for i, fragment in enumerate(fragments, 1):
            parts.append(f"片段{i}: {fragment}")
        
        return "\n".join(parts)
    
    def _fallback_compose(self, name: str, fragments: List[str]) -> str:
        """LLM失败时的备用合成"""
        
        # 随机选择开场
        openings = [
            f"{name} 这个工具最近挺火的，",
            f"最近发现了 {name}，",
            f"{name} 是一个值得关注的新项目，",
        ]
        
        opening = random.choice(openings)
        
        # 简单拼接
        combined = " ".join(fragments)
        
        # 组合
        content = opening + combined
        
        # 清理
        content = self._clean_structure(content)
        
        return content
    
    def _clean_and_finalize(self, content: str, url: str) -> str:
        """清理并添加URL"""
        
        # 清理结构化痕迹
        content = self._clean_structure(content)
        
        # 确保长度
        if len(content) > self.max_length:
            content = content[:self.max_length].rsplit(' ', 1)[0] + "..."
        
        # 添加URL
        if url:
            content += f"\n\n{url}"
        
        return content
    
    def _clean_structure(self, text: str) -> str:
        """清理结构化痕迹"""
        import re
        
        # 替换列表符号
        text = re.sub(r'^[\s]*[-*•][\s]+', '', text, flags=re.MULTILINE)
        
        # 替换序号
        text = re.sub(r'^[\s]*\d+[.、][\s]+', '', text, flags=re.MULTILINE)
        text = re.sub(r'第一|第二|第三|首先|其次|最后', '', text)
        
        # 替换结构化标题
        text = re.sub(r'主要功能[：:]|功能列表[：:]|特点[：:]', '', text)
        text = re.sub(r'使用场景[：:]|适用场景[：:]', '', text)
        text = re.sub(r'技术细节[：:]|实现原理[：:]', '', text)
        text = re.sub(r'优缺点[：:]|优势[：:]|劣势[：:]', '', text)
        
        # 替换空话
        text = re.sub(r'针对痛点|针对需求|解决痛点', '', text)
        text = re.sub(r'功能设计|架构设计', '', text)
        text = re.sub(r'旨在|致力于|目的是', '', text)
        text = re.sub(r'综上所述|总的来说|从.*来看', '', text)
        
        # 清理多余空格
        text = re.sub(r'  +', ' ', text)
        
        return text.strip()
