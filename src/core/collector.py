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
        
        content = self._format_for_summary(articles)
        prompt = f"""你是一位 AI 圈 KOL，拥有百万粉丝。你的任务是从全网各处挖掘**普通人马上就能用上**的 AI 新东西。

【核心要求】
1. **实用主义**：粉丝关心的是"这对我有什么用"，不是技术细节
2. **生活化场景**：结合工作、学习、生活的具体场景说明价值
3. **立即可用**：优先推荐现在就能体验、免费或低成本使用的工具
4. **降低门槛**：像朋友聊天，不要用行业黑话，多用"你"

【原始数据】
{content}

【创作要求】
1. **筛选标准**：
   - 刚发布或刚更新的 AI 产品/功能
   - 普通人能直接用的（有网站/APP，不用写代码）
   - 免费或低成本
   - 解决真实痛点

2. **内容组织**：
   - 按类型分类：新模型、新工具、新功能
   - **关键要求：用口语化连贯的叙述描述项目，不要分点列出！**
   - 像跟朋友聊天一样自然流畅，说说这个工具是什么、为什么值得试、怎么用
   - 融入具体场景和例子，有个人观点和评价
   - 不要暴露"我们用什么方法挖掘的"

3. **语言风格**：
   - 像发现好东西跟朋友分享
   - 连贯的段落，不是列表
   - 有情感、有观点、有场景

【输出格式】
🔥 AI 圈本周热点 | 值得体验的新工具

【导语】
（2-3句话，这周 AI 圈有什么普通人能用的好东西，口语化自然引入）

【本周精选】

### 🤖 新模型（体验升级）

**1. 模型名称**
（用2-3段连贯的文字描述：这是什么+为什么值得关注+怎么用+适合什么人。像聊天一样自然，不要分点！可以加入个人感受和使用场景）
👉 **链接**：https://xxx

### 🛠️ 新工具（效率神器）

**1. 工具名称**
（同上，连贯叙述，口语化描述）
👉 **链接**：https://xxx

### 💡 新功能（产品更新）

**1. 产品名称 - 功能名**
（同上，连贯叙述）
👉 **链接**：https://xxx

【趋势洞察】
（1-2段话，这周 AI 圈有什么值得关注的新趋势，口语化总结）

---
数据时间：{datetime.now().strftime('%Y-%m-%d')}

【重要提醒】
❌ 不要写成：
- 一句话说清：XXX
- 对你有什么用：XXX  
- 怎么用：XXX

✅ 要写成：
"这周我发现了一个超酷的XXX，它其实就是...想象一下，你在工作的时候经常遇到XXX问题，以前你得..., 现在用这个工具，只要...我试用了一下，感觉特别适合XXX的人，而且最重要的是它完全免费！
👉 **链接**：https://xxx"
"""
        
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
        
        # 优先取新兴平台的（更可能有新内容）
        priority_order = ['twitter', 'reddit', 'producthunt', 'hackernews', 'brave_search', 'github_trending']
        for source in priority_order:
            if source in by_source:
                posts = by_source[source][:5]  # 每个来源最多5条
                selected.extend(posts)
        
        lines = []
        for i, article in enumerate(selected[:20], 1):  # 总共最多20条
            source_tag = f"[{article.source.upper()}]"
            lines.append(f"{i}. {source_tag} {article.title}")
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
