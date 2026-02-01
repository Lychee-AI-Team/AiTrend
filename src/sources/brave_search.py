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
    
    # 官方新闻源域名（降低权重）
    OFFICIAL_NEWS_DOMAINS = [
        "36kr.com", "techcrunch.com", "theverge.com", "venturebeat.com",
        " bloomberg.com", "reuters.com", "cnbc.com", "forbes.com"
    ]
    
    def _parse_results(self, data: dict, query: str) -> List[Article]:
        """解析搜索结果"""
        articles = []
        results = data.get("web", {}).get("results", [])
        
        for result in results:
            try:
                title = result.get("title", "").strip()
                url = result.get("url", "").strip()
                description = result.get("description", "").strip()
                
                if not title or not url:
                    continue
                
                # 检测是否为官方新闻源
                is_official_news = any(domain in url.lower() for domain in self.OFFICIAL_NEWS_DOMAINS)
                
                # 检测标题是否为官方发布类新闻
                official_keywords = ["发布", "宣布", "推出", "融资", "上市", "财报", "市值"]
                is_official_title = any(kw in title for kw in official_keywords) and is_official_news
                
                # 官方新闻降低权重（metadata中标记）
                weight = 0.3 if is_official_news else 1.0
                
                articles.append(Article(
                    title=title,
                    url=url,
                    summary=description,
                    source="brave_search",
                    metadata={
                        "query": query,
                        "age": result.get("age", ""),
                        "is_official_news": is_official_news,
                        "weight": weight
                    }
                ))
            except Exception as e:
                logger.debug(f"解析结果失败: {e}")
                continue
        
        return articles
