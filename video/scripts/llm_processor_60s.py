#!/usr/bin/env python3
"""
60秒视频脚本生成器
生成精简浓缩的视频脚本
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend')


class VideoScriptGenerator60s:
    """60秒视频脚本生成器"""
    
    def __init__(self):
        # 加载Gemini配置
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
    
    def generate(self, selected_hotspots: list, date: str = None) -> dict:
        """
        生成60秒视频脚本
        
        时长分配:
        - 开场: 3秒 (一句话)
        - 热点1: 18秒 (详细)
        - 热点2: 18秒 (详细)
        - 热点3: 18秒 (详细)
        - 结尾: 3秒 (一句话)
        总计: 60秒
        """
        date = date or datetime.now().strftime('%Y-%m-%d')
        
        # 选择前3个热点
        top3 = selected_hotspots[:3]
        
        print(f"🎬 生成60秒脚本，精选 {len(top3)} 个热点")
        
        # 构建Prompt
        prompt = self._build_prompt(top3, date)
        
        # 调用Gemini生成
        script = self._call_llm(prompt)
        
        return {
            'date': date,
            'total_duration': '60秒',
            'scene_count': 5,
            'hotspot_count': len(top3),
            'script': script
        }
    
    def _build_prompt(self, hotspots: list, date: str) -> str:
        """构建60秒脚本生成Prompt"""
        
        hotspots_text = json.dumps(hotspots, ensure_ascii=False, indent=2)
        
        return f"""你是专业AI新闻视频编辑。请将以下3个热点转化为60秒视频脚本。

日期: {date}
热点数据:
{hotspots_text}

【时长分配 - 严格控制在60秒】
1. 开场 (3秒): 一句话快速引入，不要铺垫
2. 热点1 (18秒): 详细介绍，口语化，包含核心亮点
3. 热点2 (18秒): 详细介绍，口语化，包含核心亮点
4. 热点3 (18秒): 详细介绍，口语化，包含核心亮点
5. 结尾 (3秒): 一句话收尾 + 引导关注

【语速要求】
- 语速较快（比正常快20%）
- 每句话简短有力
- 避免重复和废话

【风格要求】
- 开场直接: "今天AI圈发生了什么？"
- 热点介绍直奔主题
- 使用口语化表达
- 每段都有"钩子"保持注意力

【输出格式 - JSON】
{{
  "opening": "开场白（3秒朗读量，一句话）",
  "hotspots": [
    {{
      "rank": 1,
      "title": "优化后的口语化标题",
      "script": "详细脚本（18秒朗读量，约70-80字）",
      "key_point": "一句话核心亮点",
      "duration": "18秒"
    }}
  ],
  "closing": "结尾（3秒朗读量，一句话 + 引导关注）",
  "total_duration": "60秒"
}}

请只输出JSON，不要任何解释。"""
    
    def _call_llm(self, prompt: str) -> dict:
        """调用Gemini API"""
        import urllib.request
        import urllib.error
        
        payload = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2000
            }
        }, ensure_ascii=False).encode('utf-8')
        
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
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            print(f"⚠️  LLM调用失败，使用默认脚本: {e}")
            return self._default_script()
    
    def _default_script(self) -> dict:
        """默认脚本（LLM失败时使用）"""
        return {
            "opening": "今天AI圈又有大事发生！",
            "hotspots": [
                {
                    "rank": 1,
                    "title": "热点一",
                    "script": "这是第一个热点的详细介绍。",
                    "key_point": "核心亮点",
                    "duration": "18秒"
                },
                {
                    "rank": 2,
                    "title": "热点二",
                    "script": "这是第二个热点的详细介绍。",
                    "key_point": "核心亮点",
                    "duration": "18秒"
                },
                {
                    "rank": 3,
                    "title": "热点三",
                    "script": "这是第三个热点的详细介绍。",
                    "key_point": "核心亮点",
                    "duration": "18秒"
                }
            ],
            "closing": "以上就是今天的热点，点赞关注不错过！",
            "total_duration": "60秒"
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='60秒视频脚本生成器')
    parser.add_argument('--input', '-i', required=True, help='精选热点JSON文件')
    parser.add_argument('--output', '-o', required=True, help='输出脚本文件')
    parser.add_argument('--date', '-d', help='日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 加载热点
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hotspots = data.get('hotspots', [])
    
    # 生成脚本
    generator = VideoScriptGenerator60s()
    result = generator.generate(hotspots, args.date or data.get('date'))
    
    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 60秒脚本已生成: {args.output}")
    print(f"📊 时长: {result['total_duration']}, 场景: {result['scene_count']}")


if __name__ == '__main__':
    main()
