"""
LLM客户端
统一调用大模型进行内容生成
"""

import os
import requests
from typing import Dict, Any, Optional

class LLMClient:
    """
    大模型客户端
    支持：OpenAI, Kimi, 或其他兼容OpenAI API的模型
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('KIMI_API_KEY')
        self.base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
        self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.session = requests.Session()
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: str = "",
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        """
        生成内容
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 创造性 (0-1)
            max_tokens: 最大生成长度
        
        Returns:
            生成的文本
        """
        
        if not self.api_key:
            print("⚠️ 未配置API Key，跳过LLM生成")
            return ""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            return content.strip()
            
        except Exception as e:
            print(f"❌ LLM生成失败: {e}")
            return ""
    
    def summarize(self, text: str, max_length: int = 500) -> str:
        """
        总结文本
        
        提示词约束：
        - 不能结构化输出
        - 必须自然叙述
        - 突出关键信息
        """
        system_prompt = """你是一个专业的产品分析师，擅长从项目文档中提取关键信息并用自然语言描述。

重要约束：
1. 禁止结构化输出 - 不要使用列表、序号、 bullet points
2. 禁止空话套话 - 不要写"针对痛点"、"功能设计"、"架构清晰"等模板化内容
3. 必须自然叙述 - 像跟朋友介绍一个工具一样，口语化、流畅
4. 突出产品特点 - 具体是什么、能做什么、为什么值得关注
5. 突出亮点 - 最特别的地方、最实用的功能
6. 信息密度高 - 每句话都要有价值，不废话

输出风格：
- 用连续的段落，不是列表
- 用"它"、"这个工具"来指代产品
- 直接说功能，不要"旨在解决"、"致力于"
- 举例说明，不要抽象描述"""
        
        prompt = f"""请分析以下项目信息，用自然叙述的方式描述这个产品：

项目信息：
{text[:3000]}

要求：
1. 清晰描述产品是什么、做什么
2. 突出最值得关注的特点和亮点
3. 用自然叙述，不要列表、不要序号
4. 控制在{max_length}字以内
5. 直接输出描述内容，不要标题"""
        
        return self.generate(prompt, system_prompt, temperature=0.5, max_tokens=max_length)

# 单例
_llm_client = None

def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
