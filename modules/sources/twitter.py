"""
Twitter/X 信息源模块

提供功能：
- 搜索 Twitter 上 AI/ML 相关的热门推文
- 支持按关键词、时间筛选
- 提取推文内容、作者、互动数据

API: Twitter API v2 (使用 OAuth 1.0a)
认证: Consumer Key + Secret（用户提供）
"""

import requests
import base64
import hashlib
import hmac
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os


class TwitterSource:
    """Twitter/X 信息源"""
    
    API_BASE = "https://api.twitter.com/2"
    
    # 默认搜索关键词
    DEFAULT_QUERIES = [
        '"AI tool" OR "AI launch" -is:retweet lang:en',
        '"machine learning" OR "new model" -is:retweet lang:en',
        '#BuildInPublic AI -is:retweet lang:en',
        'ChatGPT OR Claude OR Gemini launch -is:retweet lang:en'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Twitter 信息源
        
        Args:
            config: 配置字典
                - api_key: Twitter API Key
                - api_secret: Twitter API Key Secret
                - queries: 搜索查询列表
                - min_retweets: 最小转发数，默认 10
                - min_likes: 最小点赞数，默认 20
                - days_back: 回溯天数，默认 1
                - max_results: 最大结果数，默认 20
        """
        self.config = config or {}
        
        # 从配置或环境变量获取凭证
        self.api_key = self.config.get('api_key') or os.getenv('TWITTER_API_KEY')
        self.api_secret = self.config.get('api_secret') or os.getenv('TWITTER_API_SECRET')
        
        self.queries = self.config.get('queries', self.DEFAULT_QUERIES)
        self.min_retweets = self.config.get('min_retweets', 10)
        self.min_likes = self.config.get('min_likes', 20)
        self.days_back = self.config.get('days_back', 1)
        self.max_results = self.config.get('max_results', 20)
        
        # Bearer Token（用于应用认证）
        self.bearer_token = None
        
    def is_enabled(self) -> bool:
        """检查是否启用（需要 API Key）"""
        return bool(self.api_key and self.api_secret)
    
    def _get_bearer_token(self) -> Optional[str]:
        """
        获取 Bearer Token（OAuth 2.0 应用认证）
        
        使用 Consumer Key 和 Secret 换取 Bearer Token
        """
        if self.bearer_token:
            return self.bearer_token
        
        try:
            # 构建认证字符串
            credentials = f"{self.api_key}:{self.api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # 请求 Bearer Token
            url = "https://api.twitter.com/oauth2/token"
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
            }
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.bearer_token = token_data.get('access_token')
            return self.bearer_token
            
        except Exception as e:
            print(f"[Twitter] 获取 Bearer Token 失败: {e}")
            return None
    
    def _search_tweets(self, query: str) -> List[Dict]:
        """
        搜索推文
        
        Args:
            query: 搜索查询
            
        Returns:
            推文列表
        """
        bearer_token = self._get_bearer_token()
        if not bearer_token:
            return []
        
        try:
            # 构建请求
            url = f"{self.API_BASE}/tweets/search/recent"
            
            # 计算开始时间（ISO 8601 格式）
            start_time = (datetime.utcnow() - timedelta(days=self.days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            params = {
                'query': query,
                'max_results': min(self.max_results, 100),
                'tweet.fields': 'created_at,public_metrics,author_id,source',
                'expansions': 'author_id',
                'user.fields': 'username,public_metrics,description',
                'start_time': start_time
            }
            
            headers = {
                'Authorization': f'Bearer {bearer_token}'
            }
            
            print(f"[Twitter] 搜索: {query[:50]}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 429:
                print("[Twitter] 速率限制，请稍后再试")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            tweets = data.get('data', [])
            includes = data.get('includes', {})
            users = {u['id']: u for u in includes.get('users', [])}
            
            # 处理推文数据
            results = []
            for tweet in tweets:
                metrics = tweet.get('public_metrics', {})
                author_id = tweet.get('author_id')
                author = users.get(author_id, {})
                
                # 筛选条件
                retweet_count = metrics.get('retweet_count', 0)
                like_count = metrics.get('like_count', 0)
                
                if retweet_count >= self.min_retweets or like_count >= self.min_likes:
                    results.append({
                        'id': tweet.get('id'),
                        'text': tweet.get('text', ''),
                        'created_at': tweet.get('created_at'),
                        'retweet_count': retweet_count,
                        'like_count': like_count,
                        'reply_count': metrics.get('reply_count', 0),
                        'quote_count': metrics.get('quote_count', 0),
                        'author_username': author.get('username', 'unknown'),
                        'author_name': author.get('name', 'Unknown'),
                        'author_followers': author.get('public_metrics', {}).get('followers_count', 0),
                        'tweet_url': f"https://twitter.com/{author.get('username', 'user')}/status/{tweet.get('id')}"
                    })
            
            print(f"[Twitter] 找到 {len(results)} 条热门推文")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"[Twitter] 请求失败: {e}")
            return []
        except Exception as e:
            print(f"[Twitter] 处理错误: {e}")
            return []
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现热门推文
        
        Returns:
            候选推文列表
        """
        if not self.is_enabled():
            print("[Twitter] 未配置 API Key，跳过")
            return []
        
        all_tweets = []
        
        for query in self.queries:
            try:
                tweets = self._search_tweets(query)
                all_tweets.extend(tweets)
                
                # 避免速率限制
                time.sleep(1)
                
            except Exception as e:
                print(f"[Twitter] 查询失败 '{query[:30]}...': {e}")
                continue
        
        # 去重（按推文ID）
        seen_ids = set()
        unique_tweets = []
        for tweet in all_tweets:
            if tweet['id'] not in seen_ids:
                seen_ids.add(tweet['id'])
                unique_tweets.append(tweet)
        
        # 按互动数排序
        unique_tweets.sort(key=lambda x: x['retweet_count'] + x['like_count'], reverse=True)
        
        # 转换为统一格式
        candidates = []
        for tweet in unique_tweets[:self.max_results]:
            # 构建描述
            engagement = f"🔁{tweet['retweet_count']} ❤️{tweet['like_count']}"
            description = f"@{tweet['author_username']}: {tweet['text'][:200]}...\n\n{engagement}"
            
            candidates.append({
                'name': f"Tweet by @{tweet['author_username']}",
                'title': tweet['text'][:100],
                'description': description,
                'text': tweet['text'],
                'author': tweet['author_name'],
                'author_username': tweet['author_username'],
                'author_followers': tweet['author_followers'],
                'retweets': tweet['retweet_count'],
                'likes': tweet['like_count'],
                'replies': tweet['reply_count'],
                'url': tweet['tweet_url'],
                'created_at': tweet['created_at'],
                'source': 'Twitter',
                'type': 'tweet'
            })
        
        print(f"[Twitter] 共 {len(candidates)} 条候选推文")
        return candidates
    
    def discover_single(self) -> Optional[Dict[str, Any]]:
        """获取单条热门推文"""
        tweets = self.discover()
        return tweets[0] if tweets else None


if __name__ == "__main__":
    # 测试
    import os
    
    # 使用用户提供的 API Key
    config = {
        'api_key': 'kwjFF1m2uTXzkFNCw0AMEkXpP',
        'api_secret': 'Q6RNe8O1mhNR9AHb5809TIumai7rfRqZFJ9oxWX4dkGf5QFpPV',
        'queries': ['AI launch -is:retweet lang:en'],
        'min_retweets': 5,
        'min_likes': 10,
        'days_back': 1,
        'max_results': 5
    }
    
    twitter = TwitterSource(config)
    
    if not twitter.is_enabled():
        print("❌ 未配置 API Key")
        exit(1)
    
    tweets = twitter.discover()
    
    print(f"\n找到 {len(tweets)} 条推文:\n")
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"{i}. @{tweet['author_username']} ({tweet['author_followers']} 粉丝)")
        print(f"   {tweet['text'][:100]}...")
        print(f"   🔁 {tweet['retweets']} ❤️ {tweet['likes']}")
        print(f"   {tweet['url']}")
        print()
