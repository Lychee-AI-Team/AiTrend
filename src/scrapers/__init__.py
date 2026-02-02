"""
页面抓取模块基类
统一接口，支持GitHub、Product Hunt、HackerNews等数据源
"""

import requests
import re
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from urllib.parse import urlparse

class BaseScraper(ABC):
    """抓取器基类"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """是否能处理该URL"""
        pass
    
    @abstractmethod
    def scrape(self, url: str) -> Dict:
        """
        抓取页面并提取关键信息
        返回必须包含：
        - name: 项目名称
        - description: 项目描述
        - features: 功能列表
        - source: 数据来源
        """
        pass
    
    def fetch(self, url: str) -> str:
        """获取页面HTML"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"抓取失败 {url}: {e}")
            return ""

class GitHubScraper(BaseScraper):
    """GitHub项目抓取器"""
    
    def can_handle(self, url: str) -> bool:
        return 'github.com' in url and '/blob/' not in url
    
    def scrape(self, url: str) -> Dict:
        """抓取GitHub项目信息"""
        result = {
            'name': '',
            'description': '',
            'tagline': '',
            'features': [],
            'install': '',
            'usage': '',
            'tech_stack': [],
            'stars': 0,
            'url': url,
            'source': 'github'
        }
        
        # 获取README内容（通过API）
        repo_path = self._extract_repo_path(url)
        if not repo_path:
            return result
        
        # 获取repo基本信息
        repo_info = self._fetch_repo_info(repo_path)
        if repo_info:
            result['name'] = repo_info.get('name', '')
            result['description'] = repo_info.get('description', '')
            result['stars'] = repo_info.get('stargazers_count', 0)
            result['tagline'] = repo_info.get('description', '')
        
        # 获取README内容
        readme = self._fetch_readme(repo_path)
        if readme:
            # 提取功能列表
            result['features'] = self._extract_features(readme)
            # 提取安装说明
            result['install'] = self._extract_installation(readme)
            # 提取使用示例
            result['usage'] = self._extract_usage(readme)
            # 检测技术栈
            result['tech_stack'] = self._detect_tech_stack(repo_path, readme)
        
        return result
    
    def _extract_repo_path(self, url: str) -> str:
        """从URL提取owner/repo"""
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return ""
    
    def _fetch_repo_info(self, repo_path: str) -> Dict:
        """获取GitHub API项目信息"""
        api_url = f"https://api.github.com/repos/{repo_path}"
        try:
            response = self.session.get(api_url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"获取repo信息失败: {e}")
        return {}
    
    def _fetch_readme(self, repo_path: str) -> str:
        """获取README内容"""
        # 尝试获取README
        readme_urls = [
            f"https://raw.githubusercontent.com/{repo_path}/main/README.md",
            f"https://raw.githubusercontent.com/{repo_path}/master/README.md",
        ]
        
        for url in readme_urls:
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return ""
    
    def _extract_features(self, readme: str) -> List[str]:
        """从README提取功能列表"""
        features = []
        
        # 查找Features部分
        lines = readme.split('\n')
        in_features = False
        
        for i, line in enumerate(lines):
            # 检测Features标题
            if re.match(r'^#{1,3}\s*features?', line, re.I):
                in_features = True
                continue
            
            # 检测下一个标题，结束Features
            if in_features and line.startswith('#'):
                break
            
            # 提取列表项
            if in_features:
                # 匹配 - 或 * 开头的列表
                match = re.match(r'^\s*[-*]\s*(.+)', line)
                if match:
                    feature = match.group(1).strip()
                    if feature and len(feature) > 5:
                        features.append(feature[:100])  # 限制长度
                
                if len(features) >= 5:  # 最多5个
                    break
        
        return features
    
    def _extract_installation(self, readme: str) -> str:
        """提取安装命令"""
        # 查找Installation部分
        lines = readme.split('\n')
        in_install = False
        
        for i, line in enumerate(lines):
            if re.match(r'^#{1,3}\s*install', line, re.I):
                in_install = True
                continue
            
            if in_install and line.startswith('#'):
                break
            
            if in_install:
                # 查找代码块
                if '```' in line and i + 1 < len(lines):
                    code_line = lines[i + 1]
                    if any(cmd in code_line for cmd in ['pip ', 'npm ', 'yarn ', 'go get ', 'cargo ']):
                        return code_line.strip()[:200]
        
        return ""
    
    def _extract_usage(self, readme: str) -> str:
        """提取使用示例"""
        lines = readme.split('\n')
        in_usage = False
        
        for i, line in enumerate(lines):
            if re.match(r'^#{1,3}\s*usage|example|quick start', line, re.I):
                in_usage = True
                continue
            
            if in_usage and line.startswith('#'):
                break
            
            if in_usage:
                # 查找代码示例
                if '```' in line and i + 1 < len(lines):
                    code = lines[i + 1]
                    if code.strip() and not code.startswith('#'):
                        return code.strip()[:150]
        
        return ""
    
    def _detect_tech_stack(self, repo_path: str, readme: str) -> List[str]:
        """检测技术栈"""
        tech = []
        
        # 从README检测
        tech_keywords = {
            'python': ['python', 'pip', 'requirements.txt'],
            'javascript': ['javascript', 'node.js', 'npm', 'yarn'],
            'typescript': ['typescript', 'ts-node'],
            'rust': ['rust', 'cargo'],
            'go': ['golang', 'go.mod'],
            'rust': ['rust', 'cargo.toml'],
        }
        
        readme_lower = readme.lower()
        for lang, keywords in tech_keywords.items():
            if any(kw in readme_lower for kw in keywords):
                tech.append(lang)
        
        # 限制数量
        return tech[:3]

