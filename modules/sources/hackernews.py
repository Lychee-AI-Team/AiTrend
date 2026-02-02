#!/usr/bin/env python3
"""
HackerNews 信息源模块
从 HackerNews 获取热门技术讨论和项目
"""

import os
import re
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from modules.logger import get_logger
from modules.sources.base import BaseSource

logger = get_logger()

class Hackernews(BaseSource):
    """
    HackerNews 信息源模块
    
    功能：
    - 获取热门帖子（top stories, best stories）
    - 过滤技术相关标签
    - 提取高赞评论
    
    挖掘标准：
    - 分数 > 100
    - 评论数 > 20
    - 链接指向 GitHub 或产品页
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = "https://hacker-news.firebaseio.com/v0"
        self.min_points = config.get('min_points', 100)
        self.min_comments = config.get('min_comments', 20)
        self.max_candidates = config.get('max_candidates', 10)
        self.target_keywords = config.get('keywords', ['AI', 'machine learning', 'open source', 'github', 'developer', 'programming'])
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info(f"Hackernews 模块初始化")
        logger.info(f"  - 最小分数: {self.min_points}")
        logger.info(f"  - 最小评论: {self.min_comments}")
    
    def is_enabled(self) -> bool:
        """HackerNews API 无需认证，始终启用"""
        return True
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现热门帖子
        
        返回 HN 上分数达标的技术相关帖子
        """
        logger.section("📡 从 HackerNews 挖掘热门帖子")
        
        all_candidates = []
        
        # 获取 top stories
        try:
            logger.info("  获取 Top Stories...")
            top_ids = self._fetch_story_ids('topstories')
            candidates = self._process_stories(top_ids[:30])  # 处理前30个
            logger.info(f"    获取 {len(candidates)} 个帖子")
            all_candidates.extend(candidates)
        except Exception as e:
            logger.error(f"    获取失败: {e}")
        
        # 获取 best stories
        try:
            logger.info("  获取 Best Stories...")
            best_ids = self._fetch_story_ids('beststories')
            candidates = self._process_stories(best_ids[:30])
            logger.info(f"    获取 {len(candidates)} 个帖子")
            all_candidates.extend(candidates)
        except Exception as e:
            logger.error(f"    获取失败: {e}")
        
        # 去重（按 ID）
        seen_ids = set()
        unique_candidates = []
        for c in all_candidates:
            item_id = c.get('id', '')
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_candidates.append(c)
        
        # 按分数排序
        sorted_candidates = sorted(unique_candidates, key=lambda x: x.get('points', 0), reverse=True)
        
        # 限制数量
        result = sorted_candidates[:self.max_candidates]
        
        logger.info(f"✅ 总计发现 {len(result)} 个候选帖子")
        
        return result
    
    def _fetch_story_ids(self, story_type: str) -> List[int]:
        """获取故事 ID 列表"""
        url = f"{self.api_base}/{story_type}.json"
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        return response.json() or []
    
    def _process_stories(self, story_ids: List[int]) -> List[Dict]:
        """处理故事列表，筛选技术相关内容"""
        candidates = []
        
        for story_id in story_ids:
            try:
                story = self._fetch_item(story_id)
                if not story:
                    continue
                
                # 检查是否是故事（不是评论或job）
                if story.get('type') != 'story':
                    continue
                
                points = story.get('score', 0)
                comments = story.get('descendants', 0)
                title = story.get('title', '')
                url = story.get('url', '')
                
                # 过滤条件
                if points < self.min_points:
                    continue
                
                if comments < self.min_comments:
                    continue
                
                # 检查是否技术相关
                if not self._is_tech_related(title, url):
                    continue
                
                # 获取高赞评论
                top_comments = self._fetch_top_comments(story_id, limit=3)
                
                candidate = {
                    'id': story_id,
                    'name': self._extract_project_name(title, url),
                    'title': title,
                    'url': url or f"https://news.ycombinator.com/item?id={story_id}",
                    'points': points,
                    'comments': comments,
                    'top_comments': top_comments,
                    'hn_url': f"https://news.ycombinator.com/item?id={story_id}",
                    'source_type': 'hackernews',
                    'source_name': 'HackerNews'
                }
                
                candidates.append(candidate)
                
            except Exception as e:
                logger.debug(f"    处理故事 {story_id} 失败: {e}")
                continue
        
        return candidates
    
    def _fetch_item(self, item_id: int) -> Dict:
        """获取单个项目详情"""
        url = f"{self.api_base}/item/{item_id}.json"
        
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        return response.json() or {}
    
    def _is_tech_related(self, title: str, url: str) -> bool:
        """检查是否是技术相关内容"""
        text = f"{title} {url}".lower()
        
        # 检查关键词
        for keyword in self.target_keywords:
            if keyword.lower() in text:
                return True
        
        # 检查是否是 GitHub 链接
        if 'github.com' in url:
            return True
        
        return False
    
    def _fetch_top_comments(self, story_id: int, limit: int = 3) -> List[str]:
        """获取高赞评论 - 简化版，避免过多网络请求"""
        # 暂时跳过评论获取，避免性能问题
        # 后续可以添加缓存或批量获取优化
        return []
    
    def _extract_project_name(self, title: str, url: str) -> str:
        """从标题或URL提取项目名"""
        # 尝试从标题提取
        # 模式: "Show HN: Project Name - description"
        match = re.match(r'Show HN:\s*([^-–:]+)', title, re.I)
        if match:
            return match.group(1).strip()[:50]
        
        # 模式: "Project Name: description"
        match = re.match(r'^([^:]+):', title)
        if match and len(match.group(1)) < 50:
            return match.group(1).strip()[:50]
        
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
    print("HackerNews 信息源模块测试")
    print("="*60)
    
    config = {
        'min_points': 50,
        'min_comments': 10,
        'max_candidates': 5
    }
    
    source = Hackernews(config)
    candidates = source.discover()
    
    print(f"\n发现 {len(candidates)} 个候选帖子:")
    for i, c in enumerate(candidates, 1):
        print(f"\n{i}. {c['name']}")
        print(f"   标题: {c['title'][:60]}...")
        print(f"   分数: {c['points']}, 评论: {c['comments']}")
        print(f"   URL: {c['url']}")
        if c['top_comments']:
            print(f"   评论预览: {c['top_comments'][0][:100]}...")
