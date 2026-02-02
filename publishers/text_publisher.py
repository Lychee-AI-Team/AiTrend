#!/usr/bin/env python3
"""
Discord 文字频道发布模块
发布内容到 Discord 文字消息频道（Text Channel）

使用方法：
1. 在 Discord 中创建一个文字频道
2. 创建 Webhook
3. 配置 WEBHOOK_URL
4. 可选：配置是否使用 Embed 格式
"""

import os
import time
import requests
from typing import Dict, Any, List
from .base import BasePublisher

class TextPublisher(BasePublisher):
    """
    Discord 文字频道发布模块
    
    功能：
    - 发布到文字频道
    - 支持纯文本或 Embed 格式
    - 支持消息分割（长内容分多条发送）
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        self.use_embed = config.get('use_embed', False)  # 是否使用 Embed 格式
        self.delay_between_posts = config.get('delay', 1)
        self.username = config.get('username', 'AiTrend')
        self.avatar_url = config.get('avatar_url', '')
        self.max_content_length = 2000  # Discord 文字限制
        
        self.session = requests.Session()
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.webhook_url:
            print("❌ 未配置 Discord Webhook URL")
            return False
        return True
    
    def publish(self, content: Dict[str, Any]) -> bool:
        """
        发布单条内容到文字频道
        """
        if not self.validate_config():
            return False
        
        name = content.get('name', 'Unknown')
        text = content.get('content', '')
        url = content.get('url', '')
        source = content.get('source', 'AiTrend')
        
        if self.use_embed:
            return self._publish_with_embed(name, text, url, source)
        else:
            return self._publish_plain_text(name, text, url, source)
    
    def _publish_plain_text(self, name: str, text: str, url: str, source: str) -> bool:
        """纯文本格式发布"""
        
        # 添加标题
        header = f"**{name}** – *{source}*\n\n"
        
        # 组合内容
        full_text = header + text
        
        # 截断（Discord 限制 2000 字符）
        if len(full_text) > self.max_content_length:
            # 保留 URL，截断内容
            if len(url) + 10 < self.max_content_length:
                truncated = full_text[:self.max_content_length - len(url) - 20]
                full_text = truncated + f"...\n\n{url}"
            else:
                full_text = full_text[:self.max_content_length - 3] + "..."
        
        payload = {
            'username': self.username,
            'content': full_text
        }
        
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url
        
        return self._send_request(payload)
    
    def _publish_with_embed(self, name: str, text: str, url: str, source: str) -> bool:
        """Embed 格式发布"""
        
        # 截断描述（Embed 描述限制 4096 字符，但建议短一些）
        description = text[:2000] if len(text) > 2000 else text
        
        embed = {
            'title': name,
            'description': description,
            'url': url,
            'footer': {
                'text': f"来源: {source} • AiTrend"
            },
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }
        
        payload = {
            'username': self.username,
            'embeds': [embed]
        }
        
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url
        
        return self._send_request(payload)
    
    def _send_request(self, payload: Dict) -> bool:
        """发送请求"""
        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            print(f"  ✅ 消息发送成功")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                print(f"  ⏳ 速率限制，等待 {retry_after} 秒...")
                time.sleep(retry_after)
                return self._send_request(payload)  # 重试
            else:
                print(f"  ❌ HTTP 错误: {e}")
                return False
                
        except Exception as e:
            print(f"  ❌ 发送失败: {e}")
            return False
    
    def publish_batch(self, contents: List[Dict[str, Any]]) -> int:
        """批量发布到文字频道"""
        
        if not self.validate_config():
            return 0
        
        print(f"\n📤 发布 {len(contents)} 条内容到 Discord 文字频道...")
        
        success_count = 0
        for i, content in enumerate(contents, 1):
            print(f"  [{i}/{len(contents)}] {content.get('name', 'Unknown')[:40]}...")
            
            if self.publish(content):
                success_count += 1
            
            if i < len(contents):
                time.sleep(self.delay_between_posts)
        
        print(f"\n  ✅ 成功发布 {success_count}/{len(contents)} 条")
        return success_count

# 测试
if __name__ == '__main__':
    print("="*60)
    print("Discord 文字频道发布模块测试")
    print("="*60)
    
    config = {
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
        'use_embed': False,  # 切换为 True 测试 Embed 格式
        'delay': 1
    }
    
    publisher = TextPublisher(config)
    
    if not publisher.validate_config():
        print("\n⚠️ 请先配置 DISCORD_WEBHOOK_URL 环境变量")
        exit(1)
    
    test_content = {
        'name': 'Test Project',
        'content': '这是一个测试内容，用于验证文字频道发布模块是否正常工作。',
        'url': 'https://github.com/test/project',
        'source': 'GitHub'
    }
    
    print("\n发送测试内容...")
    print(f"格式: {'Embed' if config['use_embed'] else '纯文本'}")
    
    if publisher.publish(test_content):
        print("✅ 测试成功！")
    else:
        print("❌ 测试失败")
