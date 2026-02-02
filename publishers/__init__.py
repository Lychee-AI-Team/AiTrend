"""
发布模块集合
可插拔的发布模块系统
"""

from typing import Dict, Any, Optional
from .base import BasePublisher
from .forum_publisher import ForumPublisher
from .text_publisher import TextPublisher

# 可用的发布模块映射
PUBLISHER_MAP = {
    'forum': ForumPublisher,
    'text': TextPublisher,
    'discord_forum': ForumPublisher,
    'discord_text': TextPublisher,
}

def create_publisher(publisher_type: str, config: Dict[str, Any]) -> Optional[BasePublisher]:
    """
    创建发布模块实例
    
    Args:
        publisher_type: 发布模块类型 ('forum', 'text', etc.)
        config: 配置字典
    
    Returns:
        发布模块实例，如果类型不存在则返回 None
    
    Examples:
        >>> publisher = create_publisher('forum', {'webhook_url': '...'})
        >>> publisher = create_publisher('text', {'use_embed': True})
    """
    publisher_class = PUBLISHER_MAP.get(publisher_type.lower())
    
    if not publisher_class:
        print(f"❌ 未知的发布模块类型: {publisher_type}")
        print(f"可用的类型: {', '.join(PUBLISHER_MAP.keys())}")
        return None
    
    try:
        instance = publisher_class(config)
        if instance.validate_config():
            return instance
        else:
            return None
    except Exception as e:
        print(f"❌ 创建发布模块失败: {e}")
        return None

def list_publishers() -> list:
    """列出所有可用的发布模块"""
    return list(PUBLISHER_MAP.keys())

__all__ = [
    'BasePublisher',
    'ForumPublisher',
    'TextPublisher',
    'create_publisher',
    'list_publishers',
]