class ProductHuntScraper(BaseScraper):
    """Product Hunt产品抓取器"""
    
    def can_handle(self, url: str) -> bool:
        return 'producthunt.com' in url or 'ph.co' in url
    
    def scrape(self, url: str) -> Dict:
        """抓取Product Hunt产品信息"""
        result = {
            'name': '',
            'description': '',
            'tagline': '',
            'maker_description': '',
            'reviews': [],
            'pricing': '',
            'votes': 0,
            'url': url,
            'source': 'producthunt'
        }
        
        html = self.fetch(url)
        if not html:
            return result
        
        # 提取产品名
        result['name'] = self._extract_name(html)
        
        # 提取tagline
        result['tagline'] = self._extract_tagline(html)
        
        # 提取Maker描述
        result['maker_description'] = self._extract_maker_description(html)
        
        # 提取用户评论（前3条）
        result['reviews'] = self._extract_reviews(html, limit=3)
        
        # 提取投票数
        result['votes'] = self._extract_votes(html)
        
        # 组合完整描述
        result['description'] = result['tagline'] or result['maker_description']
        
        return result
    
    def _extract_name(self, html: str) -> str:
        """提取产品名"""
        # 从title提取
        match = re.search(r'<title>(.+?)\s*[–|]', html)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_tagline(self, html: str) -> str:
        """提取产品一句话描述"""
        # 查找meta description
        match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html, re.I)
        if match:
            return match.group(1).strip()[:200]
        return ""
    
    def _extract_maker_description(self, html: str) -> str:
        """提取Maker写的详细描述"""
        # 查找主要内容区域
        # 简化处理，提取第一个大段落
        match = re.search(r'<p[^>]*>([^<]{100,500})</p>', html)
        if match:
            text = match.group(1).strip()
            # 清理HTML实体
            text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
            return text[:300]
        return ""
    
    def _extract_reviews(self, html: str, limit: int = 3) -> List[str]:
        """提取用户评论"""
        reviews = []
        
        # 查找评论区域（简化处理）
        # Product Hunt评论通常在特定class中
        comment_pattern = r'<div[^>]*class="[^"]*comment[^"]*"[^>]*>.*?<p[^>]*>([^<]+)</p>'
        matches = re.findall(comment_pattern, html, re.DOTALL)
        
        for match in matches[:limit]:
            text = match.strip()[:200]
            if text:
                reviews.append(text)
        
        return reviews
    
    def _extract_votes(self, html: str) -> int:
        """提取投票数"""
        # 查找vote count
        match = re.search(r'(\d+)\s*upvotes?', html, re.I)
        if match:
            return int(match.group(1))
        return 0

