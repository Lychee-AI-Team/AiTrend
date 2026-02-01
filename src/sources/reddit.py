"""
Reddit AI 热点监控 - 使用 Pushshift API
无需 OAuth，直接获取 Reddit AI 相关帖子
"""
import http.client
import json
import time
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class RedditSource(DataSource):
    """Reddit AI 热点数据源 - 使用 Pushshift API"""
    name = "reddit"
    
    # Pushshift API 地址
    BASE_URL = "api.pullpush.io"
    
    # AI 相关 subreddit
    SUBREDDITS = [
        "ChinaAI", "ChineseAI", "KimiAI", "TongyiQianwen", "WenxinYiyan",
        "DeepSeekAI", "ByteDanceAI", "TencentAI",
        "artificial", "MachineLearning", "OpenAI", "ChatGPT", "ClaudeAI",
    ]
    
    def fetch(self) -> List[Article]:
        """使用 Pushshift API 获取 Reddit AI 相关帖子"""
        all_posts = []
        
        # 获取最近 24 小时的热门帖子
        for subreddit in self.SUBREDDITS:
            try:
                posts = self._fetch_subreddit(subreddit)
                all_posts.extend(posts)
                logger.info(f"Reddit r/{subreddit} 获取 {len(posts)} 条")
                # 避免请求过快
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"获取 r/{subreddit} 失败: {e}")
                continue
        
        # 去重并按 score 排序
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
        """使用 Pushshift API 获取指定 subreddit 的帖子"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        
        try:
            # 获取热门帖子（不按时间过滤，因为 Pushshift 数据有延迟）
            # sort_type=score: 按分数排序
            # sort=desc: 降序
            # size=10: 取前 10 条
            path = f"/reddit/search/submission/?subreddit={subreddit}&sort_type=score&sort=desc&size=10"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                logger.warning(f"Pushshift r/{subreddit} 返回状态 {response.status}")
                return []
            
            data = json.loads(response.read().decode('utf-8'))
            return self._parse_posts(data, subreddit)
            
        finally:
            conn.close()
    
    def _parse_posts(self, data: Dict, subreddit: str) -> List[Article]:
        """解析 Pushshift 返回的帖子数据"""
        posts = []
        
        for post in data.get('data', []):
            try:
                title = post.get('title', '').strip()
                url = post.get('full_link', '')
                score = post.get('score', 0)
                comments = post.get('num_comments', 0)
                selftext = post.get('selftext', '')[:200] if post.get('selftext') else ''
                
                # 过滤低质量帖子（降低阈值）
                if score < 3 or not title:
                    continue
                
                # 构建摘要
                summary = selftext or f"来自 r/{subreddit} 的热门讨论，{comments} 条评论"
                
                posts.append(Article(
                    title=f"[Reddit] {title}",
                    url=url,
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
