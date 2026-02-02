#!/usr/bin/env python3
"""
全网评价搜索模块（带大模型深度总结）
使用Tavily搜索项目评价，并用大模型生成自然叙述
"""

import os
import requests
from typing import Dict, Any, List
from .base import BaseProcessor
from ..llm_client import get_llm_client

class SearchProcessor(BaseProcessor):
    """
    全网评价搜索处理器（LLM增强版）
    
    功能：
    1. 搜索项目名称+评价/评测
    2. 获取多个来源的评价
    3. 调用大模型深度总结评价
    4. 生成自然叙述（非结构化）
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_results = config.get('max_results', 5)
        self.max_length = config.get('max_length', 300)
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.session = requests.Session()
        self.llm = get_llm_client()
    
    def can_process(self, candidate: Dict[str, Any]) -> bool:
        """需要项目名称和API Key"""
        name = candidate.get('name', '')
        return bool(name) and bool(self.tavily_api_key)
    
    def process(self, candidate: Dict[str, Any]) -> str:
        """搜索并深度总结全网评价"""
        
        name = candidate.get('name', '')
        description = candidate.get('description', '')
        url = candidate.get('url', '')
        
        # 搜索多个查询
        search_results = self._multi_search(name, description)
        
        if not search_results:
            return ""
        
        # 构建给LLM的输入
        context = self._build_context(name, search_results)
        
        # 调用大模型生成评价总结
        system_prompt = """你是一个专业的产品评价分析师，擅长从用户反馈中提取有价值的观点。

重要约束：
1. 禁止结构化输出 - 不要使用列表、序号、 bullet points
2. 必须自然叙述 - 像转述朋友的话一样，口语化
3. 突出用户真实反馈 - 具体用户在说什么、关心什么
4. 突出优缺点 - 用户喜欢什么、抱怨什么
5. 信息来源多样 - 综合多个来源的评价
6. 客观中立 - 既说优点也说不足

输出风格：
- 用连续的段落
- 用"有人说"、"有用户提到"来引用
- 直接说评价内容，不要"评价显示"、"反馈表明"
- 控制在300字以内"""
        
        prompt = f"""请分析以下关于「{name}」的搜索评价，用自然叙述的方式总结用户反馈：

搜索到的评价内容：
{context}

要求：
1. 总结用户的真实反馈（优点和缺点）
2. 用自然叙述，不要列表、不要序号
3. 控制在300字以内
4. 直接输出内容，不要标题"""
        
        summary = self.llm.generate(prompt, system_prompt, temperature=0.5, max_tokens=self.max_length)
        
        if not summary:
            return self._fallback_summary(search_results)
        
        return summary
    
    def _multi_search(self, name: str, description: str) -> List[Dict]:
        """执行多个搜索查询"""
        
        queries = [
            f"{name} review github experience",
            f"{name} 评测 使用体验",
        ]
        
        all_results = []
        for query in queries[:2]:
            try:
                results = self._search_tavily(query)
                all_results.extend(results)
            except Exception as e:
                print(f"    搜索失败: {e}")
        
        return all_results[:self.max_results]
    
    def _search_tavily(self, query: str) -> List[Dict]:
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
        return data.get('results', [])
    
    def _build_context(self, name: str, results: List[Dict]) -> str:
        """构建给LLM的上下文"""
        
        parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', '')
            content = result.get('content', '')
            url = result.get('url', '')
            
            if content:
                parts.append(f"来源{i} [{title}]:\n{content[:500]}")
        
        return "\n\n".join(parts)
    
    def _fallback_summary(self, results: List[Dict]) -> str:
        """LLM失败时的备用总结"""
        if not results:
            return ""
        
        # 简单拼接前几条
        snippets = []
        for r in results[:2]:
            content = r.get('content', '')[:150]
            if content:
                snippets.append(content)
        
        return " ".join(snippets) if snippets else ""
