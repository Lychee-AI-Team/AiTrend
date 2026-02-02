#!/usr/bin/env python3
"""
README 整理模块（带大模型深度总结）
从GitHub README提取关键信息，并用大模型生成自然叙述
"""

import re
import requests
from typing import Dict, Any
from .base import BaseProcessor
from ..llm_client import get_llm_client

class ReadmeProcessor(BaseProcessor):
    """
    README整理处理器（LLM增强版）
    
    功能：
    1. 抓取README内容
    2. 提取关键信息
    3. 调用大模型深度总结
    4. 生成自然叙述（非结构化）
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_length = config.get('max_length', 400)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.llm = get_llm_client()
    
    def can_process(self, candidate: Dict[str, Any]) -> bool:
        """只能处理GitHub项目"""
        url = candidate.get('url', '')
        return 'github.com' in url
    
    def process(self, candidate: Dict[str, Any]) -> str:
        """处理候选项目，使用LLM生成深度总结"""
        
        url = candidate.get('url', '')
        name = candidate.get('name', '')
        description = candidate.get('description', '')
        
        # 提取repo路径
        repo_path = self._extract_repo_path(url)
        if not repo_path:
            return ""
        
        # 抓取README
        readme = self._fetch_readme(repo_path)
        if not readme:
            # 如果没有README，用API描述
            readme = description or ""
        
        # 提取结构化信息
        features = self._extract_features(readme)
        install = self._extract_install(readme)
        usage = self._extract_usage(readme)
        
        # 构建给LLM的输入
        context = self._build_context(name, description, readme, features, install, usage)
        
        # 调用大模型生成自然叙述
        summary = self.llm.summarize(context, max_length=self.max_length)
        
        if not summary:
            # LLM失败，使用简单提取
            return self._fallback_summary(name, description, features)
        
        return summary
    
    def _build_context(self, name: str, description: str, readme: str, 
                       features: list, install: str, usage: str) -> str:
        """构建给LLM的上下文"""
        
        parts = [f"项目名称: {name}"]
        
        if description:
            parts.append(f"项目描述: {description}")
        
        # README前1500字
        readme_preview = readme[:1500].strip()
        if readme_preview:
            parts.append(f"README内容:\n{readme_preview}")
        
        if features:
            parts.append(f"功能列表: {', '.join(features[:5])}")
        
        if install:
            parts.append(f"安装方式: {install}")
        
        if usage:
            parts.append(f"使用示例: {usage}")
        
        return "\n\n".join(parts)
    
    def _fallback_summary(self, name: str, description: str, features: list) -> str:
        """LLM失败时的备用总结"""
        parts = []
        
        if description:
            parts.append(f"{name} {description}")
        
        if features:
            features_text = "、".join(features[:3])
            parts.append(f"主要功能包括{features_text}")
        
        return "。".join(parts) if parts else ""
    
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
    
    def _extract_features(self, readme: str) -> list:
        """提取功能列表"""
        features = []
        lines = readme.split('\n')
        in_features = False
        
        for line in lines:
            if re.match(r'^#{1,3}\s*feature', line, re.I):
                in_features = True
                continue
            
            if in_features and line.startswith('#'):
                break
            
            if in_features:
                match = re.match(r'^\s*[-*]\s*(.+)', line)
                if match:
                    feature = match.group(1).strip()
                    feature = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', feature)
                    if feature and len(feature) > 5:
                        features.append(feature[:80])
                
                if len(features) >= 5:
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
                if '```' in line and i + 1 < len(lines):
                    code = lines[i + 1].strip()
                    if code and not code.startswith('#') and len(code) < 150:
                        return code
        
        return ""
