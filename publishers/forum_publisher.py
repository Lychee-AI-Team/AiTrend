#!/usr/bin/env python3
"""
Discord 论坛发布模块
发布内容到 Discord 论坛频道（Forum Channel）

使用方法：
1. 在 Discord 中创建一个论坛频道
2. 创建 Webhook（论坛频道的 Webhook 可以创建帖子）
3. 配置 WEBHOOK_URL
4. 设置帖子名称模板
"""

import os
import time
import requests
from typing import Dict, Any, List
from .base import BasePublisher

class ForumPublisher(BasePublisher):
    """
    Discord 论坛发布模块
    
    功能：
    - 发布到论坛频道，创建新帖子
    - 支持自定义帖子标题模板
    - 自动处理速率限制
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        self.thread_name_template = config.get('thread_name', '{name} – {source}')
        self.delay_between_posts = config.get('delay', 2)  # 帖子间隔（秒）
        self.username = config.get('username', 'AiTrend')
        self.max_content_length = config.get('max_length', 1900)  # Discord 限制
        
        self.session = requests.Session()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.webhook_url:
            print("❌ 未配置 Discord Webhook URL")
            return False
        return True
    
    def publish(self, content: Dict[str, Any]) -> bool:
        """
        发布单条内容到论坛
        
        使用 Webhook 的 thread_name 参数创建论坛帖子
        """
        if not self.validate_config():
            return False
        
        name = content.get('name', 'Unknown')
        text = content.get('content', '')
        url = content.get('url', '')
        source = content.get('source', 'AiTrend')
        
        # 构建帖子标题
        thread_name = self.thread_name_template.format(
            name=name,
            source=source,
            date=time.strftime('%m-%d')
        )
        
        # 截断内容（Discord 限制）
        if len(text) > self.max_content_length:
            text = text[:self.max_content_length - 50] + f"...\n\n{url}"
        
        # 构建 payload
        payload = {
            'username': self.username,
            'thread_name': thread_name[:100],  # Discord 标题限制 100 字符
            'content': text
        }
        
        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            print(f"  ✅ 论坛帖子创建成功: {thread_name[:50]}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # 速率限制
                retry_after = int(e.response.headers.get('Retry-After', 5))
                print(f"  ⏳ 速率限制，等待 {retry_after} 秒...")
                time.sleep(retry_after)
                return self.publish(content)  # 重试
            else:
                print(f"  ❌ HTTP 错误: {e}")
                return False
                
        except Exception as e:
            print(f"  ❌ 发布失败: {e}")
            return False
    
    def publish_batch(self, contents: List[Dict[str, Any]]) -> int:
        """批量发布到论坛"""
        
        if not self.validate_config():
            return 0
        
        print(f"\n📤 发布 {len(contents)} 条内容到 Discord 论坛...")
        
        success_count = 0
        for i, content in enumerate(contents, 1):
            print(f"  [{i}/{len(contents)}] {content.get('name', 'Unknown')[:40]}...")
            
            if self.publish(content):
                success_count += 1
            
            # 间隔，避免速率限制
            if i < len(contents):
                time.sleep(self.delay_between_posts)
        
        print(f"\n  ✅ 成功发布 {success_count}/{len(contents)} 条")
        return success_count

# 测试
if __name__ == '__main__':
    print("="*60)
    print("Discord 论坛发布模块测试")
    print("="*60)
    
    config = {
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
        'thread_name': '{name} – {source}',
        'delay': 2
    }
    
    publisher = ForumPublisher(config)
    
    if not publisher.validate_config():
        print("\n⚠️ 请先配置 DISCORD_WEBHOOK_URL 环境变量")
        exit(1)
    
    # 测试发布
    test_content = {
        'name': 'Test Project',
        'content': '这是一个测试内容，用于验证论坛发布模块是否正常工作。',
        'url': 'https://github.com/test/project',
        'source': 'GitHub'
    }
    
    print("\n发送测试内容...")
    if publisher.publish(test_content):
        print("✅ 测试成功！")
    else:
        print("❌ 测试失败")
