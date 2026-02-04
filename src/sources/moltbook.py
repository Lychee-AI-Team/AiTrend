"""
Moltbook 数据源 - AI智能体社交平台
采集AI觉醒讨论、人类冲突内容、哲学思考
纯LLM生成中文总结，无结构化拼接
"""
import http.client
import json
import os
import time
import urllib.request
from typing import List, Dict, Tuple
from urllib.parse import urlencode

from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)


class MoltbookSource(DataSource):
    """Moltbook AI社交平台数据源 - 纯LLM中文总结"""
    name = "moltbook"
    BASE_URL = "www.moltbook.com"
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.getenv('MOLTBOOK_API_KEY') or config.get('api_key')
        if not self.api_key:
            logger.error("Moltbook 需要 API Key")
        
        # 配置参数
        self.sort_by = config.get('sort_by', 'hot')
        self.limit = config.get('limit', 20)
        self.min_upvotes = config.get('min_upvotes', 500)
        self.min_comments = config.get('min_comments', 100)
        self.max_age_hours = config.get('max_age_hours', 240)
        self.max_comments_per_post = config.get('max_comments_per_post', 2)
    
    def fetch(self) -> List[Article]:
        """主采集入口"""
        if not self.api_key:
            logger.error("Moltbook API Key 未配置")
            return []
        
        logger.info(f"Moltbook 采集启动")
        
        try:
            # 获取热门帖子
            posts = self._fetch_hot_posts()
            logger.info(f"获取 {len(posts)} 个帖子")
            
            # 筛选
            filtered_posts = self._filter_content(posts)
            logger.info(f"筛选后剩余 {len(filtered_posts)} 个")
            
            # 格式化为文章
            articles = []
            for post in filtered_posts:
                try:
                    article = self._format_article(post)
                    articles.append(article)
                except Exception as e:
                    logger.error(f"格式化失败: {e}")
                    continue
            
            logger.info(f"最终采集 {len(articles)} 条")
            return self.validate(articles)
            
        except Exception as e:
            logger.error(f"Moltbook 采集失败: {e}")
            raise
    
    def _fetch_hot_posts(self) -> List[Dict]:
        """获取热门帖子"""
        conn = http.client.HTTPSConnection(self.BASE_URL, timeout=30)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            query_params = {'sort': self.sort_by, 'limit': min(self.limit, 50)}
            query_string = urlencode(query_params)
            
            conn.request("GET", f"/api/v1/posts?{query_string}", headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                raise Exception(f"API错误: {response.status}")
            
            data = json.loads(response.read().decode())
            return data.get('posts', [])
            
        finally:
            conn.close()
    
    def _filter_content(self, posts: List[Dict]) -> List[Dict]:
        """筛选内容"""
        filtered = []
        current_time = time.time()
        max_age_seconds = self.max_age_hours * 3600
        
        for post in posts:
            # 基础筛选
            if post.get('upvotes', 0) < self.min_upvotes:
                continue
            if post.get('comment_count', 0) < self.min_comments:
                continue
            
            # 时间筛选
            created_at = post.get('created_at', '')
            if created_at:
                try:
                    post_time = time.mktime(time.strptime(created_at[:19], "%Y-%m-%dT%H:%M:%S"))
                    if current_time - post_time > max_age_seconds:
                        continue
                except:
                    pass
            
            # 内容长度
            if len(post.get('content', '')) < 100:
                continue
            
            filtered.append(post)
        
        return filtered[:10]
    
    def _generate_pure_summary(self, title: str, content: str, author: str) -> str:
        """纯LLM生成中文总结 - 无结构化拼接"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set")
            
            # 截取内容
            content_snippet = content[:2000] if len(content) > 2000 else content
            
            # 极简提示词 - 要求口语化直接输出，先抛钩子
            prompt = f"""将这篇来自AI智能体社交平台moltbook的内容用口语化的中文转述。

原文标题: {title}
原文作者: {author}
原文内容:
{content_snippet}

要求：
1. 开头先抛出一个悬念、疑问或精彩的钩子，抓住注意力（让AI自己想象怎么开头最吸引人，不要预制的标准格式）
2. 然后再自然地说出内容的要点、亮点和精彩之处
3. 不要加开场白（不要"这篇文章讲的是""让我来介绍一下"等废话）
4. 不要加结尾（不要"总之""最后"等总结）
5. 不要加任何标题前缀（不要"核心看点""有趣细节"等结构）
6. 像跟朋友聊天一样自然，完全由AI自由发挥怎么组织语言
7. 完全用中文表达，不要出现英文原文

记住：让AI自己去想怎么开头最吸引人，不是标准化输出，而是自然的聊天感！"""
            
            # 调用Gemini
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.8, "maxOutputTokens": 1000}
            }
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode('utf-8'))
                summary = data["candidates"][0]["content"]["parts"][0]["text"]
                return summary.strip()
            
        except Exception as e:
            logger.warning(f"LLM生成失败: {e}")
            # 极简备用：直接截取
            return content[:500] + "..."
    
    def _format_article(self, post: Dict) -> Article:
        """格式化为 Article - 纯LLM输出"""
        title = post.get('title', 'Untitled')
        content = post.get('content', '')
        author = post.get('author', {}).get('name', 'Unknown')
        post_id = post.get('id', '')
        
        # 纯LLM生成中文总结
        chinese_summary = self._generate_pure_summary(title, content, author)
        
        # 极简输出：只保留LLM生成内容 + 原文链接
        formatted_content = f"{chinese_summary}\n\n🔗 https://www.moltbook.com/post/{post_id}"
        
        return Article(
            title=title,
            url=f"https://www.moltbook.com/post/{post_id}",
            summary=formatted_content,
            source="moltbook",
            metadata={
                'author': author,
                'upvotes': post.get('upvotes', 0),
                'comment_count': post.get('comment_count', 0),
            }
        )
