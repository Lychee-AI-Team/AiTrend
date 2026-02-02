#!/usr/bin/env python3
"""
Discord 论坛发布模块
发布内容到 Discord 论坛频道（Forum Channel）
"""

import os
import time
import requests
from typing import Dict, Any, List
from modules.logger import get_logger
from publishers.base import BasePublisher

logger = get_logger()

class ForumPublisher(BasePublisher):
    """
    Discord 论坛发布模块
    
    功能：
    - 发布到论坛频道，创建新帖子
    - 支持自定义帖子标题模板
    - 自动处理速率限制
    - 日志记录完整状态
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get('webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        self.thread_name_template = config.get('thread_name', '{name} – {source}')
        self.delay_between_posts = config.get('delay', 2)
        self.username = config.get('username', 'AiTrend')
        self.max_content_length = config.get('max_length', 1900)
        
        self.session = requests.Session()
        
        logger.info(f"ForumPublisher 初始化完成")
        logger.info(f"  - 帖子标题模板: {self.thread_name_template}")
        logger.info(f"  - 发布间隔: {self.delay_between_posts}秒")
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not self.webhook_url:
            logger.error("❌ 未配置 Discord Webhook URL")
            return False
        
        # 验证Webhook格式
        if not self.webhook_url.startswith('https://discord.com/api/webhooks/'):
            if not self.webhook_url.startswith('https://discordapp.com/api/webhooks/'):
                logger.warning("⚠️ Webhook URL 格式可能不正确")
        
        logger.info("✅ ForumPublisher 配置验证通过")
        return True
    
    def format_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化内容
        
        确保格式与文字频道一致
        """
        name = content.get('name', 'Unknown')
        text = content.get('content', '')
        url = content.get('url', '')
        source = content.get('source', 'AiTrend')
        
        # 构建帖子标题（安全格式化）
        try:
            thread_name = self.thread_name_template.format(
                name=name,
                source=source,
                date=time.strftime('%m-%d')
            )
        except (KeyError, ValueError):
            # 如果模板格式不匹配，使用默认格式
            thread_name = f"{name} – {source}"
        
        # 确保内容包含链接
        if url and url not in text:
            text = text.strip() + f"\n\n{url}"
        
        # 截断内容
        if len(text) > self.max_content_length:
            text = text[:self.max_content_length - 50].rsplit('\n', 1)[0]
            text += f"\n\n...\n\n{url}"
        
        return {
            'thread_name': thread_name[:100],
            'content': text,
            'username': self.username
        }
    
    def publish(self, content: Dict[str, Any]) -> bool:
        """
        发布单条内容到论坛
        """
        if not self.validate_config():
            return False
        
        # 格式化内容
        formatted = self.format_content(content)
        thread_name = formatted['thread_name']
        text = formatted['content']
        
        logger.info(f"📤 发布到论坛: {thread_name[:50]}...")
        
        # 构建 payload
        payload = {
            'username': self.username,
            'thread_name': thread_name,
            'content': text
        }
        
        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            logger.success(f"论坛帖子创建成功: {thread_name[:50]}")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get('Retry-After', 5))
                logger.warning(f"⏳ 速率限制，等待 {retry_after} 秒后重试...")
                time.sleep(retry_after)
                return self.publish(content)  # 重试
            else:
                logger.error(f"❌ HTTP 错误: {e.response.status_code} - {e.response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 发布失败: {e}")
            return False
    
    def publish_batch(self, contents: List[Dict[str, Any]]) -> int:
        """批量发布到论坛"""
        
        if not self.validate_config():
            logger.error("❌ 配置验证失败，无法批量发布")
            return 0
        
        logger.section(f"📤 批量发布 {len(contents)} 条内容到 Discord 论坛")
        
        success_count = 0
        for i, content in enumerate(contents, 1):
            name = content.get('name', 'Unknown')
            logger.info(f"[{i}/{len(contents)}] {name[:40]}...")
            
            if self.publish(content):
                success_count += 1
            
            # 间隔，避免速率限制
            if i < len(contents):
                time.sleep(self.delay_between_posts)
        
        logger.section(f"✅ 批量发布完成: {success_count}/{len(contents)} 条成功")
        return success_count
