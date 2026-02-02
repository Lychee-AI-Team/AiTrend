"""
Discord Webhook 发送器
支持论坛频道创建帖子
"""
import requests
import os
from typing import Optional, List

class DiscordWebhookSender:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_to_forum(self, title: str, content: str, tags: Optional[List[str]] = None) -> bool:
        """
        发送消息到论坛频道（自动创建帖子）
        
        Args:
            title: 帖子标题
            content: 帖子内容（支持 Markdown）
            tags: 标签 ID 列表（可选）
        
        Returns:
            是否发送成功
        """
        payload = {
            "thread_name": title,
            "content": content,
            "username": "AiTrend",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2103/2103633.png"
        }
        
        if tags:
            payload["applied_tags"] = tags
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Webhook 发送失败: {e}")
            return False
