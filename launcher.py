#!/usr/bin/env python3
"""
AiTrend 启动中枢 (Launcher)
统一调度、配置管理、流程控制
"""

import yaml
import json
import importlib
from typing import List, Dict, Any
from datetime import datetime

class Launcher:
    """启动中枢 - 统一调度所有模块"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.sources = []
        self.processors = []
        self.output_module = None
        self.publishers = []
        
    def _load_config(self, path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'sources': {
                'github_trend': {
                    'enabled': True,
                    'languages': ['python', 'javascript', 'go'],
                    'max_candidates': 10,
                    'growth_threshold': 0.1  # 增长率阈值
                }
            },
            'processors': {
                'readme': {'enabled': True},
                'search': {'enabled': True}
            },
            'output': {
                'style': 'natural_narrative',
                'min_length': 200,
                'max_length': 800
            },
            'publishers': {
                'discord': {'enabled': True}
            }
        }
    
    def init_modules(self):
        """初始化所有模块"""
        print("🚀 启动中枢初始化...")
        
        # 1. 初始化信息源模块
        print("\n📡 初始化信息源模块...")
        for source_name, source_config in self.config.get('sources', {}).items():
            if source_config.get('enabled', False):
                try:
                    module = importlib.import_module(f'modules.sources.{source_name}')
                    source_class = getattr(module, 'GithubTrend')
                    source_instance = source_class(source_config)
                    self.sources.append(source_instance)
                    print(f"  ✅ {source_name}")
                except Exception as e:
                    print(f"  ❌ {source_name}: {e}")
        
        # 2. 初始化信息整理模块
        print("\n🔧 初始化信息整理模块...")
        for proc_name, proc_config in self.config.get('processors', {}).items():
            if proc_config.get('enabled', False):
                try:
                    module = importlib.import_module(f'modules.processors.{proc_name}_processor')
                    proc_class = getattr(module, f'{proc_name.title()}Processor')
                    proc_instance = proc_class(proc_config)
                    self.processors.append(proc_instance)
                    print(f"  ✅ {proc_name}_processor")
                except Exception as e:
                    print(f"  ❌ {proc_name}_processor: {e}")
        
        # 3. 初始化输出整理模块
        print("\n✍️ 初始化输出整理模块...")
        try:
            from modules.output.narrative_composer import NarrativeComposer
            self.output_module = NarrativeComposer(self.config.get('output', {}))
            print(f"  ✅ narrative_composer")
        except Exception as e:
            print(f"  ❌ narrative_composer: {e}")
        
        print(f"\n📊 模块加载完成:")
        print(f"  信息源: {len(self.sources)} 个")
        print(f"  整理模块: {len(self.processors)} 个")
        print(f"  输出模块: {'已加载' if self.output_module else '未加载'}")
    
    def run_pipeline(self) -> List[Dict]:
        """
        运行完整流程
        返回生成的所有内容
        """
        results = []
        
        # 阶段1: 从各信息源获取候选项目
        print("\n" + "="*60)
        print("阶段1: 信息源挖掘")
        print("="*60)
        
        all_candidates = []
        for source in self.sources:
            try:
                print(f"\n📡 从 {source.name} 挖掘...")
                candidates = source.discover()
                print(f"  发现 {len(candidates)} 个候选项目")
                
                # 添加来源标记
                for c in candidates:
                    c['source_name'] = source.name
                
                all_candidates.extend(candidates)
            except Exception as e:
                print(f"  ❌ 挖掘失败: {e}")
        
        print(f"\n📊 共发现 {len(all_candidates)} 个候选项目")
        
        # 阶段2: 对每个候选项目进行多维度整理
        print("\n" + "="*60)
        print("阶段2: 信息整理")
        print("="*60)
        
        for i, candidate in enumerate(all_candidates[:5], 1):  # 先处理前5个演示
            print(f"\n🔍 整理项目 {i}/5: {candidate.get('name', 'Unknown')}")
            
            # 收集所有整理模块的输出
            processed_fragments = []
            
            for processor in self.processors:
                try:
                    print(f"  📄 {processor.name}...", end=' ')
                    fragment = processor.process(candidate)
                    if fragment:
                        processed_fragments.append(fragment)
                        print(f"✅ ({len(fragment)} 字符)")
                    else:
                        print("⚠️ 无输出")
                except Exception as e:
                    print(f"❌ {e}")
            
            # 阶段3: 输出整理
            if processed_fragments and self.output_module:
                print(f"  ✍️ 合成最终内容...", end=' ')
                try:
                    final_content = self.output_module.compose(
                        candidate=candidate,
                        fragments=processed_fragments
                    )
                    
                    results.append({
                        'name': candidate.get('name', ''),
                        'source': candidate.get('source_name', ''),
                        'content': final_content,
                        'url': candidate.get('url', ''),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    print(f"✅ ({len(final_content)} 字符)")
                except Exception as e:
                    print(f"❌ {e}")
        
        return results
    
    def publish(self, contents: List[Dict]):
        """发布内容"""
        print("\n" + "="*60)
        print("阶段4: 内容发布")
        print("="*60)
        
        for pub_name, pub_config in self.config.get('publishers', {}).items():
            if pub_config.get('enabled', False):
                try:
                    print(f"\n📤 发布到 {pub_name}...")
                    
                    if pub_name == 'discord':
                        self._publish_to_discord(contents, pub_config)
                    
                except Exception as e:
                    print(f"  ❌ 发布失败: {e}")
    
    def _publish_to_discord(self, contents: List[Dict], config: Dict):
        """发布到Discord"""
        import os
        import requests
        import time
        
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not webhook_url:
            print("  ❌ 未配置 DISCORD_WEBHOOK_URL")
            return
        
        published = 0
        for i, content in enumerate(contents, 1):
            try:
                print(f"  发布 {i}/{len(contents)}: {content['name'][:35]}...")
                
                # 创建论坛帖子
                payload = {
                    'username': 'AiTrend',
                    'thread_name': f"{content['name']} – GitHub趋势",
                    'content': content['content'][:1900]  # Discord限制
                }
                
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=15
                )
                response.raise_for_status()
                
                published += 1
                print(f"    ✅ 成功")
                
                # 避免速率限制
                time.sleep(2)
                
            except Exception as e:
                print(f"    ❌ 失败: {e}")
        
        print(f"\n  ✅ 成功发布 {published}/{len(contents)} 条内容")

def main():
    """主入口"""
    # 加载环境变量
    import os
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    print("="*60)
    print("🎯 AiTrend 模块化系统启动")
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
