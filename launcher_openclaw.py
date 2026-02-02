#!/usr/bin/env python3
"""
AiTrend 启动中枢 (Launcher) - OpenClaw版本
使用 sessions_spawn 调用默认大模型
"""

import yaml
import json
import os
from typing import List, Dict, Any
from datetime import datetime

class Launcher:
    """启动中枢 - 使用OpenClaw大模型"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.sources = []
        self.processors = []
        self.output_module = None
        
    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        return {
            'sources': {
                'github_trend': {
                    'enabled': True,
                    'languages': ['python', 'javascript', 'go'],
                    'max_candidates': 5,
                    'growth_threshold': 0.5
                }
            },
            'output': {
                'min_length': 200,
                'max_length': 500
            },
            'publishers': {
                'discord': {'enabled': True}
            }
        }
    
    def init_modules(self):
        """初始化模块"""
        print("🚀 启动中枢初始化...")
        
        # 初始化信息源
        print("\n📡 初始化信息源模块...")
        try:
            from modules.sources.github_trend import GithubTrend
            source_config = self.config.get('sources', {}).get('github_trend', {})
            if source_config.get('enabled', False):
                self.sources.append(GithubTrend(source_config))
                print("  ✅ github_trend")
        except Exception as e:
            print(f"  ❌ github_trend: {e}")
        
        print(f"\n📊 模块加载完成: 信息源 {len(self.sources)} 个")
    
    def run_pipeline(self) -> List[Dict]:
        """运行完整流程"""
        results = []
        
        # 阶段1: 挖掘项目
        print("\n" + "="*60)
        print("阶段1: 信息源挖掘")
        print("="*60)
        
        all_candidates = []
        for source in self.sources:
            try:
                print(f"\n📡 从 {source.name} 挖掘...")
                candidates = source.discover()
                for c in candidates:
                    c['source_name'] = source.name
                all_candidates.extend(candidates)
                print(f"  发现 {len(candidates)} 个候选")
            except Exception as e:
                print(f"  ❌ 挖掘失败: {e}")
        
        print(f"\n📊 共发现 {len(all_candidates)} 个候选项目")
        
        # 阶段2: 使用大模型生成内容
        print("\n" + "="*60)
        print("阶段2: 大模型内容生成")
        print("="*60)
        
        for i, candidate in enumerate(all_candidates[:3], 1):  # 处理前3个
            print(f"\n📝 生成内容 {i}/3: {candidate.get('name', 'Unknown')}")
            
            try:
                content = self._generate_with_llm(candidate)
                if content:
                    results.append({
                        'name': candidate.get('name', ''),
                        'source': candidate.get('source_name', ''),
                        'content': content,
                        'url': candidate.get('url', ''),
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"  ✅ 生成成功 ({len(content)} 字符)")
                else:
                    print(f"  ❌ 生成失败")
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
        
        return results
    
    def _generate_with_llm(self, candidate: Dict) -> str:
        """
        使用OpenClaw大模型生成内容
        
        1. 抓取README
        2. 构建提示
        3. 调用sessions_spawn
        4. 返回结果
        """
        
        name = candidate.get('name', '')
        description = candidate.get('description', '')
        url = candidate.get('url', '')
        stars = candidate.get('stars', 0)
        language = candidate.get('language', '')
        
        # 抓取README
        print(f"  📄 抓取README...", end=' ')
        readme = self._fetch_readme(url)
        print("✅" if readme else "⚠️ 无README")
        
        # 构建提示
        context = self._build_prompt_context(name, description, readme, stars, language)
        
        # 调用大模型
        print(f"  🤖 调用OpenClaw大模型生成...")
        
        # 使用 sessions_spawn 工具
        result = self._call_openclaw_llm(context)
        
        if result:
            # 清理结果
            result = self._clean_output(result)
            # 添加URL
            result += f"\n\n{url}"
            return result
        
        return ""
    
    def _build_prompt_context(self, name: str, description: str, readme: str, 
                              stars: int, language: str) -> str:
        """构建提示上下文"""
        
        parts = [f"项目名称: {name}"]
        
        if description:
            parts.append(f"项目描述: {description}")
        
        if stars:
            parts.append(f"GitHub Stars: {stars}")
        
        if language:
            parts.append(f"主要语言: {language}")
        
        if readme:
            # 提取README前1000字的关键部分
            readme_preview = self._extract_readme_preview(readme)
            if readme_preview:
                parts.append(f"README预览:\n{readme_preview}")
        
        return "\n\n".join(parts)
    
    def _extract_readme_preview(self, readme: str) -> str:
        """提取README预览"""
        lines = readme.split('\n')
        preview_lines = []
        
        for line in lines[:30]:  # 前30行
            line = line.strip()
            # 跳过代码块
            if line.startswith('```'):
                continue
            # 保留描述性内容
            if line and not line.startswith('#') and len(line) > 10:
                preview_lines.append(line[:100])
            # 保留功能列表
            if line.startswith('- ') or line.startswith('* '):
                preview_lines.append(line[:100])
            
            if len('\n'.join(preview_lines)) > 500:
                break
        
        return '\n'.join(preview_lines[:10])
    
    def _fetch_readme(self, url: str) -> str:
        """抓取README"""
        import requests
        
        # 提取repo路径
        parts = url.replace('https://', '').replace('http://', '').split('/')
        if len(parts) < 3:
            return ""
        
        repo_path = f"{parts[1]}/{parts[2]}"
        
        urls = [
            f"https://raw.githubusercontent.com/{repo_path}/main/README.md",
            f"https://raw.githubusercontent.com/{repo_path}/master/README.md",
        ]
        
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
        for readme_url in urls:
            try:
                response = session.get(readme_url, timeout=10)
                if response.status_code == 200:
                    return response.text[:3000]  # 限制长度
            except:
                continue
        
        return ""
    
    def _call_openclaw_llm(self, context: str) -> str:
        """调用OpenClaw大模型"""
        import subprocess
        import tempfile
        import time
        
        # 构建任务
        task = f"""请用自然叙述的方式介绍以下项目：

