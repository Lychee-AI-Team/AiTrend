"""
输出处理器
支持多渠道输出：Console、Discord、DiscordForum、Feishu、Telegram
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

class DiscordForumSender(ChannelSender):
    """Discord 论坛发送器 - 创建新帖子"""
    
    def send(self, content: str) -> bool:
        """
        论坛频道输出格式：
        [DISCORD_FORUM:channel_id] title | content
        """
        channel_id = self.config.get('channel_id', '')
        if not channel_id:
            print(content)
            return True
        
        # 提取标题（第一行）和内容（剩余部分）
        lines = content.split('\n')
        title = lines[0].strip() if lines else "AI 热点"
        body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else content
        
        # 论坛格式：频道ID | 标题 | 内容
        print(f"[DISCORD_FORUM:{channel_id}] {title} | {body}")
        return True
    
    def format_content(self, data: Dict[str, Any]) -> str:
        """论坛帖子格式：标题 + 内容"""
        articles = data.get('data', {}).get('articles', [])
        language = data.get('language', 'zh')
        
        # 生成标题
        titles = {
            'zh': f"🔥 AI 热点 {self._get_date()}",
            'en': f"🔥 AI Hotspots {self._get_date()}",
            'ja': f"🔥 AI ホットニュース {self._get_date()}",
            'ko': f"🔥 AI 핫이슈 {self._get_date()}",
            'es': f"🔥 Tendencias AI {self._get_date()}"
        }
        title = titles.get(language, titles['zh'])
        
        # 生成内容
        lines = [title, "═══════════════════\n"]
        
        for i, article in enumerate(articles[:10], 1):
            lines.append(f"{i}. **{article.get('title', 'N/A')}**")
            summary = article.get('summary', '')[:300]
            lines.append(f"   {summary}...")
            lines.append(f"   🔗 {article.get('url', '')}")
            lines.append(f"   📌 {article.get('source', '')}\n")
        
        lines.append("━━━━━━━━━━━━━━━")
        lines.append("🤖 Powered by AiTrend")
        
        return '\n'.join(lines)
    
    def _get_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%m-%d")

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
        'discord_forum': DiscordForumSender,
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
