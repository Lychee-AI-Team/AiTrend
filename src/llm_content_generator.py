"""
LLM内容生成器
使用Gemini API为每个项目生成独特内容
严格遵守AiTrend宪法文档要求

配置入口：config/config.json -> summarizer.model

重要变更：
- 不再验证LLM输出（信任大模型质量）
- 改为验证输入数据质量（确保输入有足够信息量）
- 使用HTTP API直接调用（避免google.generativeai库的中文字符问题）
"""
import os
import json
import socket
import urllib.request
import urllib.error
from typing import Dict, Optional

class LLMContentGenerator:
    """使用Gemini生成独特内容（HTTP API版本）"""
    
    def __init__(self, model_name: str = None):
        """
        初始化LLM生成器
        
        Args:
            model_name: 模型名称，默认从配置文件读取
        """
        # 加载配置获取模型名称（唯一配置入口）
        if model_name is None:
            from .core.config_loader import load_config
            config = load_config()
            summarizer_config = config.get('summarizer', {})
            model_name = summarizer_config.get('model', 'gemini-2.5-flash')
        
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not set. 请确保环境变量已正确导出: export GEMINI_API_KEY='your-key'")
        
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    def _validate_input(self, article_data: Dict) -> tuple[bool, str]:
        """
        验证输入数据质量
        
        验证规则：
        1. 标题不能为空
        2. 标题不能只有网址
        3. 描述/摘要要有足够信息量（至少50字符）
        4. URL不能为空
        
        Returns:
            (是否合格, 不合格原因)
        """
        title = article_data.get('title', '').strip()
        summary = article_data.get('summary', '').strip()
        url = article_data.get('url', '').strip()
        
        # 检查标题
        if not title:
            return False, "标题为空"
        
        if len(title) < 3:
            return False, f"标题过短（{len(title)}字符），至少需要3字符"
        
        # 检查标题是否只是网址
        if title.startswith('http://') or title.startswith('https://'):
            return False, "标题不能只是网址"
        
        # 检查URL
        if not url:
            return False, "URL为空"
        
        if not url.startswith('http://') and not url.startswith('https://'):
            return False, "URL格式无效"
        
        # 检查描述/摘要的信息量
        info_text = f"{title} {summary}".strip()
        if len(info_text) < 50:
            return False, f"输入信息不足（{len(info_text)}字符），标题+描述至少需要50字符"
        
        # 检查是否包含有效信息（不只是占位符）
        meaningless_words = ['待补充', '暂无', 'unknown', 'n/a', 'null', 'none']
        if summary.lower() in meaningless_words or len(summary.strip()) < 5:
            # 如果summary无效，检查title是否足够长
            if len(title) < 30:
                return False, "描述无有效信息且标题过短"
        
        return True, ""
    
    def generate(self, article_data: Dict) -> str:
        """
        基于文章数据生成独特内容
        
        流程：
        1. 验证输入数据质量（前置验证）
        2. 使用LLM生成内容（信任大模型输出）
        3. 确保URL在内容中
        
        Returns:
            生成的内容
        
        Raises:
            RuntimeError: 输入不合格或LLM生成失败
        """
        title = article_data.get('title', '')
        summary = article_data.get('summary', '')
        url = article_data.get('url', '')
        source = article_data.get('source', '')
        metadata = article_data.get('metadata', {})
        
        # 【关键变更】验证输入数据质量，而非输出
        is_valid, error_msg = self._validate_input(article_data)
        if not is_valid:
            raise RuntimeError(f"❌ 输入数据不合格：{error_msg}")
        
        # 构建提示词
        prompt = self._build_prompt(title, summary, url, source, metadata)
        
        try:
            content = self._call_gemini_api(prompt, url)
            return content
            
        except Exception as e:
            raise RuntimeError(f"❌ LLM生成失败：{str(e)}")
    
    def _call_gemini_api(self, prompt: str, url: str) -> str:
        """
        调用Gemini HTTP API
        
        Args:
            prompt: 提示词
            url: 文章URL（用于确保在输出中）
            
        Returns:
            生成的内容
        """
        import sys
        print(f"   📝 开始生成内容...", file=sys.stderr)
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8000
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        # 设置socket级别的超时
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(60)
        
        try:
            print(f"   🌐 调用API: {self.model_name}...", file=sys.stderr)
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'candidates' not in result or not result['candidates']:
                    raise RuntimeError("API返回空结果")
                
                candidate = result['candidates'][0]
                if 'content' not in candidate or 'parts' not in candidate['content']:
                    raise RuntimeError("API返回格式错误")
                
                content = candidate['content']['parts'][0].get('text', '').strip()
                
                if not content:
                    raise RuntimeError("API返回空内容")
                
                # 确保URL在内容中
                if url not in content:
                    content = f"{content} {url}"
                
                print(f"   ✅ 内容生成完成 ({len(content)}字符)", file=sys.stderr)
                return content
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"API HTTP错误 {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"API请求失败: {e.reason}")
        except TimeoutError:
            raise RuntimeError("API请求超时")
        except socket.timeout:
            raise RuntimeError("API请求超时(socket)")
        finally:
            socket.setdefaulttimeout(old_timeout)
    
    def _build_prompt(self, title: str, summary: str, url: str, source: str, metadata: Dict) -> str:
        """构建提示词 - 严格遵守宪法文档"""
        
        lang = metadata.get('language', '')
        stars = metadata.get('stars', 0)
        
        base_info = f"""项目名称：{title}
项目介绍：{summary}
来源：{source}
链接：{url}"""
        
        if lang:
            base_info += f"\n编程语言：{lang}"
        if stars:
            base_info += f"\nGitHub Stars：{stars}"
        
        # 严格遵循宪法文档的禁止项和必须项
        return f"""基于以下项目信息，写一段150-200字的项目介绍。

【绝对禁止 - 硬性约束】
1. ❌ 禁止套话开头："最近发现"、"今天看到"、"找到一个"、"发现一个"
2. ❌ 禁止"这是一个..."、"是一个..."的句式
3. ❌ 禁止"主要解决...问题"、"主要功能包括"
4. ❌ 禁止序号：第一第二、首先其次
5. ❌ 禁止列表符号：- * •
6. ❌ 禁止空话："针对痛点"、"功能设计"、"架构清晰"、"旨在解决"
7. ❌ 禁止重复用词和句式

【必须遵守】
1. ✅ 直接描述产品是什么、能做什么、为什么值得用
2. ✅ 连续段落，无结构化痕迹
3. ✅ 控制在150-200字
4. ✅ 最后必须包含链接
5. ✅ 不要分段，写成一段连续文本

项目信息：
{base_info}

直接输出介绍内容（不要加标题、不要加总结、不要分段）："""

# 单例
_llm_generator = None

def get_llm_generator() -> LLMContentGenerator:
    """获取LLM生成器单例"""
    global _llm_generator
    if _llm_generator is None:
        _llm_generator = LLMContentGenerator()
    return _llm_generator
