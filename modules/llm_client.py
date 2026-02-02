"""
LLM客户端 - 使用OpenClaw默认大模型
通过 sessions_spawn 调用
"""

import os
import json
import time
from typing import Dict, Any, Optional

class LLMClient:
    """大模型客户端 - OpenClaw集成版"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY') or os.getenv('KIMI_API_KEY')
        self.use_external_api = bool(self.api_key)
        
        if self.use_external_api:
            self.base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
            self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    def generate(self, 
                 prompt: str, 
                 system_prompt: str = "",
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        """生成内容"""
        
        if self.use_external_api:
            return self._generate_with_api(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_with_openclaw(prompt, system_prompt, max_tokens)
    
    def _generate_with_openclaw(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """使用本地脚本生成（备用方案）"""
        
        import tempfile
        import subprocess
        import os
        
        # 构建完整提示
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"[System]\n{system_prompt}\n\n[User]\n{prompt}\n\n[Assistant]\n"
        
        print(f"    🤖 调用LLM生成 ({len(full_prompt)} 字符)...", end=' ')
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(full_prompt)
                prompt_file = f.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                output_file = f.name
            
            # 调用生成脚本
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'llm_generator.py')
            
            result = subprocess.run(
                ['python3', script_path, prompt_file, output_file],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # 读取输出
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            else:
                content = ""
            
            # 清理临时文件
            try:
                os.unlink(prompt_file)
                os.unlink(output_file)
            except:
                pass
            
            if content:
                print("✅")
                return content
            else:
                print("⚠️ 无输出，使用备用方案")
                return self._fallback_extract(full_prompt)
            
        except Exception as e:
            print(f"❌ {e}")
            return self._fallback_extract(full_prompt)
    
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
            return data['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            return ""
    
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
        """备用提取"""
        lines = text.split('\n')
        name = desc = ""
        features = []
        
        for line in lines:
            if '项目名称:' in line:
                name = line.split(':', 1)[1].strip()
            elif '项目描述:' in line:
                desc = line.split(':', 1)[1].strip()
            elif '功能列表:' in line:
                features = [f.strip() for f in line.split(':', 1)[1].split(',')]
        
        if name and desc:
            result = f"{name} {desc}"
            if features:
                result += f"，可以{features[0]}"
            return result
        return ""

# 单例
_llm_client = None

def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
