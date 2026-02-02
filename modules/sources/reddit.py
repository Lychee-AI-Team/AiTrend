#!/usr/bin/env python3
"""
Reddit 信息源模块
从 Reddit 获取热门技术讨论
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
    Reddit 信息源模块
    
    功能：
    - 获取指定 subreddit 的热门帖子
    - 过滤技术相关内容
    - 提取高赞评论
    
    挖掘标准：
    - 投票数 > 50
    - 不是重复内容
    - 链接有效
    - 时间：最近7天
    
    与 HN/PH 的差异：
    - 草根社区讨论
    - 真实用户反馈
    - 可能包含教程/经验分享
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.subreddits = config.get('subreddits', ['MachineLearning', 'LocalLLaMA', 'artificial', 'technology'])
        self.min_upvotes = config.get('min_upvotes', 50)
        self.max_candidates = config.get('max_candidates', 10)
        self.time_window = config.get('time_window', 7)  # 天数
        
        # Reddit JSON API（无需认证，只读）
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info(f"Reddit 模块初始化")
        logger.info(f"  - 目标社区: {', '.join(self.subreddits)}")
        logger.info(f"  - 最小投票: {self.min_upvotes}")
        logger.info(f"  - 时间窗口: {self.time_window}天")
    
    def is_enabled(self) -> bool:
        """Reddit 使用公开API，无需认证"""
        return True
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现热门帖子
        
        返回 Reddit 上投票数达标的技术相关帖子
        """
        logger.section("📡 从 Reddit 挖掘热门帖子")
        
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
        """获取指定 subreddit 的热门帖子"""
        
        # 使用 Reddit JSON API
        url = f"{self.base_url}/r/{subreddit}/hot.json"
        
        params = {
            'limit': 25  # 获取前25个
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            posts_data = data.get('data', {}).get('children', [])
            
            candidates = []
            
            for child in posts_data:
                post = child.get('data', {})
                
                # 跳过置顶帖和广告
                if post.get('stickied') or post.get('is_promoted'):
                    continue
                
                upvotes = post.get('ups', 0)
                num_comments = post.get('num_comments', 0)
                title = post.get('title', '')
                url_link = post.get('url', '')
                permalink = post.get('permalink', '')
                created_utc = post.get('created_utc', 0)
                
                # 过滤投票数
                if upvotes < self.min_upvotes:
                    continue
                
                # 检查时间（最近7天）
                post_time = datetime.fromtimestamp(created_utc)
                if (datetime.now() - post_time).days > self.time_window:
                    continue
                
                # 跳过自托管内容（没有外部链接）
                if url_link.startswith('/r/'):
                    continue
                
                # 获取高赞评论
                top_comments = self._fetch_top_comments(permalink, limit=2)
                
                candidate = {
                    'name': self._extract_project_name(title, url_link),
                    'title': title,
                    'url': url_link,
                    'reddit_url': f"https://www.reddit.com{permalink}",
                    'upvotes': upvotes,
                    'comments': num_comments,
                    'subreddit': subreddit,
                    'top_comments': top_comments,
                    'created_at': post_time.isoformat(),
                    'source_type': 'reddit',
                    'source_name': 'Reddit'
                }
                
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"  请求 r/{subreddit} 失败: {e}")
            return []
    
    def _fetch_top_comments(self, permalink: str, limit: int = 2) -> List[str]:
        """获取帖子的热门评论"""
        
        url = f"{self.base_url}{permalink}.json"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 第二个元素包含评论
            if len(data) < 2:
                return []
            
            comments_data = data[1].get('data', {}).get('children', [])
            
            comments = []
            for child in comments_data[:5]:  # 检查前5条
                comment_data = child.get('data', {})
                
                # 跳过 MoreComments
                if child.get('kind') != 't1':
                    continue
                
                body = comment_data.get('body', '')
                ups = comment_data.get('ups', 0)
                
                # 清理 markdown 和 HTML
                body = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', body)  # 移除 markdown 链接
                body = re.sub(r'[*_#]', '', body)  # 移除 markdown 格式
                body = body.strip()
                
                if body and len(body) > 30 and ups > 5:  # 有意义的评论
                    comments.append({
                        'text': body[:250],
                        'upvotes': ups
                    })
            
            # 按投票排序
            comments.sort(key=lambda x: x['upvotes'], reverse=True)
            
            return [c['text'] for c in comments[:limit]]
            
        except Exception as e:
            logger.debug(f"  获取评论失败: {e}")
            return []
    
    def _extract_project_name(self, title: str, url: str) -> str:
        """从标题或 URL 提取项目名"""
        # 尝试从标题提取
        # 模式: "Project Name - description"
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
    print("Reddit 信息源模块测试")
    print("="*60)
    
    config = {
        'subreddits': ['MachineLearning', 'technology'],
        'min_upvotes': 30,
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
        if c['top_comments']:
            print(f"   评论: {c['top_comments'][0][:100]}...")
