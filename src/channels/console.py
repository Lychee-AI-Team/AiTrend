"""
控制台发送渠道
用于本地测试，直接输出到控制台
"""
from typing import Dict, Any
from .base import Channel
import logging

logger = logging.getLogger(__name__)

class ConsoleChannel(Channel):
    """控制台渠道（测试用）"""
    name = "console"
    
    async def send(self, content: str) -> bool:
        """输出到控制台"""
        print("\n" + "="*50)
        print("📤 消息内容:")
        print("="*50)
        print(content)
        print("="*50 + "\n")
        
        logger.info("✅ Console 输出成功")
        return True
