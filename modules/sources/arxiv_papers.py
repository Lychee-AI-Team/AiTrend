"""
arXiv Papers 信息源模块

提供功能：
- 获取 arXiv 最新 AI/ML 论文
- 支持多个分类：cs.AI, cs.CL, cs.LG, cs.CV
- 提取论文标题、摘要、作者、链接

API: http://export.arxiv.org/api/query
无需认证
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote


class ArxivPapers:
    """arXiv 论文信息源"""
    
    # arXiv API 端点
    API_URL = "http://export.arxiv.org/api/query"
    
    # AI 相关分类
    DEFAULT_CATEGORIES = ['cs.AI', 'cs.CL', 'cs.LG', 'cs.CV']
    
    # 命名空间
    NS = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 arXiv 信息源
        
        Args:
            config: 配置字典
                - categories: 分类列表，默认 ['cs.AI', 'cs.CL', 'cs.LG', 'cs.CV']
                - days_back: 回溯天数，默认 7
                - max_results: 最大结果数，默认 20
                - min_authors: 最少作者数（用于筛选重要论文），默认 1
        """
        self.config = config or {}
        self.categories = self.config.get('categories', self.DEFAULT_CATEGORIES)
        self.days_back = self.config.get('days_back', 7)
        self.max_results = self.config.get('max_results', 20)
        self.min_authors = self.config.get('min_authors', 1)
        
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return True  # arXiv 不需要认证，始终可用
    
    def _build_query(self) -> str:
        """构建搜索查询"""
        # 构建分类查询
        cat_query = ' OR '.join([f'cat:{cat}' for cat in self.categories])
        return f"search_query={quote(cat_query)}&start=0&max_results={self.max_results}&sortBy=submittedDate&sortOrder=descending"
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        # arXiv 格式: 2024-01-15T10:30:00Z
        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        except:
            return datetime.now()
    
    def _extract_paper(self, entry: ET.Element) -> Optional[Dict[str, Any]]:
        """从 XML 条目提取论文信息"""
        try:
            # 标题
            title_elem = entry.find('atom:title', self.NS)
            if title_elem is None:
                return None
            title = title_elem.text.strip() if title_elem.text else ""
            
            # 摘要
            summary_elem = entry.find('atom:summary', self.NS)
            summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""
            
            # 作者
            authors = []
            for author in entry.findall('atom:author', self.NS):
                name_elem = author.find('atom:name', self.NS)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
            
            # 发布日期
            published_elem = entry.find('atom:published', self.NS)
            published = self._parse_date(published_elem.text) if published_elem is not None else datetime.now()
            
            # arXiv ID 和链接
            arxiv_id = ""
            pdf_url = ""
            abs_url = ""
            
            for link in entry.findall('atom:link', self.NS):
                href = link.get('href', '')
                rel = link.get('rel', '')
                link_type = link.get('type', '')
                
                if rel == 'alternate' and 'arxiv.org/abs/' in href:
                    abs_url = href
                    # 提取 ID
                    arxiv_id = href.split('/')[-1]
                elif link_type == 'application/pdf':
                    pdf_url = href
            
            # 主要分类
            primary_cat = ""
            prim_cat_elem = entry.find('arxiv:primary_category', self.NS)
            if prim_cat_elem is not None:
                primary_cat = prim_cat_elem.get('term', '')
            
            # 所有分类
            categories = []
            for cat in entry.findall('atom:category', self.NS):
                term = cat.get('term', '')
                if term:
                    categories.append(term)
            
            return {
                'title': title,
                'summary': summary,
                'authors': authors,
                'author_count': len(authors),
                'published': published,
                'published_str': published.strftime('%Y-%m-%d'),
                'arxiv_id': arxiv_id,
                'abs_url': abs_url,
                'pdf_url': pdf_url,
                'primary_category': primary_cat,
                'categories': categories,
                'source': 'arXiv'
            }
            
        except Exception as e:
            print(f"解析论文条目失败: {e}")
            return None
    
    def _is_recent(self, paper: Dict[str, Any]) -> bool:
        """检查论文是否在指定时间范围内"""
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        return paper['published'] >= cutoff_date
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现最新的 arXiv 论文
        
        Returns:
            论文列表，按发布日期排序
        """
        papers = []
        
        try:
            query = self._build_query()
            url = f"{self.API_URL}?{query}"
            
            print(f"[arXiv] 获取论文: {url[:80]}...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析 XML
            root = ET.fromstring(response.content)
            
            # 提取所有论文条目
            entries = root.findall('atom:entry', self.NS)
            print(f"[arXiv] 获取到 {len(entries)} 条论文")
            
            for entry in entries:
                paper = self._extract_paper(entry)
                if paper and self._is_recent(paper):
                    # 检查作者数要求
                    if paper['author_count'] >= self.min_authors:
                        papers.append(paper)
            
            # 按日期排序（最新的在前）
            papers.sort(key=lambda x: x['published'], reverse=True)
            
            print(f"[arXiv] 筛选后 {len(papers)} 条近期论文")
            
        except requests.exceptions.RequestException as e:
            print(f"[arXiv] 网络请求失败: {e}")
        except ET.ParseError as e:
            print(f"[arXiv] XML 解析失败: {e}")
        except Exception as e:
            print(f"[arXiv] 未知错误: {e}")
        
        return papers
    
    def discover_single(self) -> Optional[Dict[str, Any]]:
        """获取单篇最新论文"""
        papers = self.discover()
        return papers[0] if papers else None


if __name__ == "__main__":
    # 测试
    config = {
        'categories': ['cs.AI', 'cs.CL', 'cs.LG'],
        'days_back': 7,
        'max_results': 10
    }
    
    arxiv = ArxivPapers(config)
    papers = arxiv.discover()
    
    print(f"\n发现 {len(papers)} 篇论文:\n")
    for paper in papers[:5]:
        print(f"标题: {paper['title'][:80]}...")
        print(f"作者: {', '.join(paper['authors'][:3])}")
        print(f"分类: {paper['primary_category']}")
        print(f"日期: {paper['published_str']}")
        print(f"链接: {paper['abs_url']}")
        print("-" * 50)
