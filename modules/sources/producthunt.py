#!/usr/bin/env python3
"""
Product Hunt 信息源模块
从 Product Hunt 获取热门产品信息
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from modules.logger import get_logger
from modules.sources.base import BaseSource

logger = get_logger()

class Producthunt(BaseSource):
    """
    Product Hunt 信息源模块
    
    功能：
    - 获取每日/每周热门产品
    - 筛选 AI/开发者工具类别
    - 提取产品描述、评价、Maker信息
    
    挖掘标准：
    - 分类：AI/ML, Developer Tools, Productivity
    - 投票数 > 50
    - 时间：今日或本周
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_token = config.get('api_token') or os.getenv('PRODUCTHUNT_TOKEN')
        self.min_votes = config.get('min_votes', 50)
        self.categories = config.get('categories', ['AI', 'Developer Tools', 'Productivity'])
        self.time_period = config.get('time_period', 'daily')  # daily 或 weekly
        self.max_candidates = config.get('max_candidates', 10)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        })
        
        logger.info(f"Producthunt 模块初始化")
        logger.info(f"  - 最小投票数: {self.min_votes}")
        logger.info(f"  - 目标分类: {', '.join(self.categories)}")
        logger.info(f"  - 时间周期: {self.time_period}")
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return bool(self.api_token)
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现候选产品
        
        返回 Product Hunt 上投票数达标的热门产品
        """
        logger.section("📡 从 Product Hunt 挖掘产品")
        
        if not self.api_token:
            logger.error("❌ 未配置 Product Hunt API Token")
            logger.info("请在 .env 中设置: PRODUCTHUNT_TOKEN=your_token")
            return []
        
        all_posts = []
        
        # 获取每个分类的产品
        for category in self.categories:
            try:
                logger.info(f"  获取分类: {category}")
                posts = self._fetch_posts_by_topic(category)
                logger.info(f"    获取 {len(posts)} 个产品")
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"    获取失败: {e}")
        
        # 去重（按产品名）
        seen_names = set()
        unique_posts = []
        for post in all_posts:
            name = post.get('name', '')
            if name and name not in seen_names:
                seen_names.add(name)
                unique_posts.append(post)
        
        # 过滤投票数
        filtered = [p for p in unique_posts if p.get('votes', 0) >= self.min_votes]
        
        # 按投票数排序
        sorted_posts = sorted(filtered, key=lambda x: x.get('votes', 0), reverse=True)
        
        # 限制数量
        result = sorted_posts[:self.max_candidates]
        
        logger.info(f"✅ 总计发现 {len(result)} 个候选产品")
        
        return result
    
    def _fetch_posts_by_topic(self, topic: str) -> List[Dict]:
        """通过主题获取产品列表 - 简化版，获取每日热门"""
        
        url = "https://api.producthunt.com/v2/api/graphql"
        
        # 简化查询：获取最近的热门产品
        query = """
        query {
          posts(first: 20, order: RANKING) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                website
                votesCount
                createdAt
                makers {
                  name
                  username
                }
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
        
        payload = {
            "query": query
        }
        
        try:
            logger.info(f"    正在请求 Product Hunt API...")
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'errors' in data:
                logger.error(f"    API错误: {data['errors']}")
                return []
            
            posts_data = data.get('data', {}).get('posts', {}).get('edges', [])
            logger.info(f"    API返回 {len(posts_data)} 个产品")
            
            candidates = []
            for edge in posts_data:
                node = edge.get('node', {})
                
                # 检查产品分类是否匹配
                product_topics = [t.get('node', {}).get('name', '').lower() 
                                 for t in node.get('topics', {}).get('edges', [])]
                
                topic_lower = topic.lower()
                if topic_lower not in product_topics and topic_lower not in node.get('tagline', '').lower():
                    # 不匹配当前分类，跳过
                    continue
                
                created_at = node.get('createdAt', '')
                
                candidate = {
                    'name': node.get('name', ''),
                    'tagline': node.get('tagline', ''),
                    'description': node.get('description', ''),
                    'url': node.get('url', ''),
                    'website': node.get('website', ''),
                    'votes': node.get('votesCount', 0),
                    'created_at': created_at,
                    'makers': [m.get('name', '') for m in node.get('makers', [])],
                    'topics': product_topics,
                    'source_type': 'producthunt',
                    'source_name': 'producthunt'
                }
                
                candidates.append(candidate)
            
            logger.info(f"    其中 {len(candidates)} 个匹配分类 '{topic}'")
            return candidates
            
        except Exception as e:
            logger.error(f"    请求失败: {e}")
            return []
    
    def get_details(self, candidate: Dict) -> Dict[str, Any]:
        """
        获取产品详细信息
        包括评论、更多描述等
        """
        # Product Hunt API 限制，详细信息在 discover 时已获取
        # 可以在这里添加评论获取等额外逻辑
        return candidate

# 测试
if __name__ == '__main__':
    print("="*60)
    print("Product Hunt 信息源模块测试")
    print("="*60)
    
    config = {
        'categories': ['AI', 'Developer Tools'],
        'min_votes': 30,
        'time_period': 'daily',
        'max_candidates': 5
    }
    
    source = Producthunt(config)
    
    if not source.is_enabled():
        print("\n⚠️ 未配置 PRODUCTHUNT_TOKEN")
        print("请在 .env 文件中设置:")
        print("  PRODUCTHUNT_TOKEN=your_token_here")
        exit(1)
    
    candidates = source.discover()
    
    print(f"\n发现 {len(candidates)} 个候选产品:")
    for i, c in enumerate(candidates, 1):
        print(f"\n{i}. {c['name']}")
        print(f"   Tagline: {c['tagline'][:80]}...")
        print(f"   Votes: {c['votes']}")
        print(f"   URL: {c['url']}")
