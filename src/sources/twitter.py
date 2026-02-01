"""
Twitter/X AI 热点监控 - 使用 bird CLI
获取 AI 相关的 viral 推文和新产品发布
"""
import subprocess
import json
import re
from typing import List, Dict, Any
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class TwitterSource(DataSource):
    """Twitter AI 热点数据源 - 使用 bird CLI"""
    name = "twitter"
    
    # AI 相关账号和关键词
    AI_ACCOUNTS = [
        "@OpenAI", "@AnthropicAI", "@GoogleAI", "@DeepMind",
        "@xai", "@ stabilityai", "@AIatMeta",
        "@karpathy", "@ylecun", "@goodfellow_ian"
    ]
    
    # AI 关键词（中国:美国 = 7:3）
    # 中国 AI 关键词（70%）
    CN_KEYWORDS = [
        "Kimi", "通义千问", "文心一言", "智谱", "DeepSeek",
        "字节跳动", "腾讯", "阿里", "百度", "华为盘古",
        "中国AI", "国产大模型", "中文大模型", "国内首发"
    ]
    # 美国/国际 AI 关键词（30%）
    INTL_KEYWORDS = [
        "OpenAI", "ChatGPT", "Claude", "Gemini", "Anthropic",
        "new model", "just released", "announcing"
    ]
    AI_KEYWORDS = CN_KEYWORDS + INTL_KEYWORDS
    
    def fetch(self) -> List[Article]:
        """获取 Twitter AI 相关内容"""
        auth_token = self.config.get("auth_token")
        ct0 = self.config.get("ct0")
        
        if not auth_token or not ct0:
            logger.error("Twitter Cookie 未配置")
            return []
        
        try:
            # 获取 For You 时间线
            tweets = self._fetch_timeline(auth_token, ct0)
            
            # 筛选 AI 相关内容
            ai_tweets = [t for t in tweets if self._is_ai_related(t)]
            
            logger.info(f"Twitter 获取 {len(ai_tweets)} 条 AI 相关内容（总计 {len(tweets)} 条）")
            return ai_tweets[:10]
            
        except Exception as e:
            logger.error(f"获取 Twitter 失败: {e}")
            return []
    
    def _fetch_timeline(self, auth_token: str, ct0: str) -> List[Article]:
        """获取 Twitter 时间线"""
        # 使用 bird CLI 获取时间线
        cmd = f"""export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && nvm use --lts 2>/dev/null && \
bird home -n 100 --auth-token "{auth_token}" --ct0 "{ct0}" --json 2>/dev/null"""
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            logger.warning(f"bird CLI 执行失败: {result.stderr}")
            return []
        
        # 解析 JSON 输出
        lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('Now using node')]
        
        try:
            tweets_data = json.loads('\n'.join(lines))
            if isinstance(tweets_data, list):
                return self._parse_tweets(tweets_data)
            return []
        except json.JSONDecodeError:
            logger.warning("Twitter 数据解析失败")
            return []
    
    def _parse_tweets(self, tweets_data: List[Dict]) -> List[Article]:
        """解析推文数据"""
        tweets = []
        
        for tweet in tweets_data:
            try:
                text = tweet.get('text', '').strip()
                author = tweet.get('author', {}).get('username', '')
                tweet_id = tweet.get('id', '')
                likes = tweet.get('likeCount', 0)
                retweets = tweet.get('retweetCount', 0)
                
                # 过滤低质量推文
                if not text or len(text) < 30:
                    continue
                
                # 清理文本
                text = self._clean_text(text)
                
                url = f"https://x.com/{author}/status/{tweet_id}"
                
                tweets.append(Article(
                    title=f"[Twitter] @{author}",
                    url=url,
                    summary=text[:200],
                    source="twitter",
                    metadata={
                        "author": author,
                        "likes": likes,
                        "retweets": retweets
                    }
                ))
                
            except Exception as e:
                logger.debug(f"解析推文失败: {e}")
                continue
        
        return tweets
    
    def _clean_text(self, text: str) -> str:
        """清理推文文本"""
        # 移除 t.co 链接
        text = re.sub(r'https://t\.co/\S+', '', text)
        # 移除图片/视频标记
        text = re.sub(r'🖼️\s*', '', text)
        text = re.sub(r'🎬\s*', '', text)
        # 清理多余空格
        text = ' '.join(text.split())
        return text.strip()
    
    def _is_ai_related(self, tweet: Article) -> bool:
        """判断是否是 AI 相关推文"""
        text = (tweet.title + " " + tweet.summary).lower()
        author = tweet.metadata.get('author', '').lower()
        
        # 检查是否是 AI 相关账号
        ai_authors = [
            'openai', 'anthropicai', 'googleai', 'deepmind', 'xai',
            'karpathy', 'ylecun', 'goodfellow', 'jackclark',
            'moltbook', 'openclaw'
        ]
        if any(ai in author for ai in ai_authors):
            return True
        
        # 检查关键词
        if any(keyword in text for keyword in self.AI_KEYWORDS):
            return True
        
        # 检查 AI 关键词
        ai_terms = ['ai', 'llm', 'gpt', 'claude', 'model', 'tool', 'app', 'launch']
        if any(term in text for term in ai_terms):
            # 额外检查热度
            if tweet.metadata.get('likes', 0) > 50:
                return True
        
        return False
