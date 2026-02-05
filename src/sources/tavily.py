"""
Tavily 数据源 - AI 专用搜索引擎
专为 LLM 和 RAG 场景设计，返回完整网页内容
"""
import http.client
import json
from typing import List
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class TavilySource(DataSource):
    """Tavily AI 搜索引擎数据源"""
    name = "tavily"
    BASE_URL = "api.tavily.com"
    
    def fetch(self) -> List[Article]:
        """执行 Tavily 搜索"""
        api_key = self.config.get("api_key")
        queries = self.config.get("queries", [])
        
        if not api_key:
            logger.error("Tavily 需要 API Key")
            return []
        
        if not queries:
            logger.warning("Tavily 未配置查询词")
            return []
        
        all_articles = []
        
        for query in queries:
            try:
                articles = self._search(api_key, query)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Tavily 搜索 '{query}' 失败: {e}")
                continue
        
        logger.info(f"Tavily 获取 {len(all_articles)} 条")
        return self.validate(all_articles)
    
    def _search(self, api_key: str, query: str) -> List[Article]:
        """执行单次搜索"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        
        try:
            payload = json.dumps({
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "include_images": False,
                "include_raw_content": False,
                "max_results": 5
            }, ensure_ascii=False)
            
            headers = {
                "Content-Type": "application/json"
            }
            
            conn.request("POST", "/search", body=payload.encode('utf-8'), headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                # 不记录 error_body，可能包含敏感信息
                logger.error(f"Tavily API 错误: HTTP {response.status}")
                return []
            
            data = json.loads(response.read().decode())
            return self._parse_results(data, query)
            
        finally:
            conn.close()
    
    def _parse_results(self, data: dict, query: str) -> List[Article]:
        """解析搜索结果"""
        articles = []
        results = data.get("results", [])
        
        for result in results:
            try:
                title = result.get("title", "").strip()
                url = result.get("url", "").strip()
                content = result.get("content", "").strip()
                
                if title and url:
                    articles.append(Article(
                        title=title,
                        url=url,
                        summary=content[:500],  # Tavily 返回完整内容，取前500字符
                        source="tavily",
                        metadata={
                            "query": query,
                            "score": result.get("score", 0)
                        }
                    ))
            except Exception as e:
                logger.debug(f"解析 Tavily 结果失败: {e}")
        
        return articles
