"""
LLM内容生成器
使用Gemini API为每个项目生成独特内容
严格遵守AiTrend宪法文档要求
"""
import os
import google.generativeai as genai
from typing import Dict, Optional

class LLMContentGenerator:
    """使用Gemini生成独特内容"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate(self, article_data: Dict) -> str:
        """
        基于文章数据生成独特内容
        返回：生成的内容或抛出异常
        """
        title = article_data.get('title', '')
        summary = article_data.get('summary', '')
        url = article_data.get('url', '')
        source = article_data.get('source', '')
        metadata = article_data.get('metadata', {})
        
        # 构建提示词
        prompt = self._build_prompt(title, summary, url, source, metadata)
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # 验证内容质量 - 严格检查宪法禁止项
            if self._is_low_quality(content):
                raise RuntimeError(f"❌ LLM生成内容违反宪法：检测到禁止的套话或模板化文字")
            
            # 确保URL在内容中
            if url not in content:
                content = f"{content} {url}"
            
            return content
            
        except Exception as e:
            raise RuntimeError(f"❌ LLM生成失败：{str(e)}")
    
    def _build_prompt(self, title: str, summary: str, url: str, source: str, metadata: Dict) -> str:
        """构建提示词 - 严格遵守宪法文档"""
        
        lang = metadata.get('language', '')
        stars = metadata.get('stars', 0)
        
        base_info = f"""项目名称：{title}
项目介绍：{summary}
来源：{source}
链接：{url}"""
        
        if lang:
            base_info += f"\n编程语言：{lang}"
        if stars:
            base_info += f"\nGitHub Stars：{stars}"
        
        # 严格遵循宪法文档的禁止项和必须项
        return f"""基于以下项目信息，写一段150-200字的项目介绍。

【绝对禁止 - 硬性约束】
1. ❌ 禁止套话开头："最近发现"、"今天看到"、"找到一个"、"发现一个"
2. ❌ 禁止"这是一个..."、"是一个..."的句式
3. ❌ 禁止"主要解决...问题"、"主要功能包括"
4. ❌ 禁止序号：第一第二、首先其次
5. ❌ 禁止列表符号：- * •
6. ❌ 禁止空话："针对痛点"、"功能设计"、"架构清晰"、"旨在解决"
7. ❌ 禁止重复用词和句式

【必须遵守】
1. ✅ 直接描述产品是什么、能做什么、为什么值得用
2. ✅ 连续段落，无结构化痕迹
3. ✅ 控制在150-200字
4. ✅ 最后必须包含链接
5. ✅ 不要分段，写成一段连续文本

项目信息：
{base_info}

直接输出介绍内容（不要加标题、不要加总结、不要分段）："""
    
    def _is_low_quality(self, content: str) -> bool:
        """检查是否低质量（违反宪法）"""
        # 宪法明确禁止的套话
        forbidden_patterns = [
            "最近发现",
            "今天看到",
            "找到一个",
            "发现一个",
            "最近",
            "今天",
            "这是一个",
            "是一个",
            "主要解决",
            "主要功能",
            "使用场景",
            "技术细节",
            "优缺点",
            "详细介绍",
            "详细信息",
            "针对痛点",
            "功能设计",
            "架构清晰",
            "旨在解决",
        ]
        
        # 检查禁止的模式
        for pattern in forbidden_patterns:
            if pattern in content:
                return True
        
        # 检查列表符号
        list_symbols = ['- ', '* ', '• ', '1.', '2.', '3.']
        for symbol in list_symbols:
            if symbol in content:
                return True
        
        # 检查序号词
        sequence_words = ['第一', '第二', '第三', '首先', '其次', '最后']
        for word in sequence_words:
            if word in content:
                return True
        
        return False

# 单例
_llm_generator = None

def get_llm_generator() -> LLMContentGenerator:
    """获取LLM生成器单例"""
    global _llm_generator
    if _llm_generator is None:
        _llm_generator = LLMContentGenerator()
    return _llm_generator
