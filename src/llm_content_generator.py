"""
LLM内容生成器
使用Gemini API为每个项目生成独特内容
严格禁止模板化文字
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
        
        # 构建提示词 - 要求独特叙述，禁止模板
        prompt = self._build_prompt(title, summary, url, source, metadata)
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # 验证内容质量
            if self._is_low_quality(content):
                raise RuntimeError(f"❌ LLM生成内容质量过低：检测到模板化文字")
            
            # 确保URL在内容中
            if url not in content:
                content = f"{content} {url}"
            
            return content
            
        except Exception as e:
            raise RuntimeError(f"❌ LLM生成失败：{str(e)}")
    
    def _build_prompt(self, title: str, summary: str, url: str, source: str, metadata: Dict) -> str:
        """构建提示词"""
        
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
        
        return f"""基于以下项目信息，写一段150-200字的独特介绍。

要求：
1. 直接切入项目核心价值，不要用"这是一个..."的开头
2. 基于提供的具体信息，不要编造功能
3. 使用自然流畅的中文，像朋友推荐好东西一样
4. 禁止模板化表达，如"主要解决...问题"、"是一个...工具"
5. 结尾自然，不要总结式结尾
6. 不要分段，写成一段连续的文本

项目信息：
{base_info}

直接输出介绍内容（不要加标题、不要加总结）："""
    
    def _is_low_quality(self, content: str) -> bool:
        """检查是否低质量（模板化）"""
        templates = [
            "这是一个",
            "是一个",
            "主要解决",
            "主要功能",
            "使用场景",
            "技术细节",
            "优缺点",
            "详细介绍",
            "详细信息",
        ]
        
        for template in templates:
            if template in content:
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
