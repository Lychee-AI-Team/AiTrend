"""
数据源工厂 - 纯标准库版本
"""
from typing import Dict, List, Type, Any
from .base import DataSource, Article
from .github_trending import GitHubTrendingSource
from .brave_search import BraveSearchSource
from .reddit import RedditSource
from .hackernews import HackerNewsSource
from .producthunt import ProductHuntSource
from .twitter import TwitterSource
import logging

logger = logging.getLogger(__name__)

# 数据源注册表
SOURCE_REGISTRY: Dict[str, Type[DataSource]] = {
    "github_trending": GitHubTrendingSource,
    "brave_search": BraveSearchSource,
    "reddit": RedditSource,
    "hackernews": HackerNewsSource,
    "producthunt": ProductHuntSource,
    "twitter": TwitterSource,
}

def get_source(name: str) -> Type[DataSource]:
    """获取数据源类"""
    if name not in SOURCE_REGISTRY:
        raise ValueError(f"未知数据源: {name}。可用: {list(SOURCE_REGISTRY.keys())}")
    return SOURCE_REGISTRY[name]

def create_sources(config: Dict[str, Any]) -> List[DataSource]:
    """根据配置创建所有启用的数据源（同步版本）"""
    sources = []
    
    for name, source_config in config.items():
        if not isinstance(source_config, dict):
            continue
            
        if not source_config.get("enabled", True):
            logger.info(f"数据源 {name} 已禁用")
            continue
        
        try:
            source_class = get_source(name)
            source = source_class(source_config)
            sources.append(source)
            logger.info(f"创建数据源: {name}")
        except Exception as e:
            logger.error(f"创建数据源 {name} 失败: {e}")
            continue
    
    return sources

def register_source(name: str, source_class: Type[DataSource]):
    """注册新数据源（用于插件扩展）"""
    SOURCE_REGISTRY[name] = source_class
    logger.info(f"注册数据源: {name}")
