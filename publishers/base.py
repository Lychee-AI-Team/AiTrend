"""
发布模块基类
所有发布模块必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePublisher(ABC):
    """发布模块基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Publisher', '').lower()
    
    @abstractmethod
    def publish(self, content: Dict[str, Any]) -> bool:
        """
        发布单条内容
        
        Args:
            content: 内容字典，包含:
                - name: 项目名称
                - content: 内容文本
                - url: 项目链接
                - source: 来源
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    def publish_batch(self, contents: List[Dict[str, Any]]) -> int:
        """
        批量发布内容
        
        Args:
            contents: 内容列表
        
        Returns:
            成功发布的数量
        """
        pass
    
    def validate_config(self) -> bool:
        """
        验证配置是否完整
        默认返回True，子类可覆盖
        """
        return True
