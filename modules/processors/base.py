"""
信息整理模块基类
所有整理模块必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProcessor(ABC):
    """信息整理模块基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Processor', '').lower()
    
    @abstractmethod
    def process(self, candidate: Dict[str, Any]) -> str:
        """
        处理候选项目，生成内容片段
        输入：候选项目（包含url、metadata等）
        输出：内容片段字符串
        """
        pass
    
    def can_process(self, candidate: Dict[str, Any]) -> bool:
        """
        是否能处理该候选
        默认返回True，子类可覆盖
        """
        return True
