"""
日志模块
统一日志管理，支持文件和控制台输出
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

class Logger:
    """日志管理器"""
    
    def __init__(self, name: str = "aitrend", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加handler
        if self.logger.handlers:
            return
        
        # 日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件日志（按天分割）
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 控制台日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 添加handler
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self.logger.error(msg)
    
    def success(self, msg: str):
        """成功日志（自定义级别）"""
        self.logger.info(f"✅ {msg}")
    
    def section(self, title: str):
        """分段标题"""
        self.logger.info("=" * 60)
        self.logger.info(title)
        self.logger.info("=" * 60)

# 单例
_logger = None

def get_logger(name: str = "aitrend") -> Logger:
    """获取日志管理器"""
    global _logger
    if _logger is None:
        _logger = Logger(name)
    return _logger
