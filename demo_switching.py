#!/usr/bin/env python3
"""
发布模块切换演示
展示 ForumPublisher 和 TextPublisher 的完美切换
"""

import os
import sys
sys.path.insert(0, '.')

# 加载环境变量
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from modules.logger import get_logger
from publishers import create_publisher

logger = get_logger()

def demo_switching():
    """
    演示模块切换功能
    """
    logger.section("🔄 发布模块切换演示")
    
    # 获取 Webhook URL
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        logger.error("❌ 未配置 DISCORD_WEBHOOK_URL")
        print("\n请在 .env 文件中配置:")
        print("  DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
        return
    
    # 测试内容
    test_content = {
        'name': 'ModuleSwitchDemo',
        'content': '这是一个模块切换演示内容，用于验证 ForumPublisher 和 TextPublisher 可以无缝切换。',
        'url': 'https://github.com/demo/project',
        'source': 'Demo'
    }
    
    # ============ 切换到论坛发布模块 ============
    logger.section("切换到: ForumPublisher (Discord论坛)")
    
    forum_config = {
        'webhook_url': webhook_url,
        'thread_name': '{name} – {source}',
        'username': 'AiTrend-Forum',
        'delay': 1,
        'max_length': 1900
    }
    
    forum_publisher = create_publisher('forum', forum_config)
    
    if forum_publisher:
        logger.info("✅ ForumPublisher 创建成功")
        logger.info("即将发布到论坛频道（创建新帖子）...")
        
        # 修改内容为论坛测试
        forum_content = test_content.copy()
        forum_content['name'] = 'ForumPublisher-Test'
        forum_content['content'] = '这是 ForumPublisher 测试内容。\n\n该模块会创建论坛帖子，每个项目有独立的讨论区。'
        
        success = forum_publisher.publish(forum_content)
        
        if success:
            logger.success("ForumPublisher 测试成功")
        else:
            logger.error("ForumPublisher 测试失败")
    
    # 等待一下
    import time
    time.sleep(3)
    
    # ============ 切换到文字频道发布模块 ============
    logger.section("切换到: TextPublisher (Discord文字频道)")
    
    text_config = {
        'webhook_url': webhook_url,
        'use_embed': False,  # 纯文本格式
        'username': 'AiTrend-Text',
        'delay': 1
    }
    
    text_publisher = create_publisher('text', text_config)
    
    if text_publisher:
        logger.info("✅ TextPublisher 创建成功")
        logger.info("即将发布到文字频道（发送普通消息）...")
        
        # 修改内容为文字频道测试
        text_content = test_content.copy()
        text_content['name'] = 'TextPublisher-Test'
        text_content['content'] = '这是 TextPublisher 测试内容。\n\n该模块会发送普通消息到文字频道。'
        
        success = text_publisher.publish(text_content)
        
        if success:
            logger.success("TextPublisher 测试成功")
        else:
            logger.error("TextPublisher 测试失败")
    
    # ============ 切换到 Embed 格式 ============
    logger.section("切换到: TextPublisher with Embed")
    
    text_embed_config = {
        'webhook_url': webhook_url,
        'use_embed': True,  # Embed格式
        'username': 'AiTrend-Embed',
        'delay': 1
    }
    
    embed_publisher = create_publisher('text', text_embed_config)
    
    if embed_publisher:
        logger.info("✅ TextPublisher (Embed) 创建成功")
        logger.info("即将发布 Embed 格式消息...")
        
        embed_content = test_content.copy()
        embed_content['name'] = 'Embed-Test'
        embed_content['content'] = '这是 Embed 格式测试。\n\nEmbed 格式更美观，带有标题和页脚。'
        
        success = embed_publisher.publish(embed_content)
        
        if success:
            logger.success("Embed 格式测试成功")
        else:
            logger.error("Embed 格式测试失败")
    
    logger.section("✅ 模块切换演示完成")
    logger.info("请检查 Discord 频道查看三种发布效果")
    logger.info("  1. ForumPublisher - 论坛帖子")
    logger.info("  2. TextPublisher (纯文本) - 普通消息")
    logger.info("  3. TextPublisher (Embed) - 卡片消息")

if __name__ == '__main__':
    demo_switching()
