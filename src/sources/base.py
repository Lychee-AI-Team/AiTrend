"""
数据源基类定义 - 纯标准库版本
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class Article:
    """文章数据模型 - 使用 dataclass 替代 pydantic"""
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataSource(ABC):
    """数据源基类"""
    name: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
    
    @abstractmethod
    def fetch(self) -> List[Article]:
        """获取数据，子类必须实现（同步版本）"""
        pass
    
    def validate(self, articles: List[Article]) -> List[Article]:
        """验证数据有效性"""
        valid = []
        for article in articles:
            if article.title and article.url and len(article.title) > 5:
                valid.append(article)
        return valid
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled
