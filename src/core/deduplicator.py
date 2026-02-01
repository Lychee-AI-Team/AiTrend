"""
文章去重管理器
确保同一条数据24小时内不重复出现
"""
import json
import os
import time
from typing import List, Dict, Set
from src.sources.base import Article

class ArticleDeduplicator:
    """文章去重器 - 24小时滑动窗口"""
    
    def __init__(self, memory_path: str = None):
        if memory_path is None:
            # 默认路径：项目根目录下的 memory/sent_articles.json
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            memory_path = os.path.join(base_dir, 'memory', 'sent_articles.json')
        
        self.memory_path = memory_path
        self.window_hours = 24  # 24小时窗口
        
        # 确保目录存在
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    
    def load_sent_articles(self) -> List[Dict]:
        """加载已发送的文章记录"""
        if not os.path.exists(self.memory_path):
            return []
        
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('articles', [])
        except:
            return []
    
    def save_sent_articles(self, articles: List[Dict]):
        """保存已发送的文章记录"""
        data = {
            'description': '记录已发送的文章，24小时内不重复',
            'articles': articles
        }
        
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def is_duplicate(self, url: str) -> bool:
        """检查是否是24小时内已发送的重复内容"""
        if not url:
            return False
        
        sent_articles = self.load_sent_articles()
        current_time = time.time()
        window_seconds = self.window_hours * 3600
        
        for article in sent_articles:
            # URL匹配
            if article.get('url') == url:
                sent_at = article.get('sent_at', 0)
                # 检查是否在24小时内
                if current_time - sent_at < window_seconds:
                    return True
        
        return False
    
    def filter_new_articles(self, articles: List[Article]) -> List[Article]:
        """过滤掉24小时内已发送的文章"""
        new_articles = []
        
        for article in articles:
            if not self.is_duplicate(article.url):
                new_articles.append(article)
        
        return new_articles
    
    def record_sent_articles(self, articles: List[Article]):
        """记录已发送的文章"""
        sent_articles = self.load_sent_articles()
        current_time = time.time()
        window_seconds = self.window_hours * 3600
        
        # 清理超过24小时的旧记录
        sent_articles = [
            a for a in sent_articles 
            if current_time - a.get('sent_at', 0) < window_seconds
        ]
        
        # 添加新记录
        existing_urls = {a.get('url') for a in sent_articles}
        
        for article in articles:
            if article.url and article.url not in existing_urls:
                sent_articles.append({
                    'url': article.url,
                    'title': article.title,
                    'sent_at': current_time,
                    'sent_count': 1
                })
        
        self.save_sent_articles(sent_articles)
    
    def get_stats(self) -> Dict:
        """获取去重统计"""
        sent_articles = self.load_sent_articles()
        current_time = time.time()
        window_seconds = self.window_hours * 3600
        
        # 24小时内的记录
        active = [a for a in sent_articles if current_time - a.get('sent_at', 0) < window_seconds]
        
        return {
            'total_recorded': len(sent_articles),
            'active_in_24h': len(active),
            'window_hours': self.window_hours
        }
