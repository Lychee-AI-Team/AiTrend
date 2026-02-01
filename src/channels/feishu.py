"""
飞书发送渠道
"""
import aiohttp
from typing import Dict, Any
from .base import Channel
import logging

logger = logging.getLogger(__name__)

class FeishuChannel(Channel):
    """飞书渠道"""
    name = "feishu"
    
    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    MESSAGE_URL = "https://open.feishu.cn/open-apis/im/v1/messages"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.app_id = config.get("app_id") or config.get("appId")
        self.app_secret = config.get("app_secret") or config.get("appSecret")
        self.target = config.get("target")  # chat_id 或 user_id
    
    async def validate_config(self) -> bool:
        """验证配置完整性"""
        if not self.app_id:
            logger.error("Feishu: 缺少 app_id")
            return False
        if not self.app_secret:
            logger.error("Feishu: 缺少 app_secret")
            return False
        if not self.target:
            logger.error("Feishu: 缺少 target (chat_id)")
            return False
        return True
    
    async def send(self, content: str) -> bool:
        """发送消息到飞书"""
        if not await self.validate_config():
            return False
        
        try:
            # 获取 token
            token = await self._get_token()
            if not token:
                return False
            
            # 发送消息
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # 构造消息内容
                content_json = {"text": content}
                
                data = {
                    "receive_id": self.target,
                    "msg_type": "text",
                    "content": content_json
                }
                
                async with session.post(
                    f"{self.MESSAGE_URL}?receive_id_type=chat_id",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    result = await resp.json()
                    
                    if result.get("code") == 0:
                        logger.info("✅ Feishu 发送成功")
                        return True
                    else:
                        logger.error(f"❌ Feishu 发送失败: {result.get('msg')}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Feishu 发送异常: {e}")
            return False
    
    async def _get_token(self) -> str:
        """获取飞书 tenant_access_token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.TOKEN_URL,
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                result = await resp.json()
                
                if result.get("code") == 0:
                    return result["tenant_access_token"]
                else:
                    logger.error(f"获取 Feishu token 失败: {result.get('msg')}")
                    return ""
