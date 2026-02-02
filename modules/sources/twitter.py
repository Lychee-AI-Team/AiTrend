"""
Twitter/X 信息源模块 (Cookie方式 - 使用 bird CLI)

提供功能：
- 使用Cookie访问Twitter/X
- 获取AI/ML相关热门推文
- 通过 bird CLI 工具获取数据

方式: Cookie认证 (auth_token + ct0)
依赖: @steipete/bird (需要预先安装)
"""

import subprocess
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import os


class TwitterSource:
    """Twitter/X 信息源 (使用 bird CLI)"""
    
    # 默认搜索关键词
    DEFAULT_QUERIES = [
        'AI launch',
        'machine learning',
        'ChatGPT OR Claude',
        'new AI model'
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Twitter 信息源
        
        Args:
            config: 配置字典
                - auth_token: Twitter auth_token
                - ct0: Twitter ct0
                - queries: 搜索查询列表
                - min_retweets: 最小转发数，默认 5
                - min_likes: 最小点赞数，默认 10
                - max_results: 最大结果数，默认 20
        """
        self.config = config or {}
        
        # 获取凭证
        self.auth_token = self.config.get('auth_token') or os.getenv('TWITTER_AUTH_TOKEN', '')
        self.ct0 = self.config.get('ct0') or os.getenv('TWITTER_CT0', '')
        
        # 也可以从完整的cookie字符串中提取
        cookie = self.config.get('cookie', '')
        if cookie and not self.auth_token:
            self.auth_token = self._extract_cookie(cookie, 'auth_token')
        if cookie and not self.ct0:
            self.ct0 = self._extract_cookie(cookie, 'ct0')
        
        # 其他配置
        self.queries = self.config.get('queries', self.DEFAULT_QUERIES)
        # 精华内容阈值：阅读量10万+
        self.min_views = self.config.get('min_views', 100000)  # 10万阅读
        self.min_retweets = self.config.get('min_retweets', 100)  # 100转发
        self.min_likes = self.config.get('min_likes', 500)  # 500点赞
        self.max_results = self.config.get('max_results', 50)  # 多获取一些供后续筛选
    
    def _extract_cookie(self, cookie_str: str, name: str) -> str:
        """从cookie字符串中提取值"""
        match = re.search(rf'{name}=([^;]+)', cookie_str)
        return match.group(1) if match else ''
    
    def is_enabled(self) -> bool:
        """检查是否启用（需要 auth_token 和 ct0）"""
        return bool(self.auth_token and self.ct0)
    
    def _run_bird(self, query: str) -> List[Dict]:
        """
        使用 bird CLI 搜索推文
        
        Args:
            query: 搜索查询
            
        Returns:
            推文列表
        """
        try:
            print(f"[Twitter] 搜索: {query}")
            
            # 构建 bird 命令（加载nvm环境）
            nvm_init = 'export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use --lts'
            bird_cmd = f"bird search '{query}' -n {min(self.max_results, 20)} --json --auth-token '{self.auth_token}' --ct0 '{self.ct0}'"
            
            full_cmd = f"{nvm_init} && {bird_cmd}"
            
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True,
                executable='/bin/bash'
            )
            
            if result.returncode != 0:
                print(f"[Twitter] bird 命令失败: {result.stderr[:200]}")
                return []
            
            # 解析 JSON 输出（bird输出JSON数组）
            tweets = []
            try:
                # 找到JSON数组的开始位置
                stdout = result.stdout.strip()
                # bird输出以"Now using node..."开头，需要找到"["
                json_start = stdout.find('[')
                if json_start == -1:
                    print(f"[Twitter] 未找到JSON数据")
                    return []
                
                json_data = stdout[json_start:]
                bird_tweets = json.loads(json_data)
                
                for tweet in bird_tweets:
                    # 提取互动数据
                    retweets = tweet.get('retweetCount', 0)
                    likes = tweet.get('likeCount', 0)
                    
                    # 获取阅读量（views/impressions）
                    views = tweet.get('viewCount', 0) or tweet.get('views', 0)
                    
                    # 数据筛选：必须满足高阈值
                    meets_threshold = (
                        views >= self.min_views or 
                        retweets >= self.min_retweets or 
                        likes >= self.min_likes
                    )
                    
                    if meets_threshold:
                        author = tweet.get('author', {})
                        tweets.append({
                            'id': str(tweet.get('id', '')),
                            'text': tweet.get('text', ''),
                            'created_at': tweet.get('createdAt', ''),
                            'view_count': views,
                            'retweet_count': retweets,
                            'like_count': likes,
                            'reply_count': tweet.get('replyCount', 0),
                            'author_username': author.get('username', 'unknown'),
                            'author_name': author.get('name', 'Unknown'),
                            'author_followers': 0,
                            'tweet_url': f"https://twitter.com/{author.get('username', 'user')}/status/{tweet.get('id', '')}",
                            'meets_data_threshold': True  # 标记已通过数据筛选
                        })
            except json.JSONDecodeError as e:
                print(f"[Twitter] JSON解析错误: {e}")
            except Exception as e:
                print(f"[Twitter] 解析错误: {e}")
            
            print(f"[Twitter] 找到 {len(tweets)} 条推文")
            return tweets
            
        except subprocess.TimeoutExpired:
            print("[Twitter] bird 命令超时")
            return []
        except FileNotFoundError:
            print("[Twitter] bird CLI 未安装")
            print("  安装: npm install -g @steipete/bird")
            return []
        except Exception as e:
            print(f"[Twitter] 错误: {e}")
            return []
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现热门推文
        
        Returns:
            候选推文列表
        """
        if not self.is_enabled():
            print("[Twitter] 未配置 auth_token/ct0，跳过")
            return []
        
        all_tweets = []
        
        for query in self.queries[:3]:  # 限制查询数量
            try:
                tweets = self._run_bird(query)
                all_tweets.extend(tweets)
            except Exception as e:
                print(f"[Twitter] 查询失败: {e}")
                continue
        
        # 去重
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
            candidates.append({
                'name': f"@{tweet['author_username']}: {tweet['text'][:60]}",
                'title': tweet['text'][:100],
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
    cookie = 'guest_id_marketing=v1%3A176987549229925032; guest_id_ads=v1%3A176987549229925032; guest_id=v1%3A176987549229925032; personalization_id="v1_9kVMSKZuCxk+EpvF1/g8GA=="; gt=2017630167401943362; __cuid=19e2a63ef6a547bbadbed3e6587222ab; g_state={"i_l":0,"i_ll":1769875479841,"i_b":"oS5VXXuka/LSdTJncUa3mOWQ1RnzhyELXSVtD9AbhYs","i_e":{"enable_itp_optimization":3}}; kdt=ZBkjw7T6361ogMpQQJd4qeHS0CkHEVnWJYfruk0K; auth_token=b8630954ba040bdb5f9fc8b79c4adc67457eabfe; ct0=31455a7de266a10216ac5eb0b17dfe9098dc7628bbfb4138d195a148ad5bc45a8eb0187a726f4c8f4e0ce31ddda65a8f612c87aa8f5e64e05b6bf7b22039a046e23eeaed3149a8fd0d810ca5bd059e08; att=1-AanaTf8KCdNVUUcLXYScJCtoiFQcMROFpURu3hTK; lang=zh-cn; twid=u%3D1135576048177836033; __cf_bm=8zx92X463tzLbfA8t39wtqmIkWO4VbjhO98P7uVh8as-1769875791.704196-1.0.1.1-7rUFG.x0VrZA2O3PYtLHysdE9M0WyHY.R3RZth2lKbEB8U_inG6_9MtzrBaEfTLWg1eP56xlU7HfJh0m5Ztw0LipA9_A27tLmVXCirIZPs66LwTqbz92ju3lWTWTQgi4'
    
    config = {
        'cookie': cookie,
        'queries': ['AI launch'],
        'min_retweets': 1,
        'min_likes': 1,
        'max_results': 5
    }
    
    twitter = TwitterSource(config)
    
    print(f"✅ auth_token: {'有效' if twitter.auth_token else '无效'}")
    print(f"✅ ct0: {'有效' if twitter.ct0 else '无效'}")
    
    if not twitter.is_enabled():
        print("❌ 未配置")
        exit(1)
    
    tweets = twitter.discover()
    
    print(f"\n找到 {len(tweets)} 条推文:\n")
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"{i}. @{tweet['author_username']}")
        print(f"   {tweet['text'][:100]}...")
        print(f"   🔁 {tweet['retweets']} ❤️ {tweet['likes']}")
        print()
