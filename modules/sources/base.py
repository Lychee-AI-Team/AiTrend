"""
信息源模块基类
所有信息源必须继承此类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSource(ABC):
    """信息源基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def discover(self) -> List[Dict[str, Any]]:
        """
        发现候选项目
        返回：候选项目列表，每个项目包含：
        - name: 项目名称
        - url: 项目URL
        - metadata: 元数据（star数、增长率等）
        """
        pass
    
    @abstractmethod
    def get_details(self, candidate: Dict) -> Dict[str, Any]:
        """
        获取项目详细信息
        输入：候选项目
        输出：详细信息字典
        """
        pass
