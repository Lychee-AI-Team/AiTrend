#!/usr/bin/env python3
"""
飞书通知脚本 - 视频上传完成通知
使用: python notify_feishu.py <视频URL> [视频标题]
"""

import requests
import json
import sys
import os


def send_notification(video_url, video_title="AiTrend每日AI热点"):
    """发送飞书通知"""
    
    # 从环境变量读取Webhook URL
    env_path = '/home/ubuntu/.openclaw/workspace/AiTrend/.env'
    webhook_url = ''
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('FEISHU_WEBHOOK_URL='):
                    webhook_url = line.strip().split('=', 1)[1]
                    break
    
    if not webhook_url:
        print("⚠️  未配置飞书Webhook URL，跳过通知")
        print("请在.env文件中添加: FEISHU_WEBHOOK_URL=你的Webhook地址")
        return False
    
    # 构建消息卡片
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🎬 AiTrend视频已生成"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{video_title}**\n\n[点击观看视频]({video_url})"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "观看视频"
                            },
                            "type": "primary",
                            "url": video_url
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=30)
        if response.status_code == 200:
            print("✅ 飞书通知发送成功")
            return True
        else:
            print(f"⚠️  通知发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"⚠️  通知异常: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python notify_feishu.py <视频URL> [视频标题]")
        print("示例: python notify_feishu.py https://example.com/video.mp4")
        sys.exit(1)
    
    video_url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "AiTrend每日AI热点"
    
    send_notification(video_url, title)
