#!/usr/bin/env python3
"""
Discord 文字频道发布模块
发布内容到 Discord 文字消息频道（Text Channel）
"""

import os
import time
import requests
from typing import Dict, Any, List
import logging
from publishers.base import BasePublisher

logger = logging.getLogger(__name__)

class TextPublisher(BasePublisher):
    """
    Discord 文字频道发布模块
    
    功能：
    - 发布到文字频道
    - 支持纯文本或 Embed 格式
    - 与论坛发布模块保持格式一致
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        self.use_embed = config.get('use_embed', False)
        self.delay_between_posts = config.get('delay', 1)
        self.username = config.get('username', 'AiTrend')
        self.avatar_url = config.get('avatar_url', '')
        self.max_content_length = 2000  # Discord 文字限制
        
        self.session = requests.Session()
        
        logger.info(f"TextPublisher 初始化完成")
        logger.info(f"  - 使用Embed格式: {self.use_embed}")
        logger.info(f"  - 发布间隔: {self.delay_between_posts}秒")
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.webhook_url:
            logger.error("❌ 未配置 Discord Webhook URL")
            return False
        
        logger.info("✅ TextPublisher 配置验证通过")
        return True
    
    def format_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化内容
        
        与论坛发布模块保持一致的格式
        """
        name = content.get('name', 'Unknown')
        text = content.get('content', '')
        url = content.get('url', '')
        source = content.get('source', 'AiTrend')
        
        # 确保内容包含链接
        if url and url not in text:
            text = text.strip() + f"\n\n{url}"
        
        return {
            'name': name,
            'text': text,
            'url': url,
            'source': source
        }
    
    def publish(self, content: Dict[str, Any]) -> bool:
        """发布单条内容到文字频道"""
        
        if not self.validate_config():
            return False
        
        formatted = self.format_content(content)
        name = formatted['name']
        
        logger.info(f"📤 发布到文字频道: {name[:50]}...")
        
        if self.use_embed:
            return self._publish_with_embed(formatted)
        else:
            return self._publish_plain_text(formatted)
    
    def _publish_plain_text(self, formatted: Dict[str, Any]) -> bool:
        """纯文本格式发布"""
        
        name = formatted['name']
        text = formatted['text']
        source = formatted['source']
        
        # 添加标题（与论坛帖子标题格式一致）
        header = f"**{name}** – *{source}*\n\n"
        full_text = header + text
        
        # 截断
        if len(full_text) > self.max_content_length:
            full_text = full_text[:self.max_content_length - 3] + "..."
        
        payload = {
            'username': self.username,
            'content': full_text
        }
        
        if self.avatar_url:
            payload['avatar_url'] = self.avatar_url
        
        return self._send_request(payload, name)
    
    def _publish_with_embed(self, formatted: Dict[str, Any]) -> bool:
        """Embed 格式发布"""
        
        name = formatted['name']
        text = formatted['text']
        url = formatted['url']
        source = formatted['source']
        
        # 截断描述
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
        
        return self._send_request(payload, name)
    
    def _send_request(self, payload: Dict, name: str) -> bool:
        """发送请求"""
        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            logger.success(f"文字频道消息发送成功: {name[:50]}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                logger.warning(f"⏳ 速率限制，等待 {retry_after} 秒后重试...")
                time.sleep(retry_after)
                return self._send_request(payload, name)
            else:
                logger.error(f"❌ HTTP 错误: {e.response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 发送失败: {e}")
            return False
    
    def publish_batch(self, contents: List[Dict[str, Any]]) -> int:
        """批量发布到文字频道"""
        
        if not self.validate_config():
            logger.error("❌ 配置验证失败，无法批量发布")
            return 0
        
        format_type = "Embed" if self.use_embed else "纯文本"
        logger.section(f"📤 批量发布 {len(contents)} 条内容到 Discord 文字频道 ({format_type})")
        
        success_count = 0
        for i, content in enumerate(contents, 1):
            name = content.get('name', 'Unknown')
            logger.info(f"[{i}/{len(contents)}] {name[:40]}...")
            
            if self.publish(content):
                success_count += 1
            
            if i < len(contents):
                time.sleep(self.delay_between_posts)
        
        logger.section(f"✅ 批量发布完成: {success_count}/{len(contents)} 条成功")
        return success_count
