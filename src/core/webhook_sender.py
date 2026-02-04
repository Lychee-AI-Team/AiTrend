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
        # Discord thread_name 限制100字符
        truncated_title = title[:97] + "..." if len(title) > 100 else title
        
        payload = {
            "thread_name": truncated_title,
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
            if response.status_code not in [200, 204]:
                print(f"   ⚠️ Webhook 返回错误: HTTP {response.status_code} - {response.text[:200]}")
            return response.status_code in [200, 204]
        except requests.exceptions.Timeout:
            print(f"   ⚠️ Webhook 请求超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Webhook 请求失败: {e}")
            return False
        except Exception as e:
            print(f"   ⚠️ Webhook 发送失败: {e}")
            return False
