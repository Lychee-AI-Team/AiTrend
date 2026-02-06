#!/usr/bin/env python3
"""
Gemini LLM 视频脚本生成器
复用 AiTrend 的 Gemini 配置
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Dict, Any
from datetime import datetime

# 添加 AiTrend 路径
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend')


class GeminiLLMClient:
    """Gemini LLM 客户端（与 AiTrend 实现一致）"""
    
    def __init__(self, model_name: str = None, api_key: str = None):
        """
        初始化 Gemini 客户端
        
        Args:
            model_name: 模型名称，默认从环境变量读取
            api_key: API Key，默认从环境变量读取
        """
        # 从环境变量读取配置（与 AiTrend 一致）
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model_name = model_name or os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        
        if not self.api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not set. 请确保环境变量已正确导出")
        
        # Gemini API URL
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        调用 Gemini API 生成内容
        
        Args:
            prompt: 提示词
            temperature: 温度（创造性）
            max_tokens: 最大输出长度
            
        Returns:
            生成的文本内容
        """
        # 构建请求体
        payload = json.dumps({
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }, ensure_ascii=False).encode('utf-8')
        
        # 构建请求
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        req = urllib.request.Request(
            self.api_url,
            data=payload,
            headers=headers,
            method="POST"
        )
        
        try:
            # 发送请求
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # 提取生成的文本
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    return text
                else:
                    raise Exception("Gemini API 返回空结果")
                    
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise Exception(f"Gemini API 错误: {e.code} - {error_body}")
    
    def generate_video_script(self, hotspots_data: Dict) -> Dict:
        """
        生成视频脚本（专用方法）
        
        Args:
            hotspots_data: 热点数据（精选后的5-10条）
            
        Returns:
            视频脚本 JSON
        """
        # 构建 Prompt
        prompt = self._build_script_prompt(hotspots_data)
        
        print(f"🤖 调用 Gemini ({self.model_name}) 生成脚本...")
        
        # 调用 Gemini
        response = self.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # 解析 JSON 响应
        try:
            script = json.loads(response)
            print(f"✅ 脚本生成成功")
            return script
        except json.JSONDecodeError:
            # 如果返回的不是标准 JSON，尝试提取 JSON 部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    script = json.loads(json_match.group())
                    print(f"✅ 脚本生成成功（从文本中提取）")
                    return script
                except:
                    pass
            
            # 如果还是失败，返回原始文本包装
            print(f"⚠️  返回格式非标准 JSON，包装为文本")
            return {
                "raw_text": response,
                "parse_error": True
            }
    
    def _build_script_prompt(self, hotspots_data: Dict) -> str:
        """构建视频脚本生成 Prompt"""
        
        hotspots = hotspots_data.get('hotspots', [])
        date = hotspots_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # 构建热点摘要
        hotspots_summary = []
        for item in hotspots:
            summary = {
                'rank': item.get('rank', 0),
                'title': item.get('title', ''),
                'summary': item.get('summary', ''),
                'source': item.get('source_origin', 'unknown'),
                'heat_score': item.get('heat_score', 0)
            }
            hotspots_summary.append(summary)
        
        hotspots_json = json.dumps(hotspots_summary, ensure_ascii=False, indent=2)
        
        return f"""你是专业AI新闻视频编辑，请将以下热点数据转化为3分钟视频播报脚本。

日期：{date}
热点数据：
{hotspots_json}

输出要求：
1. opening（开场）：10-15秒，今日概览，吸引观众
   - 包含日期和总览
   - 语气热情专业
   
2. detailed_hotspots（详细播报）：前3条热点，各40-45秒
   - 每条包含：
     - title: 优化后的口语化标题
     - script: 详细播报脚本（3-4句话，口语化）
     - key_point: 核心观点/数据
     - source: 信息来源
     - duration: "45秒"
   
3. quick_hotspots（快速播报）：剩余热点，各15-20秒，一句话摘要
   - 每条包含：
     - title: 热点标题
     - script: 一句话摘要
     - duration: "20秒"
   
4. closing（结尾）：5-10秒，总结+引导关注
   - 简洁有力
   - 引导关注

风格要求：
- 口语化、自然、像真人主播
- 专业但不生硬
- 每段都有钩子，保持观众注意力
- 100%中文输出
- 避免过于学术化的表达
- 适当使用口语连接词（"那么"、"接下来"、"值得一提的是"）

输出格式（严格JSON）：
{{
  "opening": "开场白文本（10-15秒朗读量）",
  "detailed_hotspots": [
    {{
      "rank": 1,
      "title": "优化后的口语化标题",
      "script": "详细播报脚本（40-45秒朗读量）",
      "key_point": "核心观点或数据",
      "source": "来源名称",
      "duration": "45秒"
    }}
  ],
  "quick_hotspots": [
    {{
      "rank": 4,
      "title": "热点标题",
      "script": "一句话摘要（15-20秒朗读量）",
      "duration": "20秒"
    }}
  ],
  "closing": "结尾文本（5-10秒朗读量）",
  "total_duration_estimate": "3分30秒",
  "hotspot_count": 5
}}

请只输出 JSON，不要有任何解释说明。"""


class VideoScriptGenerator:
    """视频脚本生成器"""
    
    def __init__(self):
        self.llm_client = GeminiLLMClient()
    
    def generate(self, input_file: str, output_file: str = None) -> Dict[str, Any]:
        """
        从精选热点生成视频脚本
        
        Args:
            input_file: 精选热点文件路径（selected_YYYY-MM-DD.json）
            output_file: 输出文件路径（可选）
            
        Returns:
            视频脚本数据
        """
        # 加载精选数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📖 加载精选数据: {data.get('selected_count', 0)} 条热点")
        
        # 调用 LLM 生成脚本
        script = self.llm_client.generate_video_script(data)
        
        # 构建完整输出
        output = {
            'date': data.get('date'),
            'generation_time': datetime.now().isoformat(),
            'model': self.llm_client.model_name,
            'input_file': input_file,
            'video_script': script
        }
        
        # 保存到文件
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"💾 脚本已保存: {output_file}")
        
        # 打印摘要
        if 'opening' in script:
            print(f"\n📋 脚本结构:")
            print(f"  开场: {len(script.get('opening', ''))} 字")
            print(f"  详细播报: {len(script.get('detailed_hotspots', []))} 条")
            print(f"  快速播报: {len(script.get('quick_hotspots', []))} 条")
            print(f"  结尾: {len(script.get('closing', ''))} 字")
            print(f"  预估时长: {script.get('total_duration_estimate', '未知')}")
        
        return output


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='视频脚本生成器')
    parser.add_argument('--input', '-i', required=True, help='精选热点文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--model', '-m', help='Gemini 模型名称（可选，默认从环境变量读取）')
    
    args = parser.parse_args()
    
    # 如果指定了模型，临时设置环境变量
    if args.model:
        os.environ['GEMINI_MODEL'] = args.model
    
    generator = VideoScriptGenerator()
    result = generator.generate(args.input, args.output)


if __name__ == '__main__':
    main()
