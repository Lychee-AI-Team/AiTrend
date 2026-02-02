"""
LLM客户端 - 简化版
通过文件通信与launcher交互
"""

import os
import json
import tempfile
from typing import Dict, Any

class LLMClient:
    """
    大模型客户端
    
    两种模式：
    1. 外部API模式：直接调用API
    2. OpenClaw模式：通过文件与launcher通信
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('KIMI_API_KEY')
        self.use_external_api = bool(self.api_key)
        
        if self.use_external_api:
            self.base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
            self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        
        # OpenClaw通信文件
        self.request_file = '/tmp/openclaw_llm_request.json'
        self.response_file = '/tmp/openclaw_llm_response.txt'
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: str = "",
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        """生成内容"""
        
        if self.use_external_api:
            return self._generate_with_api(prompt, system_prompt, temperature, max_tokens)
        else:
            # OpenClaw模式 - 使用备用方案（简单提取）
            # 因为无法直接从子进程中调用sessions_spawn
            print(f"    🤖 使用备用生成方案...", end=' ')
            return self._fallback_extract(prompt)
    
    def _generate_with_api(self, prompt: str, system_prompt: str,
                           temperature: float, max_tokens: int) -> str:
        """使用外部API生成"""
        
        import requests
        
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
            session = requests.Session()
            response = session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            result = data['choices'][0]['message']['content'].strip()
            print("✅")
            return result
            
        except Exception as e:
            print(f"❌ {e}")
            return self._fallback_extract(prompt)
    
    def summarize(self, text: str, max_length: int = 500) -> str:
        """总结文本"""
        
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
        
        result = self.generate(prompt, system_prompt, temperature=0.5, max_tokens=max_length)
        
        if not result:
            return self._fallback_extract(text)
        
        return result
    
    def _fallback_extract(self, text: str) -> str:
        """备用提取 - 智能提取关键信息"""
        
        lines = text.split('\n')
        name = ""
        description = ""
        features = []
        install = ""
        usage = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('项目名称:') or '项目名称:' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    name = parts[1].strip()
            elif line.startswith('项目描述:') or '项目描述:' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    description = parts[1].strip()
            elif line.startswith('功能列表:') or '功能列表:' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    features = [f.strip() for f in parts[1].split(',')]
            elif line.startswith('安装方式:') or '安装方式:' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    install = parts[1].strip()
            elif line.startswith('使用示例:') or '使用示例:' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    usage = parts[1].strip()
        
        # 构建自然叙述
        if name and description:
            parts = [f"{name} {description}"]
            
            if features:
                feats_text = "、".join(features[:3])
                parts.append(f"可以{feats_text}")
            
            if install:
                parts.append(f"安装命令是{install}")
            
            result = "。".join(parts)
            print(f"✅ ({len(result)} 字符)")
            return result
        
        print("⚠️ 提取失败")
        return ""

# 单例
_llm_client = None

def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
