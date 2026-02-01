"""
核心收集器 - 纯标准库版本（同步）
整合数据源、AI总结、自验证、多渠道发送
"""
import json
import http.client
from typing import List, Dict, Any, Tuple
from datetime import datetime

from src.sources import create_sources
from src.core.validator import SelfValidator
from src.sources.base import Article

import logging

logger = logging.getLogger(__name__)

class TrendCollector:
    """趋势收集器 - 纯标准库版本"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = SelfValidator(
            auto_fix=config.get("advanced", {}).get("validation", {}).get("auto_fix", True)
        )
        self.max_retries = config.get("advanced", {}).get("max_retries", 3)
    
    def run(self) -> Tuple[bool, str]:
        """执行完整收集流程（同步版本）"""
        logger.info("🚀 开始 AiTrend 收集任务")
        
        for attempt in range(self.max_retries):
            try:
                # 1. 收集数据
                articles = self._collect_data()
                if not articles:
                    logger.warning("⚠️ 未收集到任何数据")
                    if attempt < self.max_retries - 1:
                        continue
                    return False, "未收集到数据"
                
                # 2. AI 总结
                summary = self._summarize(articles)
                
                # 3. 自验证
                is_valid, validation_result = self.validator.full_validate(
                    [self._article_to_dict(a) for a in articles],
                    summary,
                    "feishu"
                )
                
                final_content = validation_result.get("fixed_content", summary)
                
                # 4. 发送
                send_results = self._send_to_all_channels(final_content)
                
                # 5. 返回结果
                success_count = sum(1 for r in send_results if r[1])
                total_count = len(send_results)
                
                if success_count > 0:
                    msg = f"✅ 任务完成: 收集 {len(articles)} 条，成功发送 {success_count}/{total_count} 渠道"
                    logger.info(msg)
                    return True, final_content
                else:
                    raise RuntimeError("所有渠道发送失败")
                    
            except Exception as e:
                logger.error(f"❌ 第 {attempt + 1} 次尝试失败: {e}")
                if attempt == self.max_retries - 1:
                    return False, f"任务失败: {e}"
                import time
                time.sleep(2 ** attempt)
        
        return False, "未知错误"
    
    def _article_to_dict(self, article: Article) -> Dict:
        """Article 转 dict"""
        return {
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source
        }
    
    def _collect_data(self) -> List[Article]:
        """从所有数据源收集数据（同步）"""
        sources_config = self.config.get("sources", {})
        sources = create_sources(sources_config)
        
        if not sources:
            logger.error("没有启用的数据源")
            return []
        
        logger.info(f"📊 开始从 {len(sources)} 个数据源收集")
        
        all_articles = []
        for source in sources:
            if source.is_enabled():
                try:
                    articles = source.fetch()
                    all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"数据源 {source.name} 错误: {e}")
        
        logger.info(f"📊 共收集 {len(all_articles)} 条原始数据")
        return all_articles
    
    def _summarize(self, articles: List[Article]) -> str:
        """AI 总结（使用 http.client）"""
        summarizer_config = self.config.get("summarizer", {})
        
        if not summarizer_config.get("enabled", True):
            logger.info("⚠️ AI 总结已禁用，使用原始数据")
            return self._format_raw(articles)
        
        try:
            provider = summarizer_config.get("provider", "gemini")
            if provider == "gemini":
                return self._summarize_with_gemini(articles, summarizer_config)
            else:
                logger.warning(f"暂不支持的提供商: {provider}")
                return self._format_raw(articles)
        except Exception as e:
            logger.error(f"❌ AI 总结失败: {e}，使用原始数据")
            return self._format_raw(articles)
    
    def _summarize_with_gemini(self, articles: List[Article], config: Dict) -> str:
        """使用 Gemini API 总结"""
        api_key = config.get("api_key")
        logger.info(f"DEBUG: Gemini API Key = {api_key[:10]}..." if api_key else "None")
        if not api_key:
            raise ValueError("Gemini API Key 未配置")
        
        # 获取语言设置
        language = self.config.get("language", "zh")
        lang_names = {
            "zh": "简体中文",
            "en": "English",
            "ja": "日本語",
            "ko": "한국어",
            "es": "Español"
        }
        output_lang = lang_names.get(language, "简体中文")
        
        content = self._format_for_summary(articles)
        prompt = f"""你是 AI 圈 KOL。基于以下数据输出本周最值得推荐的 AI 产品。

【输出语言要求】
必须使用 {output_lang} 输出所有内容。

【数据】
{content}

【筛选要求】
1. 删除官方新闻（公司发布、行业报道、融资新闻）
2. 删除纯模型参数对比（超越GPT等新闻）
3. 优先保留：用户真实体验、独立开发者项目、可立即使用的工具
4. 只输出用户今天能开始用的产品

【输出格式】
1. **产品名**
@用户名 发现了这个工具...
[2-3段口语化描述，使用{output_lang}]
👉 链接

趋势洞察
[1-2段连贯口语，使用{output_lang}]

