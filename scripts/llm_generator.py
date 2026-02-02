#!/usr/bin/env python3
"""
LLM生成器 - 命令行工具
调用OpenClaw默认大模型生成内容
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def generate_with_prompt(prompt_file: str, output_file: str):
    """从文件读取提示，生成内容写入文件"""
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # 检查是否有外部API
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('KIMI_API_KEY')
    
    if api_key:
        # 使用外部API
        result = _generate_with_api(prompt, api_key)
    else:
        # 使用备用方案（简化提取）
        result = _fallback_generate(prompt)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    return result

def _generate_with_api(prompt: str, api_key: str) -> str:
    """使用API生成"""
    import requests
    
    base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 从prompt中提取system和user
    system_prompt = ""
    user_prompt = prompt
    
    if '[System]' in prompt and '[User]' in prompt:
        parts = prompt.split('[User]', 1)
        system_part = parts[0].split('[System]', 1)[1].strip()
        user_prompt = parts[1].replace('[Assistant]', '').strip()
        system_prompt = system_part
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    
    payload = {
        'model': model,
        'messages': messages,
        'temperature': 0.5,
        'max_tokens': 800
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        print(f"API错误: {e}", file=sys.stderr)
        return _fallback_generate(prompt)

def _fallback_generate(prompt: str) -> str:
    """备用生成 - 简单提取关键信息"""
    
    lines = prompt.split('\n')
    
    name = ""
    description = ""
    features = []
    
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
    
    if name and description:
        result = f"{name} {description}"
        if features:
            result += f"，主要功能包括{features[0]}"
            if len(features) > 1:
                result += f"、{features[1]}"
        return result
    
    # 返回prompt的前200字作为fallback
    return prompt[:200] if len(prompt) > 200 else prompt

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: llm_generator.py <prompt_file> <output_file>")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    output_file = sys.argv[2]
    
    result = generate_with_prompt(prompt_file, output_file)
    print(result)
