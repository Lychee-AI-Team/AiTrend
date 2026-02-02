#!/usr/bin/env python3
"""
LLM生成器 - 使用OpenClaw默认大模型
通过调用 sessions_spawn 实现

使用方法：
    python3 llm_openclaw.py <prompt_file> <output_file>
"""

import sys
import os
import json

def main():
    if len(sys.argv) < 3:
        print("Usage: llm_openclaw.py <prompt_file> <output_file>")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # 读取提示
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # 这里我们无法直接调用sessions_spawn，因为它是一个工具
    # 所以这个脚本需要通过 launcher 的特殊方式调用
    
    # 写入一个标记文件，表示需要LLM生成
    request_file = '/tmp/llm_request.json'
    with open(request_file, 'w', encoding='utf-8') as f:
        json.dump({
            'prompt': prompt,
            'output_file': output_file
        }, f)
    
    print(f"LLM请求已写入: {request_file}")
    print("请使用launcher的generate_with_llm方法处理")

if __name__ == '__main__':
    main()