{context}

要求：
1. 不要列表、不要序号、不要用 bullet points
2. 禁止空话套话（如"针对痛点"、"功能设计"、"架构清晰"、"旨在解决"）
3. 像跟朋友介绍一样口语化、流畅
4. 突出产品特点、亮点、为什么值得关注
5. 控制在400字以内
6. 直接输出内容，不要标题，不要"好的"、"明白"等确认词"""
        
        # 创建临时文件存储任务
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(task)
            task_file = f.name
        
        # 创建临时文件存储结果
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            result_file = f.name
        
        # 使用 openclaw 命令行工具
        # 注意：这里我们无法直接调用，需要通过特殊方式
        # 暂时返回一个标记，表示需要手动处理
        
        try:
            # 尝试使用环境变量传递
            os.environ['_AITREND_LLM_TASK'] = task
            os.environ['_AITREND_LLM_RESULT'] = result_file
            
            # 创建一个标记文件
            marker_file = '/tmp/aitrend_llm_request.txt'
            with open(marker_file, 'w', encoding='utf-8') as f:
                f.write(task)
            
            # 返回空，表示需要外部处理
            return ""
            
        except Exception as e:
            print(f"❌ 调用失败: {e}")
            return ""
        
        finally:
            # 清理
            try:
                os.unlink(task_file)
            except:
                pass
    
    def _clean_output(self, text: str) -> str:
        """清理输出"""
        import re
        
        # 移除常见的前缀
        prefixes = ['好的，', '明白，', '好的。', '明白。', '以下是', '这是']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # 清理结构化痕迹
        text = re.sub(r'^[\s]*[-*•][\s]+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+[.、][\s]+', '', text, flags=re.MULTILINE)
        text = re.sub(r'第一|第二|第三|首先|其次|最后', '', text)
        
        # 清理空话
        text = re.sub(r'针对痛点|针对需求|解决痛点', '', text)
        text = re.sub(r'功能设计|架构设计', '', text)
        text = re.sub(r'旨在|致力于|目的是', '', text)
        
        return text.strip()
    
    def publish(self, contents: List[Dict]):
        """发布内容"""
        print("\n" + "="*60)
        print("阶段3: 内容发布")
        print("="*60)
        
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            print("  ❌ 未配置 DISCORD_WEBHOOK_URL")
            return
        
        import requests
        import time
        
        published = 0
        for i, content in enumerate(contents, 1):
            try:
                print(f"  发布 {i}/{len(contents)}: {content['name'][:35]}...")
                
                payload = {
                    'username': 'AiTrend',
                    'thread_name': f"{content['name']} – OpenClaw生成",
                    'content': content['content'][:1900]
                }
                
                response = requests.post(webhook_url, json=payload, timeout=15)
                response.raise_for_status()
                
                published += 1
                print(f"    ✅ 成功")
                time.sleep(2)
                
            except Exception as e:
                print(f"    ❌ 失败: {e}")
        
        print(f"\n  ✅ 成功发布 {published}/{len(contents)} 条内容")

def main():
    """主入口"""
    # 加载环境变量
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    print("="*60)
    print("🎯 AiTrend - OpenClaw大模型版")
    print("="*60)
    
    launcher = Launcher()
    launcher.init_modules()
    
    # 运行流程
    results = launcher.run_pipeline()
    
    # 发布
    if results:
        launcher.publish(results)
    
    print("\n" + "="*60)
    print(f"✅ 流程完成，生成 {len(results)} 条内容")
    print("="*60)

if __name__ == '__main__':
    main()
