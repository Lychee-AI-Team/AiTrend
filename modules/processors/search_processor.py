#!/usr/bin/env python3
"""
全网评价搜索模块
使用Tavily搜索项目的全网评价
"""

import os
import requests
from typing import Dict, Any, List
from .base import BaseProcessor

class SearchProcessor(BaseProcessor):
    """
    全网评价搜索处理器
    功能：
    1. 搜索项目名称+评价/评测/体验
    2. 提取用户真实反馈
    3. 总结优缺点
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_results = config.get('max_results', 5)
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.session = requests.Session()
    
    def can_process(self, candidate: Dict[str, Any]) -> bool:
        """需要项目名称才能搜索"""
        name = candidate.get('name', '')
        return bool(name) and bool(self.tavily_api_key)
    
    def process(self, candidate: Dict[str, Any]) -> str:
        """搜索并整理全网评价"""
        
        name = candidate.get('name', '')
        description = candidate.get('description', '')
        
        # 构建搜索查询
        queries = [
            f"{name} review experience",
            f"{name} 评测 体验",
            f"{name} github alternatives comparison"
        ]
        
        all_results = []
        for query in queries[:2]:  # 搜索前2个查询
            try:
                results = self._search(query)
                all_results.extend(results)
            except Exception as e:
                print(f"    搜索失败: {e}")
        
        if not all_results:
            return ""
        
        # 提取关键信息
        pros = []
        cons = []
        user_quotes = []
        
        for result in all_results[:self.max_results]:
            content = result.get('content', '')
            
            # 简单提取正面/负面评价
            if any(word in content.lower() for word in ['good', 'great', 'awesome', 'excellent', 'love', 'perfect', '推荐']):
                # 提取这句话
                sentences = content.split('.')
                for sent in sentences:
                    if any(word in sent.lower() for word in ['good', 'great', 'awesome', 'useful', 'helpful']):
                        pros.append(sent.strip()[:100])
                        break
            
            if any(word in content.lower() for word in ['bad', 'issue', 'problem', 'bug', 'slow', 'difficult', '缺点']):
                sentences = content.split('.')
                for sent in sentences:
                    if any(word in sent.lower() for word in ['issue', 'problem', 'bug', 'limitation']):
                        cons.append(sent.strip()[:100])
                        break
            
            # 提取用户原话
            if '"' in content or '"' in content:
                import re
                quotes = re.findall(r'["""]([^"""]+)["""]', content)
                for quote in quotes[:2]:
                    if len(quote) > 20 and len(quote) < 150:
                        user_quotes.append(quote)
        
        # 组合成内容
        parts = []
        
        if user_quotes:
            parts.append(f"有用户反馈说：{user_quotes[0]}")
        
        if pros:
            parts.append(f"优点方面，{pros[0]}")
        
        if cons:
            parts.append(f"需要注意的点是{cons[0]}")
        
        if not parts:
            # 如果没有提取到具体评价，使用搜索结果摘要
            snippets = [r.get('content', '')[:100] for r in all_results[:2]]
            parts.append(f"搜索结果显示：{snippets[0]}...")
        
        return " ".join(parts)
    
    def _search(self, query: str) -> List[Dict]:
        """使用Tavily搜索"""
        
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": 3
        }
        
        response = self.session.post(url, json=payload, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        return results

# 测试
if __name__ == '__main__':
    print("="*60)
    print("全网搜索模块测试")
    print("="*60)
    
    if not os.getenv('TAVILY_API_KEY'):
        print("\n⚠️ 需要设置 TAVILY_API_KEY 环境变量")
        exit(1)
    
    config = {'max_results': 3}
    processor = SearchProcessor(config)
    
    test_candidate = {
        'name': 'browser-use',
        'description': 'Make websites accessible for AI agents'
    }
    
    print(f"\n测试项目: {test_candidate['name']}")
    result = processor.process(test_candidate)
    
    if result:
        print(f"\n搜索结果 ({len(result)} 字符):")
        print(result)
    else:
        print("\n未找到相关评价")
