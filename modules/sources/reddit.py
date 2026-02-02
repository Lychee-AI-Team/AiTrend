#!/usr/bin/env python3
"""
Reddit 信息源模块 - Pushshift API 版本
使用 Pushshift 无需 OAuth 即可访问 Reddit 数据
"""

import os
import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from modules.logger import get_logger
from modules.sources.base import BaseSource

logger = get_logger()

class Reddit(BaseSource):
    """
    Reddit 信息源模块（Pushshift API）
    
    功能：
    - 使用 Pushshift API 获取 Reddit 帖子
    - 无需 OAuth 认证
    - 支持多 subreddit 聚合
    - 提取热门讨论内容
    
    挖掘标准：
    - 投票数 > 50
    - 评论数 > 10
    - 时间：最近7天
    - 技术相关关键词
    
    与 HN/PH 的差异：
    - 草根社区讨论
    - 真实用户经验分享
    - 更 casual 的讨论氛围
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.subreddits = config.get('subreddits', ['MachineLearning', 'LocalLLaMA', 'artificial', 'technology'])
        self.min_upvotes = config.get('min_upvotes', 50)
        self.min_comments = config.get('min_comments', 10)
        self.max_candidates = config.get('max_candidates', 10)
        self.time_window = config.get('time_window', 7)  # 天数
        
        # Pushshift API（无需认证）
        self.pushshift_url = "https://api.pullpush.io/reddit/submission/search"
        self.reddit_url = "https://www.reddit.com"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info(f"Reddit 模块初始化 (Pushshift API)")
        logger.info(f"  - 目标社区: {', '.join(self.subreddits)}")
        logger.info(f"  - 最小投票: {self.min_upvotes}")
        logger.info(f"  - 最小评论: {self.min_comments}")
    
    def is_enabled(self) -> bool:
        """Pushshift 无需认证，始终启用"""
        return True
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现热门帖子
        
        使用 Pushshift API 获取 Reddit 帖子
        """
        logger.section("📡 从 Reddit (Pushshift) 挖掘热门帖子")
        
        all_posts = []
        
        # 遍历每个 subreddit
        for subreddit in self.subreddits:
            try:
                logger.info(f"  获取 r/{subreddit}...")
                posts = self._fetch_subreddit_posts(subreddit)
                logger.info(f"    获取 {len(posts)} 个帖子")
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"    获取失败: {e}")
        
        # 去重（按 URL）
        seen_urls = set()
        unique_posts = []
        for post in all_posts:
            url = post.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_posts.append(post)
        
        # 按投票数排序
        sorted_posts = sorted(unique_posts, key=lambda x: x.get('upvotes', 0), reverse=True)
        
        # 限制数量
        result = sorted_posts[:self.max_candidates]
        
        logger.info(f"✅ 总计发现 {len(result)} 个候选帖子")
        
        return result
    
    def _fetch_subreddit_posts(self, subreddit: str) -> List[Dict]:
        """使用 Pushshift API 获取帖子"""
        
        # 计算时间范围
        now = int(datetime.now().timestamp())
        days_ago = now - (self.time_window * 24 * 60 * 60)
        
        params = {
            'subreddit': subreddit,
            'sort': 'desc',
            'sort_type': 'score',
            'score': f">{self.min_upvotes}",
            'num_comments': f">{self.min_comments}",
            'after': days_ago,
            'before': now,
            'size': 25,
            'fields': 'title,url,permalink,score,num_comments,created_utc,selftext'
        }
        
        try:
            response = self.session.get(self.pushshift_url, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            posts_data = data.get('data', [])
            
            candidates = []
            
            for post in posts_data:
                upvotes = post.get('score', 0)
                num_comments = post.get('num_comments', 0)
                title = post.get('title', '')
                url_link = post.get('url', '')
                permalink = post.get('permalink', '')
                created_utc = post.get('created_utc', 0)
                selftext = post.get('selftext', '')
                
                # 跳过自托管内容
                if not url_link or url_link.startswith('/r/'):
                    continue
                
                # 检查是否是技术相关
                if not self._is_tech_related(title, selftext):
                    continue
                
                candidate = {
                    'name': self._extract_project_name(title, url_link),
                    'title': title,
                    'url': url_link,
                    'reddit_url': f"https://www.reddit.com{permalink}",
                    'upvotes': upvotes,
                    'comments': num_comments,
                    'subreddit': subreddit,
                    'created_at': datetime.fromtimestamp(created_utc).isoformat(),
                    'source_type': 'reddit',
                    'source_name': 'Reddit'
                }
                
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"  Pushshift 请求失败: {e}")
            return []
    
    def _is_tech_related(self, title: str, text: str) -> bool:
        """检查是否是技术相关内容"""
        content = f"{title} {text}".lower()
        
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'llm', 'gpt', 'claude', 'gemini',
            'github', 'open source', 'developer', 'programming',
            'python', 'javascript', 'rust', 'go',
            'startup', 'tech', 'software', 'app'
        ]
        
        return any(keyword in content for keyword in tech_keywords)
    
    def _extract_project_name(self, title: str, url: str) -> str:
        """从标题或 URL 提取项目名"""
        # 尝试从标题提取
        match = re.match(r'^([^-–:]+)', title)
        if match:
            name = match.group(1).strip()
            if len(name) < 50:
                return name[:50]
        
        # 从 URL 提取
        if 'github.com' in url:
            parts = url.split('/')
            if len(parts) >= 3:
                return parts[-1][:50] if parts[-1] else parts[-2][:50]
        
        # 默认返回标题前50字
        return title[:50]
    
    def get_details(self, candidate: Dict) -> Dict[str, Any]:
        """获取帖子详细信息"""
        return candidate

# 测试
if __name__ == '__main__':
    print("="*60)
    print("Reddit 信息源模块测试 (Pushshift)")
    print("="*60)
    
    config = {
        'subreddits': ['MachineLearning', 'technology'],
        'min_upvotes': 30,
        'min_comments': 5,
        'max_candidates': 5
    }
    
    source = Reddit(config)
    candidates = source.discover()
    
    print(f"\n发现 {len(candidates)} 个候选帖子:")
    for i, c in enumerate(candidates, 1):
        print(f"\n{i}. {c['name']}")
        print(f"   标题: {c['title'][:60]}...")
        print(f"   投票: {c['upvotes']}, 评论: {c['comments']}")
        print(f"   社区: r/{c['subreddit']}")
        print(f"   URL: {c['url']}")
