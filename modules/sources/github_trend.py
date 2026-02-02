#!/usr/bin/env python3
"""
GitHub Trend 信息源模块
挖掘Star增长速率高的项目
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import BaseSource

class GithubTrend(BaseSource):
    """
    GitHub Trend 挖掘器
    标准：增长速率而非绝对数量
    计算：今日时长 / star数量 = 增长速率
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.languages = config.get('languages', ['python', 'javascript', 'go'])
        self.max_candidates = config.get('max_candidates', 10)
        self.growth_threshold = config.get('growth_threshold', 0.1)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        })
    
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现候选项目
        返回增长速率最高的项目
        """
        print(f"  目标语言: {', '.join(self.languages)}")
        print(f"  增长率阈值: {self.growth_threshold} stars/天")
        
        all_candidates = []
        
        # 对每个语言获取trending
        for language in self.languages:
            try:
                candidates = self._fetch_trending(language)
                all_candidates.extend(candidates)
                print(f"  {language}: 获取 {len(candidates)} 个")
            except Exception as e:
                print(f"  {language}: 获取失败 - {e}")
        
        # 计算增长率并排序
        for candidate in all_candidates:
            candidate['growth_rate'] = self._calculate_growth_rate(candidate)
        
        # 按增长率排序，取Top N
        sorted_candidates = sorted(
            all_candidates,
            key=lambda x: x.get('growth_rate', 0),
            reverse=True
        )
        
        # 过滤低于阈值的
        filtered = [
            c for c in sorted_candidates[:self.max_candidates]
            if c.get('growth_rate', 0) >= self.growth_threshold
        ]
        
        print(f"  总计: {len(filtered)} 个候选 (增长率≥{self.growth_threshold})")
        
        return filtered
    
    def _fetch_trending(self, language: str) -> List[Dict]:
        """获取指定语言的trending项目"""
        
        # GitHub API - 搜索最近创建的热门仓库
        # 策略：搜索最近一周创建的，按star排序
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        query = f"language:{language} created:>{one_week_ago}"
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20  # 获取多一些，后续筛选
        }
        
        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        items = data.get('items', [])
        
        candidates = []
        for item in items:
            candidate = {
                'name': item.get('name', ''),
                'full_name': item.get('full_name', ''),
                'url': item.get('html_url', ''),
                'description': item.get('description', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'language': item.get('language', ''),
                'created_at': item.get('created_at', ''),
                'updated_at': item.get('updated_at', ''),
                'owner': item.get('owner', {}).get('login', ''),
                'source_type': 'github_trend'
            }
            candidates.append(candidate)
        
        return candidates
    
    def _calculate_growth_rate(self, candidate: Dict) -> float:
        """
        计算增长率
        增长率 = star数量 / 项目存在天数
        越高表示增长越快
        """
        stars = candidate.get('stars', 0)
        created_at = candidate.get('created_at', '')
        
        if not created_at or stars == 0:
            return 0.0
        
        try:
            # 解析创建时间
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now(created.tzinfo)
            
            # 计算存在天数（至少1天避免除0）
            days = max(1, (now - created).days)
            
            # 增长率 = stars / days
            growth_rate = stars / days
            
            return round(growth_rate, 2)
            
        except Exception as e:
            print(f"    计算增长率失败: {e}")
            return 0.0
    
    def get_details(self, candidate: Dict) -> Dict[str, Any]:
        """获取项目详细信息"""
        full_name = candidate.get('full_name', '')
        
        if not full_name:
            return candidate
        
        try:
            # 获取详细repo信息
            url = f"https://api.github.com/repos/{full_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                candidate.update({
                    'topics': data.get('topics', []),
                    'has_wiki': data.get('has_wiki', False),
                    'open_issues': data.get('open_issues_count', 0),
                    'license': data.get('license', {}).get('name', '') if data.get('license') else ''
                })
            
            # 获取README
            readme = self._fetch_readme(full_name)
            if readme:
                candidate['readme'] = readme[:2000]  # 限制长度
            
        except Exception as e:
            print(f"  获取详情失败: {e}")
        
        return candidate
    
    def _fetch_readme(self, full_name: str) -> str:
        """获取README内容"""
        urls = [
            f"https://raw.githubusercontent.com/{full_name}/main/README.md",
            f"https://raw.githubusercontent.com/{full_name}/master/README.md",
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        
        return ""

# 测试
if __name__ == '__main__':
    print("="*60)
    print("GitHub Trend 挖掘器测试")
    print("="*60)
    
    config = {
        'languages': ['python'],
        'max_candidates': 3,
        'growth_threshold': 5.0
    }
    
    source = GithubTrend(config)
    candidates = source.discover()
    
    print(f"\n发现 {len(candidates)} 个候选项目:")
    for i, c in enumerate(candidates, 1):
        print(f"\n{i}. {c['full_name']}")
        print(f"   描述: {c['description'][:60] if c['description'] else 'N/A'}...")
        print(f"   Stars: {c['stars']}")
        print(f"   增长率: {c['growth_rate']} stars/天")
        print(f"   创建时间: {c['created_at'][:10]}")
