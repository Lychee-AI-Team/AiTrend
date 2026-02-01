"""
发送渠道基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Channel(ABC):
    """发送渠道基类"""
    name: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
    
    @abstractmethod
    async def send(self, content: str) -> bool:
        """发送消息，子类必须实现"""
        pass
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled
    
    async def validate_config(self) -> bool:
        """验证配置"""
        return True