---
数据时间：{datetime.now().strftime('%Y-%m-%d')}"""
        
        conn = http.client.HTTPSConnection("generativelanguage.googleapis.com", timeout=60)
        try:
            model = config.get("model", "gemini-2.5-flash")
            path = f"/v1beta/models/{model}:generateContent"
            
            data = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": config.get("temperature", 0.7),
                    "maxOutputTokens": config.get("max_tokens", 2000)
                }
            }, ensure_ascii=False)
            
            headers = {
                "Content-Type": "application/json"
            }
            
            conn.request("POST", f"{path}?key={api_key}", body=data.encode('utf-8'), headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                error_body = response.read().decode()
                raise RuntimeError(f"Gemini API 错误: {response.status} - {error_body}")
            
            result = json.loads(response.read().decode())
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # 清理格式
            text = text.replace('**', '').replace('*', '').replace('__', '')
            text = text.replace('<', '').replace('>', '')
            
            # 删除标题行
            import re
            text = re.sub(r'^[🔥\s]*AI[\s]*圈[\s]*本周[\s]*热点[\s，,、]*\n?', '', text, flags=re.MULTILINE)
            text = re.sub(r'^[\s]*直接[\s]*上[\s]*干货[\s！!]*\n?', '', text, flags=re.MULTILINE)
            text = text.strip()
            
            logger.info("✅ AI 总结完成")
            return text
            
        finally:
            conn.close()
    
    def _format_for_summary(self, articles: List[Article]) -> str:
        """格式化为总结输入 - 精选多源热点"""
        # 按来源分类
        by_source = {}
        for a in articles:
            source = a.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(a)
        
        # 每个来源取前几条
        selected = []
        
        # 优先取用户生成内容平台（过滤官方新闻）
        priority_order = ['twitter', 'reddit', 'producthunt', 'hackernews', 'github_trending', 'brave_search']
        for source in priority_order:
            if source in by_source:
                # 过滤掉官方新闻
                if source == 'brave_search':
                    posts = [p for p in by_source[source] if not p.metadata.get("is_official_news", False)][:5]
                else:
                    posts = by_source[source][:5]
                selected.extend(posts)
        
        lines = []
        for i, article in enumerate(selected[:20], 1):  # 总共最多20条
            source_tag = f"[{article.source.upper()}]"
            
            # 检测内容类型标记
            content_type = ""
            if article.source == "brave_search" and article.metadata.get("is_official_news"):
                content_type = "[官方新闻-低权重]"
            elif article.source in ["twitter", "reddit"]:
                content_type = "[用户分享]"
            elif article.source == "producthunt":
                content_type = "[产品发布]"
            elif article.source == "hackernews":
                content_type = "[开发者分享]"
            
            lines.append(f"{i}. {source_tag} {content_type} {article.title}")
            lines.append(f"   描述: {article.summary[:150]}")
            lines.append(f"   链接: {article.url}")
            lines.append("")
        return "\n".join(lines)
    
    def _format_raw(self, articles: List[Article]) -> str:
        """格式化原始数据（备用）"""
        lines = ["🔥 AI 热点资讯", ""]
        
        for i, article in enumerate(articles[:10], 1):
            lines.append(f"{i}. {article.title}")
            lines.append(f"   来源: {article.source}")
            lines.append(f"   链接: {article.url}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _send_to_all_channels(self, content: str) -> List[Tuple[str, bool]]:
        """发送到所有启用的渠道"""
        channels_config = self.config.get("channels", {})
        results = []
        
        for name, channel_config in channels_config.items():
            if not isinstance(channel_config, dict):
                continue
            if not channel_config.get("enabled", False):
                continue
            
            try:
                if name == "console":
                    success = self._send_console(content)
                elif name == "feishu":
                    success = self._send_feishu(content, channel_config)
                else:
                    success = False
                
                results.append((name, success))
            except Exception as e:
                logger.error(f"渠道 {name} 发送失败: {e}")
                results.append((name, False))
        
        return results
    
    def _send_console(self, content: str) -> bool:
        """发送到控制台"""
        print("\n" + "="*50)
        print("📤 消息内容:")
        print("="*50)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("="*50 + "\n")
        
        # 保存完整内容到文件
        import os
        output_file = "/tmp/aitrend_full_content.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 完整内容已保存到: {output_file}")
        
        return True
    
    def _send_feishu(self, content: str, config: Dict) -> bool:
        """发送到飞书"""
        app_id = config.get("app_id")
        app_secret = config.get("app_secret")
        target = config.get("target")
        
        if not all([app_id, app_secret, target]):
            logger.error("飞书配置不完整")
            return False
        
        try:
            # 获取 token
            token = self._get_feishu_token(app_id, app_secret)
            if not token:
                return False
            
            # 发送消息
            conn = http.client.HTTPSConnection("open.feishu.cn", timeout=30)
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                data = json.dumps({
                    "receive_id": target,
                    "msg_type": "text",
                    "content": json.dumps({"text": content}, ensure_ascii=False)
                })
                
                conn.request("POST", "/open-apis/im/v1/messages?receive_id_type=chat_id", 
                           body=data, headers=headers)
                response = conn.getresponse()
                result = json.loads(response.read().decode())
                
                if result.get("code") == 0:
                    logger.info("✅ Feishu 发送成功")
                    return True
                else:
                    logger.error(f"❌ Feishu 发送失败: {result.get('msg')}")
                    return False
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"❌ Feishu 发送异常: {e}")
            return False
    
    def _get_feishu_token(self, app_id: str, app_secret: str) -> str:
        """获取飞书 token"""
        conn = http.client.HTTPSConnection("open.feishu.cn", timeout=10)
        try:
            data = json.dumps({
                "app_id": app_id,
                "app_secret": app_secret
            })
            
            headers = {"Content-Type": "application/json"}
            conn.request("POST", "/open-apis/auth/v3/tenant_access_token/internal",
                       body=data, headers=headers)
            
            response = conn.getresponse()
            result = json.loads(response.read().decode())
            
            if result.get("code") == 0:
                return result["tenant_access_token"]
            else:
                logger.error(f"获取 Feishu token 失败: {result.get('msg')}")
                return ""
        finally:
            conn.close()
