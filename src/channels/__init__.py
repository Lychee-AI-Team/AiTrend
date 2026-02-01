"""
渠道工厂
动态加载和管理发送渠道
"""
from typing import Dict, List, Type, Any
from .base import Channel
from .feishu import FeishuChannel
from .console import ConsoleChannel
import logging

logger = logging.getLogger(__name__)

# 渠道注册表
CHANNEL_REGISTRY: Dict[str, Type[Channel]] = {
    "feishu": FeishuChannel,
    "console": ConsoleChannel,
}

def get_channel(name: str) -> Type[Channel]:
    """获取渠道类"""
    if name not in CHANNEL_REGISTRY:
        raise ValueError(f"未知渠道: {name}。可用: {list(CHANNEL_REGISTRY.keys())}")
    return CHANNEL_REGISTRY[name]

async def create_channels(config: Dict[str, Any]) -> List[Channel]:
    """根据配置创建所有启用的渠道"""
    channels = []
    
    for name, channel_config in config.items():
        if not isinstance(channel_config, dict):
            continue
            
        if not channel_config.get("enabled", False):
            logger.info(f"渠道 {name} 未启用")
            continue
        
        try:
            channel_class = get_channel(name)
            channel = channel_class(channel_config)
            
            # 验证配置
            is_valid = await channel.validate_config()
            if not is_valid:
                logger.error(f"渠道 {name} 配置验证失败")
                continue
            
            channels.append(channel)
            logger.info(f"创建渠道: {name}")
        except Exception as e:
            logger.error(f"创建渠道 {name} 失败: {e}")
            continue
    
    return channels

def register_channel(name: str, channel_class: Type[Channel]):
    """注册新渠道（用于插件扩展）"""
    CHANNEL_REGISTRY[name] = channel_class
    logger.info(f"注册渠道: {name}")
