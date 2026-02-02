"""
输出处理器
支持多渠道输出：Console、Discord、Feishu、Telegram
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import json

class ChannelSender(ABC):
    """发送渠道基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    def send(self, content: str) -> bool:
        """发送内容，返回是否成功"""
        pass
    
    @abstractmethod
    def format_content(self, data: Dict[str, Any]) -> str:
        """格式化内容"""
        pass

class ConsoleSender(ChannelSender):
    """控制台输出"""
    
    def send(self, content: str) -> bool:
        print(content)
        return True
    
    def format_content(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)

class DiscordSender(ChannelSender):
    """Discord 发送器（通过 OpenClaw 调用）"""
    
    def send(self, content: str) -> bool:
        # Discord 渠道通过输出到 stdout 由 OpenClaw 捕获并路由
        # 格式：[DISCORD] channel_id | content
        channel_id = self.config.get('channel_id', '')
        if channel_id:
            print(f"[DISCORD:{channel_id}] {content}")
        else:
            print(content)
        return True
    
    def format_content(self, data: Dict[str, Any]) -> str:
        # Discord 支持 Markdown，返回原始内容
        return data.get('formatted_content', '')

class FeishuSender(ChannelSender):
    """飞书发送器（通过 OpenClaw 调用）"""
    
    def send(self, content: str) -> bool:
        channel_id = self.config.get('chat_id', '')
        if channel_id:
            print(f"[FEISHU:{channel_id}] {content}")
        else:
            print(content)
        return True
    
    def format_content(self, data: Dict[str, Any]) -> str:
        return data.get('formatted_content', '')

class TelegramSender(ChannelSender):
    """Telegram 发送器"""
    
    def send(self, content: str) -> bool:
        channel_id = self.config.get('chat_id', '')
        if channel_id:
            print(f"[TELEGRAM:{channel_id}] {content}")
        else:
            print(content)
        return True
    
    def format_content(self, data: Dict[str, Any]) -> str:
        return data.get('formatted_content', '')

def create_sender(channel_name: str, config: Dict[str, Any]) -> ChannelSender:
    """工厂函数：创建对应的发送器"""
    senders = {
        'console': ConsoleSender,
        'discord': DiscordSender,
        'feishu': FeishuSender,
        'telegram': TelegramSender
    }
    
    sender_class = senders.get(channel_name.lower())
    if not sender_class:
        raise ValueError(f"未知的发送渠道: {channel_name}")
    
    return sender_class(config)

def send_to_all_channels(data: Dict[str, Any], channels_config: Dict[str, Any]) -> Dict[str, bool]:
    """发送到所有启用的渠道"""
    results = {}
    
    for channel_name, config in channels_config.items():
        if not config.get('enabled', False):
            continue
        
        try:
            sender = create_sender(channel_name, config)
            formatted = sender.format_content(data)
            success = sender.send(formatted)
            results[channel_name] = success
        except Exception as e:
            print(f"发送到 {channel_name} 失败: {e}")
            results[channel_name] = False
    
    return results
