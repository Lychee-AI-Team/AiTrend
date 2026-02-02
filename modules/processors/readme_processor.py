#!/usr/bin/env python3
"""
README 整理模块
从GitHub README提取关键信息
"""

import re
import requests
from typing import Dict, Any
from .base import BaseProcessor

class ReadmeProcessor(BaseProcessor):
    """
    README整理处理器
    功能：
    1. 抓取README内容
    2. 提取项目描述
    3. 提取功能列表
    4. 提取安装说明
    5. 提取使用示例
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_features = config.get('max_features', 5)
        self.max_length = config.get('max_length', 1500)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def can_process(self, candidate: Dict[str, Any]) -> bool:
        """只能处理GitHub项目"""
        url = candidate.get('url', '')
        return 'github.com' in url
    
    def process(self, candidate: Dict[str, Any]) -> str:
        """处理候选项目，生成README内容摘要"""
        
        url = candidate.get('url', '')
        name = candidate.get('name', '')
        
        # 提取repo路径
        repo_path = self._extract_repo_path(url)
        if not repo_path:
            return ""
        
        # 抓取README
        readme = self._fetch_readme(repo_path)
        if not readme:
            return ""
        
        # 提取各部分
        description = self._extract_description(readme, candidate)
        features = self._extract_features(readme)
        install = self._extract_install(readme)
        usage = self._extract_usage(readme)
        
        # 组合成自然叙述
        parts = []
        
        if description:
            parts.append(f"{name} {description}")
        
        if features:
            features_text = ", ".join(features[:self.max_features])
            parts.append(f"主要功能包括{features_text}")
        
        if install:
            parts.append(f"安装方式是{install}")
        
        if usage:
            parts.append(f"使用示例：{usage}")
        
        # 自然连接
        content = "。".join(parts)
        
        # 限制长度
        if len(content) > self.max_length:
            content = content[:self.max_length] + "..."
        
        return content
    
    def _extract_repo_path(self, url: str) -> str:
        """从URL提取owner/repo"""
        parts = url.replace('https://', '').replace('http://', '').split('/')
        if len(parts) >= 3:
            return f"{parts[1]}/{parts[2]}"
        return ""
    
    def _fetch_readme(self, repo_path: str) -> str:
        """抓取README"""
        urls = [
            f"https://raw.githubusercontent.com/{repo_path}/main/README.md",
            f"https://raw.githubusercontent.com/{repo_path}/master/README.md",
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        
        return ""
    
    def _extract_description(self, readme: str, candidate: Dict) -> str:
        """提取项目描述"""
        # 优先使用API返回的描述
        api_desc = candidate.get('description', '')
        if api_desc:
            return api_desc[:200]
        
        # 从README第一行提取
        lines = readme.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                return line[:200]
        
        return ""
    
    def _extract_features(self, readme: str) -> list:
        """提取功能列表"""
        features = []
        lines = readme.split('\n')
        in_features = False
        
        for line in lines:
            # 检测Features标题
            if re.match(r'^#{1,3}\s*feature', line, re.I):
                in_features = True
                continue
            
            # 检测下一个标题
            if in_features and line.startswith('#'):
                break
            
            # 提取列表项
            if in_features:
                match = re.match(r'^\s*[-*]\s*(.+)', line)
                if match:
                    feature = match.group(1).strip()
                    # 清理markdown链接
                    feature = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', feature)
                    if feature and len(feature) > 5:
                        features.append(feature[:80])
                
                if len(features) >= self.max_features:
                    break
        
        return features
    
    def _extract_install(self, readme: str) -> str:
        """提取安装命令"""
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
                    code = lines[i + 1].strip()
                    if any(cmd in code for cmd in ['pip ', 'npm ', 'yarn ', 'go get', 'cargo ']):
                        return code[:100]
        
        return ""
    
    def _extract_usage(self, readme: str) -> str:
        """提取使用示例"""
        lines = readme.split('\n')
        in_usage = False
        
        for i, line in enumerate(lines):
            if re.match(r'^#{1,3}\s*(usage|example|quick start)', line, re.I):
                in_usage = True
                continue
            
            if in_usage and line.startswith('#'):
                break
            
            if in_usage:
                # 查找代码示例
                if '```' in line and i + 1 < len(lines):
                    code = lines[i + 1].strip()
                    if code and not code.startswith('#') and len(code) < 150:
                        return code
        
        return ""

# 测试
if __name__ == '__main__':
    print("="*60)
    print("README整理模块测试")
    print("="*60)
    
    config = {'max_features': 3, 'max_length': 500}
    processor = ReadmeProcessor(config)
    
    # 测试项目
    test_candidate = {
        'name': 'browser-use',
        'url': 'https://github.com/browser-use/browser-use',
        'description': 'Make websites accessible for AI agents'
    }
    
    print(f"\n测试项目: {test_candidate['name']}")
    result = processor.process(test_candidate)
    
    if result:
        print(f"\n整理结果 ({len(result)} 字符):")
        print(result)
    else:
        print("\n无法获取README")
