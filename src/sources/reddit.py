"""
Reddit AI 热点监控 - 纯标准库版本
爬取 r/artificial、r/MachineLearning 等 AI 相关 subreddit
"""
import http.client
import json
import re
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class RedditSource(DataSource):
    """Reddit AI 热点数据源 - 爬取 AI 相关 subreddit"""
    name = "reddit"
    
    SUBREDDITS = [
        "artificial",
        "MachineLearning",
        "OpenAI",
        "ChatGPT",
        "ClaudeAI",
        "LocalLLaMA",
        "singularity"
    ]
    
    def fetch(self) -> List[Article]:
        """爬取 Reddit AI 相关帖子"""
        all_posts = []
        
        for subreddit in self.SUBREDDITS:
            try:
                posts = self._fetch_subreddit(subreddit)
                all_posts.extend(posts)
                logger.info(f"Reddit r/{subreddit} 获取 {len(posts)} 条")
            except Exception as e:
                logger.error(f"获取 r/{subreddit} 失败: {e}")
                continue
        
        # 去重并按热度排序
        seen = set()
        unique_posts = []
        for post in all_posts:
            if post.url not in seen:
                seen.add(post.url)
                unique_posts.append(post)
        
        # 按 score 排序，取前 15
        sorted_posts = sorted(unique_posts, key=lambda x: x.metadata.get('score', 0), reverse=True)[:15]
        
        logger.info(f"Reddit 总计获取 {len(sorted_posts)} 条热门帖子")
        return sorted_posts
    
    def _fetch_subreddit(self, subreddit: str) -> List[Article]:
        """获取指定 subreddit 的热门帖子"""
        conn = http.client.HTTPSConnection("www.reddit.com", timeout=30)
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            
            # 获取热门帖子（时间范围：本周）
            path = f"/r/{subreddit}/hot.json?limit=10&t=week"
            conn.request("GET", path, headers=headers)
            
            response = conn.getresponse()
            if response.status != 200:
                logger.warning(f"Reddit r/{subreddit} 返回状态 {response.status}")
                return []
            
            data = json.loads(response.read().decode('utf-8'))
            return self._parse_posts(data, subreddit)
            
        finally:
            conn.close()
    
    def _parse_posts(self, data: Dict, subreddit: str) -> List[Article]:
        """解析 Reddit 帖子数据"""
        posts = []
        
        for child in data.get('data', {}).get('children', []):
            try:
                post = child.get('data', {})
                
                title = post.get('title', '').strip()
                url = post.get('url', '')
                score = post.get('score', 0)
                comments = post.get('num_comments', 0)
                
                # 过滤低质量帖子
                if score < 10 or not title:
                    continue
                
                # 构建摘要
                selftext = post.get('selftext', '')[:200] if post.get('selftext') else ''
                summary = selftext or f"来自 r/{subreddit} 的热门讨论，{comments} 条评论"
                
                posts.append(Article(
                    title=f"[Reddit] {title}",
                    url=url if not url.startswith('/r/') else f"https://www.reddit.com{url}",
                    summary=summary,
                    source="reddit",
                    metadata={
                        "subreddit": subreddit,
                        "score": score,
                        "comments": comments
                    }
                ))
                
            except Exception as e:
                logger.debug(f"解析 Reddit 帖子失败: {e}")
                continue
        
        return posts
