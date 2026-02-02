"""
GitHub Trending 数据源 - 纯标准库版本
使用 http.client + 正则表达式解析 HTML
"""
import http.client
import gzip
import re
from typing import List
from .base import DataSource, Article
import logging

logger = logging.getLogger(__name__)

class GitHubTrendingSource(DataSource):
    """GitHub Trending 数据源 - 纯标准库版本"""
    name = "github_trending"
    
    # 要跳过的路径模式
    SKIP_PATTERNS = ['/sponsors', '/trending', '/apps/', '/settings', '/search', '/_graphql', '/explore']
    
    # AI 特征关键词
    AI_KEYWORDS = [
        "ai", "artificial intelligence", "llm", "language model", "gpt", "claude",
        "openai", "anthropic", "gemini", "kimi", "deepseek", "agent", "rag",
        "embedding", "vector", "prompt", "chatbot", "copilot", "automation",
        "ml", "machine learning", "neural", "transformer", "diffusion"
    ]
    
    def fetch(self) -> List[Article]:
        """获取 GitHub Trending 数据（同步版本）"""
        languages = self.config.get("languages", ["python", "typescript", "rust"])
        
        all_articles = []
        
        for lang in languages:
            try:
                articles = self._fetch_language(lang)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"获取 {lang} 趋势失败: {e}")
                continue
        
        logger.info(f"GitHub Trending 获取 {len(all_articles)} 条")
        return self.validate(all_articles)
    
    def _fetch_language(self, language: str) -> List[Article]:
        """获取指定语言的趋势仓库（使用 http.client）"""
        conn = http.client.HTTPSConnection("github.com", timeout=15)
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br"
            }
            
            url = f"/trending/{language}"
            conn.request("GET", url, headers=headers)
            
            response = conn.getresponse()
            if response.status != 200:
                logger.warning(f"GitHub Trending 返回状态 {response.status}")
                return []
            
            # 处理 gzip 压缩
            data = response.read()
            try:
                html = gzip.decompress(data).decode('utf-8')
            except:
                html = data.decode('utf-8')
            
            return self._parse_html(html, language)
            
        finally:
            conn.close()
    
    def _should_skip(self, href: str) -> bool:
        """检查是否应该跳过该链接"""
        for pattern in self.SKIP_PATTERNS:
            if pattern in href:
                return True
        return False
    
    def _parse_html(self, html: str, language: str) -> List[Article]:
        """解析 HTML 获取仓库信息"""
        articles = []
        
        # 查找所有 h2 标签内的仓库链接
        repo_blocks = re.findall(
            r'<h2[^>]*>.*?<a[^>]*href="(/[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+)"[^>]*>.*?<span[^>]*>([^<]+)</span>\s*([^<]+)</a>\s*</h2>',
            html, 
            re.DOTALL
        )
        
        logger.info(f"找到 {len(repo_blocks)} 个潜在仓库")
        
        for href, owner, repo_name in repo_blocks:
            try:
                # 跳过非仓库链接
                if self._should_skip(href):
                    continue
                
                # 清理 owner（去除换行和多余空格）
                owner = ' '.join(owner.split()).replace('/', '').strip()
                repo_name = repo_name.strip()
                
                if not owner or not repo_name:
                    continue
                
                full_name = f"{owner}/{repo_name}"
                url = f"https://github.com{href}"
                
                # 找到该仓库在 HTML 中的位置
                pos = html.find(f'href="{href}"')
                if pos < 0:
                    continue
                
                snippet = html[pos:pos+2000]
                
                # 提取描述
                desc_match = re.search(
                    r'<p[^>]*class="[^"]*color-fg-muted[^"]*"[^>]*>([^<]+)</p>',
                    snippet
                )
                description = ""
                if desc_match:
                    description = ' '.join(desc_match.group(1).split())  # 清理空白
                
                if not description:
                    description = f"{repo_name} - {language} 热门项目"
                
                # 提取 star 数（在 stargazers 链接后的 </svg> 和 </a> 之间）
                # 格式: /stargazers...>...</svg>\n        12,737</a>
                stars_match = re.search(
                    r'/stargazers[^<]*<[^>]*>.*?</svg>\s*([\d,]+)\s*</a>',
                    snippet,
                    re.DOTALL
                )
                stars = 0
                if stars_match:
                    stars_text = stars_match.group(1).replace(',', '')
                    stars = int(stars_text)
                
                # AI 特征检测：标题或描述包含 AI 关键词
                full_text = f"{repo_name} {description}".lower()
                is_ai_related = any(kw in full_text for kw in self.AI_KEYWORDS)
                
                if is_ai_related:
                    articles.append(Article(
                        title=f"{full_name} ⭐{stars}",
                        url=url,
                        summary=description,
                        source="github_trending",
                        metadata={
                            "language": language,
                            "stars": stars
                        }
                    ))
                    
            except Exception as e:
                logger.debug(f"解析仓库失败: {e}")
                continue
        
        return articles
