#!/usr/bin/env python3
"""
使用Tavily搜索获取AI产品详细信息
"""

import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend/src')

# 读取环境变量
env_path = '/home/ubuntu/.openclaw/workspace/AiTrend/.env'
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value

# 设置环境变量
for key, value in env_vars.items():
    os.environ[key] = value

from tavily import TavilyClient
import json

def search_product_info(product_name: str) -> dict:
    """搜索产品详细信息"""
    
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("错误: TAVILY_API_KEY 未设置")
        return None
    
    client = TavilyClient(api_key=api_key)
    
    # 搜索产品信息
    query = f"{product_name} AI product features what does it do 2026"
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=3
        )
        
        results = response.get('results', [])
        
        if results:
            # 提取最相关的结果
            best_result = results[0]
            return {
                'title': best_result.get('title', ''),
                'content': best_result.get('content', ''),
                'url': best_result.get('url', ''),
            }
        
        return None
        
    except Exception as e:
        print(f"搜索失败: {e}")
        return None


def main():
    """搜索3个产品的详细信息"""
    
    products = [
        "ClawApp",
        "OpenAI Frontier", 
        "Obi Product Hunt"
    ]
    
    print("=" * 60)
    print("🔍 使用Tavily搜索产品详细信息")
    print("=" * 60)
    
    for product in products:
        print(f"\n{'='*60}")
        print(f"搜索: {product}")
        print(f"{'='*60}")
        
        info = search_product_info(product)
        
        if info:
            print(f"标题: {info['title']}")
            print(f"内容: {info['content'][:400]}...")
            print(f"URL: {info['url']}")
        else:
            print("未找到信息")


if __name__ == '__main__':
    main()
