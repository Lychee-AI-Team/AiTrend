"""
Brave Search 数据源 - 纯标准库版本
使用 http.client 替代 aiohttp
"""
import http.client
import json
from typing import List
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class BraveSearchSource(DataSource):
    """Brave Search 数据源 - 纯标准库版本"""
    name = "brave_search"
    BASE_URL = "api.search.brave.com"
    
    def fetch(self) -> List[Article]:
        """执行 Brave Search（同步版本）"""
        api_key = self.config.get("api_key")
        queries = self.config.get("queries", [])
        freshness = self.config.get("freshness", "pd")
        count = self.config.get("count", 5)
        
        if not api_key:
            logger.error("Brave Search 需要 API Key")
            return []
        
        if not queries:
            logger.warning("Brave Search 未配置查询词")
            return []
        
        all_articles = []
        
        for query in queries:
            try:
                articles = self._search(api_key, query, freshness, count)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"搜索 '{query}' 失败: {e}")
                continue
        
        logger.info(f"Brave Search 获取 {len(all_articles)} 条")
        return self.validate(all_articles)
    
    def _search(self, api_key: str, query: str, 
                freshness: str, count: int) -> List[Article]:
        """执行单次搜索（使用 http.client）"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            
            # URL 编码查询词
            from urllib.parse import quote
            encoded_query = quote(query)
            params = f"?q={encoded_query}&freshness={freshness}&count={count}"
            
            conn.request("GET", f"/res/v1/web/search{params}", headers=headers)
            
            response = conn.getresponse()
            if response.status != 200:
                error_body = response.read().decode('utf-8')
                logger.error(f"Brave API 错误: {response.status} - {error_body}")
                return []
            
            data = json.loads(response.read().decode('utf-8'))
            return self._parse_results(data, query)
            
        finally:
            conn.close()
    
    def _parse_results(self, data: dict, query: str) -> List[Article]:
        """解析搜索结果"""
        articles = []
        results = data.get("web", {}).get("results", [])
        
        for result in results:
            try:
                title = result.get("title", "").strip()
                url = result.get("url", "").strip()
                description = result.get("description", "").strip()
                
                if title and url:
                    articles.append(Article(
                        title=title,
                        url=url,
                        summary=description,
                        source="brave_search",
                        metadata={
                            "query": query,
                            "age": result.get("age", "")
                        }
                    ))
            except Exception as e:
                logger.debug(f"解析结果失败: {e}")
                continue
        
        return articles
