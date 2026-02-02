"""
Twitter 内容生成器

生成中文介绍文本：
- 推文核心观点
- 作者背景
- 社区反响（转发/点赞）
- 相关话题价值

最终输出：中文
"""

from typing import Dict, Any, List


class TwitterContentComposer:
    """Twitter 推文中文内容生成器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    def compose_narrative(self, tweet: Dict[str, Any]) -> str:
        """
        生成叙述式中文介绍
        
        Args:
            tweet: 推文信息
            
        Returns:
            自然叙述式中文文本
        """
        text = tweet.get('text', '')
        author = tweet.get('author', 'Unknown')
        username = tweet.get('author_username', 'unknown')
        followers = tweet.get('author_followers', 0)
        retweets = tweet.get('retweets', 0)
        likes = tweet.get('likes', 0)
        replies = tweet.get('replies', 0)
        url = tweet.get('url', '')
        
        # 格式化粉丝数
        followers_str = self._format_number(followers)
        
        # 格式化互动数
        engagement_str = f"🔁 {retweets} 次转发，❤️ {likes} 次点赞"
        
        # 生成内容
        lines = []
        
        # 开头：介绍作者和影响力
        lines.append(f"Twitter 用户 @{username} ({author}) 分享了关于 AI 的见解，该账号拥有 {followers_str} 关注者。")
        
        # 推文核心内容
        clean_text = text.replace('\n', ' ').strip()
        if len(clean_text) > 150:
            clean_text = clean_text[:150] + "..."
        
        lines.append(f"推文内容：「{clean_text}」")
        
        # 社区反响
        lines.append(f"这条推文获得了 {engagement_str}，{self._engagement_level(retweets, likes)}。")
        
        # 价值判断
        if retweets > 100 or likes > 500:
            lines.append("作为一条被广泛传播的技术推文，它反映了当前 AI 社区关注的热点话题。")
        elif followers > 10000:
            lines.append(f"鉴于作者在该领域的影响力，这条推文值得关注。")
        else:
            lines.append("这条推文提供了来自技术社区的实时声音。")
        
        # 链接
        lines.append("")
        lines.append(f"🐦 原文: {url}")
        
        return '\n'.join(lines)
    
    def _format_number(self, n: int) -> str:
        """格式化数字"""
        if n >= 1000000:
            return f"{n/1000000:.1f}M"
        elif n >= 1000:
            return f"{n/1000:.1f}K"
        return str(n)
    
    def _engagement_level(self, retweets: int, likes: int) -> str:
        """判断互动水平"""
        total = retweets + likes
        if total > 1000:
            return "在社区引起了较大反响"
        elif total > 100:
            return "获得了不错的关注度"
        elif total > 50:
            return "有一定讨论热度"
        else:
            return "属于小众但高质量的内容"


if __name__ == "__main__":
    # 测试
    test_tweet = {
        'text': 'Just launched our new AI tool that can generate code from natural language descriptions. Check it out! 🚀 #AI #BuildInPublic',
        'author': 'John Developer',
        'author_username': 'johndev',
        'author_followers': 15000,
        'retweets': 45,
        'likes': 230,
        'replies': 12,
        'url': 'https://twitter.com/johndev/status/1234567890'
    }
    
    composer = TwitterContentComposer()
    print(composer.compose_narrative(test_tweet))
