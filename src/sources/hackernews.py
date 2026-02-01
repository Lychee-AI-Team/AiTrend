"""
HackerNews AI 热点监控 - 纯标准库版本
获取 Show HN 和 AI 相关热门帖子
"""
import http.client
import json
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class HackerNewsSource(DataSource):
    """HackerNews AI 热点数据源"""
    name = "hackernews"
    
    # HN 官方 API
    BASE_URL = "hacker-news.firebaseio.com"
    
    # AI 相关关键词
    AI_KEYWORDS = [
        "ai", "artificial intelligence", "llm", "gpt", "claude", "openai",
        "machine learning", "neural", "model", "agent", "autonomous"
    ]
    
    def fetch(self) -> List[Article]:
        """获取 HN 热门 AI 相关帖子"""
        all_posts = []
        
        try:
            # 获取 Show HN 帖子
            show_hn = self._fetch_show_hn()
            all_posts.extend(show_hn)
            
            # 获取当前热门帖子并筛选 AI 相关
            top_stories = self._fetch_top_stories()
            ai_posts = [p for p in top_stories if self._is_ai_related(p)]
            all_posts.extend(ai_posts)
            
            logger.info(f"HackerNews 获取 {len(all_posts)} 条（Show HN: {len(show_hn)}, AI相关: {len(ai_posts)}）")
            
        except Exception as e:
            logger.error(f"获取 HackerNews 失败: {e}")
        
        # 按 score 排序，取前 10
        sorted_posts = sorted(all_posts, key=lambda x: x.metadata.get('score', 0), reverse=True)[:10]
        return sorted_posts
    
    def _fetch_show_hn(self) -> List[Article]:
        """获取 Show HN 帖子"""
        # Show HN 的 ID 列表
        story_ids = self._get_story_ids("showstories")
        return self._fetch_stories(story_ids[:15], "show_hn")
    
    def _fetch_top_stories(self) -> List[Article]:
        """获取热门帖子"""
        story_ids = self._get_story_ids("topstories")
        return self._fetch_stories(story_ids[:30], "top")
    
    def _get_story_ids(self, category: str) -> List[int]:
        """获取帖子 ID 列表"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        try:
            conn.request("GET", f"/v0/{category}.json")
            response = conn.getresponse()
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            return []
        finally:
            conn.close()
    
    def _fetch_stories(self, story_ids: List[int], source_type: str) -> List[Article]:
        """获取帖子详情"""
        posts = []
        
        for story_id in story_ids:
            try:
                conn = http.client.HTTPSConnection(self.BASE_URL, timeout=10)
                conn.request("GET", f"/v0/item/{story_id}.json")
                response = conn.getresponse()
                
                if response.status == 200:
                    story = json.loads(response.read().decode('utf-8'))
                    if story and not story.get('deleted') and not story.get('dead'):
                        post = self._parse_story(story, source_type)
                        if post:
                            posts.append(post)
                
                conn.close()
                
            except Exception as e:
                logger.debug(f"获取 story {story_id} 失败: {e}")
                continue
        
        return posts
    
    def _parse_story(self, story: Dict, source_type: str) -> Article:
        """解析帖子数据"""
        title = story.get('title', '').strip()
        url = story.get('url', '')
        score = story.get('score', 0)
        
        # 过滤低质量帖子
        if score < 10 or not title:
            return None
        
        # 如果没有外部链接，使用 HN 讨论页
        if not url:
            url = f"https://news.ycombinator.com/item?id={story.get('id')}"
        
        # 构建摘要
        text = story.get('text', '')[:200] if story.get('text') else ''
        tag = "[Show HN]" if source_type == "show_hn" else "[HN]"
        summary = text or f"HackerNews 热门讨论，{story.get('descendants', 0)} 条评论"
        
        return Article(
            title=f"{tag} {title}",
            url=url,
            summary=summary,
            source="hackernews",
            metadata={
                "score": score,
                "comments": story.get('descendants', 0),
                "type": source_type
            }
        )
    
    def _is_ai_related(self, post: Article) -> bool:
        """判断是否是 AI 相关帖子"""
        text = (post.title + " " + post.summary).lower()
        return any(keyword in text for keyword in self.AI_KEYWORDS)
