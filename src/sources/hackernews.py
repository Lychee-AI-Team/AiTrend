"""
HackerNews AI 热点监控 - 使用 urllib 版本
获取 Show HN 和 AI 相关热门帖子
"""
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class HackerNewsSource(DataSource):
    """HackerNews AI 热点数据源"""
    name = "hackernews"
    
    # HN 官方 API
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    # AI 相关关键词
    AI_KEYWORDS = [
        "kimi", "通义千问", "文心一言", "智谱", "deepseek",
        "字节", "腾讯", "阿里", "百度", "华为", "国产", "中文",
        "openai", "chatgpt", "claude", "anthropic", "gemini",
        "llm", "ai", "machine learning", "gpt-4", "gpt4",
        "open ai", "mistral", "llama", "anthropic", "perplexity"
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
        story_ids = self._get_story_ids("showstories")
        return self._fetch_stories(story_ids[:8], "show_hn")
    
    def _fetch_top_stories(self) -> List[Article]:
        """获取热门帖子"""
        story_ids = self._get_story_ids("topstories")
        return self._fetch_stories(story_ids[:15], "top")
    
    def _get_story_ids(self, category: str) -> List[int]:
        """获取帖子 ID 列表"""
        url = f"{self.BASE_URL}/{category}.json"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.warning(f"获取 {category} ID 列表失败: {e}")
            return []
    
    def _fetch_stories(self, story_ids: List[int], source_type: str) -> List[Article]:
        """获取帖子详情"""
        posts = []
        
        for story_id in story_ids[:8]:  # 限制数量
            try:
                url = f"{self.BASE_URL}/item/{story_id}.json"
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                })
                with urllib.request.urlopen(req, timeout=8) as response:
                    story = json.loads(response.read().decode('utf-8'))
                    
                if story and not story.get('deleted') and not story.get('dead'):
                    post = self._parse_story(story, source_type)
                    if post:
                        posts.append(post)
                        
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
        
        # 确保摘要有足够信息量（至少30字符以满足LLM输入验证）
        if text:
            summary = text
        else:
            comment_count = story.get('descendants', 0)
            score_val = story.get('score', 0)
            summary = f"HackerNews 热门讨论，热度分数 {score_val}，共有 {comment_count} 条评论参与讨论。这是一个关于 {title[:30]}... 的社区热门话题"
        
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