class HackerNewsScraper(BaseScraper):
    """HackerNews讨论抓取器"""
    
    def can_handle(self, url: str) -> bool:
        return 'news.ycombinator.com' in url or 'ycombinator.com' in url
    
    def scrape(self, url: str) -> Dict:
        """抓取HN讨论信息"""
        result = {
            'name': '',
            'title': '',
            'description': '',
            'external_url': '',
            'top_comments': [],
            'comment_count': 0,
            'points': 0,
            'url': url,
            'source': 'hackernews'
        }
        
        html = self.fetch(url)
        if not html:
            return result
        
        # 提取标题
        result['title'] = self._extract_title(html)
        result['name'] = result['title'][:50]
        
        # 提取外部链接
        result['external_url'] = self._extract_external_url(html)
        
        # 提取讨论数
        result['comment_count'] = self._extract_comment_count(html)
        
        # 提取点赞数
        result['points'] = self._extract_points(html)
        
        # 提取高赞评论（前3条）
        result['top_comments'] = self._extract_top_comments(html, limit=3)
        
        # 组合描述
        if result['top_comments']:
            result['description'] = result['top_comments'][0][:200]
        else:
            result['description'] = result['title']
        
        return result
    
    def _extract_title(self, html: str) -> str:
        """提取帖子标题"""
        match = re.search(r'<title>(.+?)\s*\|', html)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_external_url(self, html: str) -> str:
        """提取讨论的外部链接"""
        # 查找titleline中的链接
        match = re.search(r'<span class="titleline">.*?<a href="([^"]+)"', html)
        if match:
            url = match.group(1)
            if not url.startswith('http'):
                url = 'https://news.ycombinator.com/' + url
            return url
        return ""
    
    def _extract_comment_count(self, html: str) -> int:
        """提取评论数"""
        match = re.search(r'(\d+)\s*comment', html, re.I)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_points(self, html: str) -> int:
        """提取点赞数"""
        match = re.search(r'(\d+)\s*points?', html, re.I)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_top_comments(self, html: str, limit: int = 3) -> List[str]:
        """提取高赞评论"""
        comments = []
        
        # HN评论在class="comment"中
        comment_pattern = r'<div class="comment">.*?<div class="commtext c00">(.*?)</div>'
        matches = re.findall(comment_pattern, html, re.DOTALL)
        
        for match in matches[:limit]:
            # 清理HTML标签
            text = re.sub(r'<[^>]+>', '', match)
            text = text.strip()[:250]
            if text and len(text) > 20:
                comments.append(text)
        
        return comments

# 工厂函数
def get_scraper(url: str) -> Optional[BaseScraper]:
    """根据URL获取合适的抓取器"""
    scrapers = [GitHubScraper(), ProductHuntScraper(), HackerNewsScraper()]
    
    for scraper in scrapers:
        if scraper.can_handle(url):
            return scraper
    
    return None

# 测试
if __name__ == '__main__':
    # 测试GitHub抓取
    github_url = "https://github.com/browser-use/browser-use"
    scraper = GitHubScraper()
    if scraper.can_handle(github_url):
        data = scraper.scrape(github_url)
        print(f"GitHub抓取结果:")
        print(f"  名称: {data['name']}")
        print(f"  描述: {data['description'][:100]}...")
        print(f"  Star: {data['stars']}")
        print(f"  功能: {data['features'][:3]}")
