"""
AI 总结器
支持多模型：Gemini、OpenAI、Anthropic
"""
import os
import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class SummaryConfig(BaseModel):
    """总结器配置"""
    provider: str = Field(default="gemini", pattern=r"^(gemini|openai|anthropic)$")
    model: str = Field(default="gemini-2.5-flash")
    api_key: str = Field(default="")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    prompt_template: str = Field(default="")

class BaseSummarizer(ABC):
    """总结器基类"""
    
    def __init__(self, config: SummaryConfig):
        self.config = config
        self.default_prompt = """你是一个专业的 AI 资讯编辑。请将以下 AI 热点资讯总结成简洁的中文：

{content}

要求：
1. 将每条资讯翻译成简洁的中文
2. 每个来源提取最重要的 2-3 条
3. 保持原有链接
4. 输出格式：
   - 分类标题使用 emoji 前缀
   - 每条：序号. 标题（来源）- 一句话摘要
   - 不要 markdown，不要 HTML 标签
   - 使用换行分隔

示例：
🔥 AI 热点资讯 - {date}

🤖 中美模型厂商
1. OpenAI 发布 GPT-5（OpenAI）- 新一代大模型，推理能力显著提升
2. DeepSeek-V3 开源（GitHub）- 国产大模型，性能媲美 GPT-4

🧠 大模型热点
1. Claude 3.5 升级（Anthropic）- 代码生成能力大幅提升
"""
    
    @abstractmethod
    async def summarize(self, content: str) -> str:
        """执行总结"""
        pass
    
    def _format_content(self, articles: List[Dict[str, Any]]) -> str:
        """格式化文章内容"""
        lines = []
        for i, article in enumerate(articles, 1):
            lines.append(f"{i}. {article.get('title', '')}")
            lines.append(f"   来源: {article.get('source', '')}")
            lines.append(f"   链接: {article.get('url', '')}")
            lines.append(f"   摘要: {article.get('summary', '')}")
            lines.append("")
        return "\n".join(lines)

class GeminiSummarizer(BaseSummarizer):
    """Gemini 总结器"""
    
    async def summarize(self, articles: List[Dict[str, Any]]) -> str:
        """使用 Gemini API 总结"""
        import aiohttp
        
        content = self._format_content(articles)
        prompt = (self.config.prompt_template or self.default_prompt).format(
            content=content,
            date="今日"
        )
        
        api_key = self.config.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API Key 未配置")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": self.config.temperature,
                "maxOutputTokens": self.config.max_tokens
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                params={"key": api_key},
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Gemini API 错误: {resp.status} - {error_text}")
                
                result = await resp.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return self._clean_output(text)
    
    def _clean_output(self, text: str) -> str:
        """清理输出格式"""
        # 移除 markdown
        text = re.sub(r'\*\*|\*|__|\[|\]', '', text)
        # 移除 HTML
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

class OpenAISummarizer(BaseSummarizer):
    """OpenAI 总结器"""
    
    async def summarize(self, articles: List[Dict[str, Any]]) -> str:
        """使用 OpenAI API 总结"""
        import aiohttp
        
        content = self._format_content(articles)
        prompt = (self.config.prompt_template or self.default_prompt).format(
            content=content,
            date="今日"
        )
        
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API Key 未配置")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的 AI 资讯编辑。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"OpenAI API 错误: {resp.status}")
                
                result = await resp.json()
                text = result["choices"][0]["message"]["content"]
                return self._clean_output(text)
    
    def _clean_output(self, text: str) -> str:
        """清理输出"""
        text = re.sub(r'\*\*|\*|__|\[|\]', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

class AnthropicSummarizer(BaseSummarizer):
    """Anthropic Claude 总结器"""
    
    async def summarize(self, articles: List[Dict[str, Any]]) -> str:
        """使用 Claude API 总结"""
        import aiohttp
        
        content = self._format_content(articles)
        prompt = (self.config.prompt_template or self.default_prompt).format(
            content=content,
            date="今日"
        )
        
        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API Key 未配置")
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"Anthropic API 错误: {resp.status}")
                
                result = await resp.json()
                text = result["content"][0]["text"]
                return self._clean_output(text)
    
    def _clean_output(self, text: str) -> str:
        """清理输出"""
        text = re.sub(r'\*\*|\*|__|\[|\]', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

def create_summarizer(config: Dict[str, Any]) -> BaseSummarizer:
    """工厂函数：创建总结器"""
    summary_config = SummaryConfig(**config)
    
    summarizers = {
        "gemini": GeminiSummarizer,
        "openai": OpenAISummarizer,
        "anthropic": AnthropicSummarizer,
    }
    
    provider = summary_config.provider
    if provider not in summarizers:
        raise ValueError(f"未知的 AI 提供商: {provider}")
    
    logger.info(f"创建总结器: {provider} / {summary_config.model}")
    return summarizers[provider](summary_config)
