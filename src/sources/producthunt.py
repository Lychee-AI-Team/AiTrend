"""
Product Hunt AI 产品监控 - 纯标准库版本
获取每日新上线的 AI 产品
"""
import http.client
import json
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class ProductHuntSource(DataSource):
    """Product Hunt AI 产品数据源"""
    name = "producthunt"
    
    BASE_URL = "api.producthunt.com"
    
    def fetch(self) -> List[Article]:
        """获取今日 AI 相关产品"""
        api_key = self.config.get("api_key")
        if not api_key:
            logger.error("Product Hunt API Key 未配置")
            return []
        
        try:
            posts = self._fetch_today_posts(api_key)
            # 筛选 AI 相关产品
            ai_posts = [p for p in posts if self._is_ai_related(p)]
            logger.info(f"Product Hunt 获取 {len(ai_posts)} 条 AI 产品（总计 {len(posts)} 条）")
            return ai_posts[:10]
            
        except Exception as e:
            logger.error(f"获取 Product Hunt 失败: {e}")
            return []
    
    def _fetch_today_posts(self, api_key: str) -> List[Article]:
        """获取今日帖子"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # GraphQL 查询
            query = {
                "query": """
                {
                    posts(order: RANKING, first: 20) {
                        edges {
                            node {
                                id
                                name
                                tagline
                                description
                                url
                                votesCount
                                commentsCount
                                topics {
                                    edges {
                                        node {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                """
            }
            
            conn.request("POST", "/v2/api/graphql", body=json.dumps(query), headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                logger.warning(f"Product Hunt API 返回状态 {response.status}")
                return []
            
            data = json.loads(response.read().decode('utf-8'))
            return self._parse_posts(data)
            
        finally:
            conn.close()
    
    def _parse_posts(self, data: Dict) -> List[Article]:
        """解析帖子数据"""
        posts = []
        
        edges = data.get('data', {}).get('posts', {}).get('edges', [])
        
        for edge in edges:
            try:
                node = edge.get('node', {})
                
                name = node.get('name', '').strip()
                tagline = node.get('tagline', '').strip()
                description = node.get('description', '')[:300] if node.get('description') else ''
                url = node.get('url', '')
                votes = node.get('votesCount', 0)
                comments = node.get('commentsCount', 0)
                
                # 获取话题标签
                topics = []
                for topic_edge in node.get('topics', {}).get('edges', []):
                    topic_name = topic_edge.get('node', {}).get('name', '')
                    if topic_name:
                        topics.append(topic_name)
                
                # 构建摘要
                summary = tagline
                if description and len(description) > len(tagline):
                    summary = description
                
                posts.append(Article(
                    title=f"[Product Hunt] {name} ⭐{votes}",
                    url=url,
                    summary=summary,
                    source="producthunt",
                    metadata={
                        "votes": votes,
                        "comments": comments,
                        "topics": topics
                    }
                ))
                
            except Exception as e:
                logger.debug(f"解析 Product Hunt 帖子失败: {e}")
                continue
        
        return posts
    
    def _is_ai_related(self, post: Article) -> bool:
        """判断是否是 AI 相关产品"""
        text = (post.title + " " + post.summary).lower()
        topics = [t.lower() for t in post.metadata.get('topics', [])]
        
        ai_keywords = [
            "ai", "artificial intelligence", "machine learning", "llm",
            "gpt", "claude", "openai", "assistant", "automation",
            "productivity", "writing", "image generation", "chatbot"
        ]
        
        # 检查标题和摘要
        if any(keyword in text for keyword in ai_keywords):
            return True
        
        # 检查话题标签
        ai_topics = ["artificial intelligence", "machine learning", "productivity", "developer tools"]
        if any(topic in topics for topic in ai_topics):
            return True
        
        return False
