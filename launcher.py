#!/usr/bin/env python3
"""
AiTrend 启动中枢 v2 (Launcher)
统一调度、配置管理、流程控制
支持模块化信息源
"""

import yaml
import json
import importlib
from typing import List, Dict, Any
from datetime import datetime

# 信息源模块映射表
SOURCE_MAP = {
    'github_trend': ('modules.sources.github_trend', 'GithubTrend'),
    'producthunt': ('modules.sources.producthunt', 'Producthunt'),
    'hackernews': ('modules.sources.hackernews', 'Hackernews'),
    'reddit': ('modules.sources.reddit', 'Reddit'),
    'arxiv_papers': ('modules.sources.arxiv_papers', 'ArxivPapers'),
}

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
            print(f"⚠️ 配置文件 {path} 不存在，使用默认配置")
            return self._default_config()
        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}，使用默认配置")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'sources': {
                'github_trend': {
                    'enabled': True,
                    'languages': ['python', 'javascript', 'go'],
                    'max_candidates': 10,
                    'growth_threshold': 0.5
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
                'forum': {'enabled': True}
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
                    # 从映射表查找模块和类名
                    if source_name in SOURCE_MAP:
                        module_path, class_name = SOURCE_MAP[source_name]
                        module = importlib.import_module(module_path)
                        source_class = getattr(module, class_name)
                        source_instance = source_class(source_config)
                        self.sources.append(source_instance)
                        print(f"  ✅ {source_name} ({class_name})")
                    else:
                        print(f"  ❌ {source_name}: 未知模块，请在 SOURCE_MAP 中注册")
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
                source_name = getattr(source, 'name', source.__class__.__name__)
                print(f"\n📡 从 {source_name} 挖掘...")
                candidates = source.discover()
                print(f"  发现 {len(candidates)} 个候选项目")
                
                # 添加来源标记
                for c in candidates:
                    c['source_name'] = source_name
                
                all_candidates.extend(candidates)
            except Exception as e:
                print(f"  ❌ 挖掘失败: {e}")
        
        print(f"\n📊 共发现 {len(all_candidates)} 个候选项目")
        
        if not all_candidates:
            print("⚠️ 未获取到候选项目，流程结束")
            return results
        
        # 阶段2: 对每个候选项目进行多维度整理
        print("\n" + "="*60)
        print("阶段2: 信息整理")
        print("="*60)
        
        # 限制处理数量避免过载
        max_to_process = min(len(all_candidates), self.config.get('system', {}).get('max_iterations', 10))
        
        for i, candidate in enumerate(all_candidates[:max_to_process], 1):
            print(f"\n🔍 整理项目 {i}/{max_to_process}: {candidate.get('name', 'Unknown')[:50]}")
            
            # 收集所有整理模块的输出
            processed_fragments = []
            
            for processor in self.processors:
                try:
                    proc_name = getattr(processor, 'name', processor.__class__.__name__)
                    print(f"  📄 {proc_name}...", end=' ')
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
            elif not self.processors:
                # 如果没有整理模块，直接输出原始信息
                print(f"  ✍️ 直接使用原始信息...")
                from modules.output.arxiv_composer import ArxivContentComposer
                composer = ArxivContentComposer()
                
                # 检查是否为 arXiv 论文
                if 'arxiv_id' in candidate:
                    final_content = composer.compose_narrative(candidate)
                else:
                    # 通用处理
                    final_content = f"**{candidate.get('name', '')}**\n\n{candidate.get('description', '')[:500]}\n\n{candidate.get('url', '')}"
                
                results.append({
                    'name': candidate.get('name', ''),
                    'source': candidate.get('source_name', ''),
                    'content': final_content,
                    'url': candidate.get('url', ''),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ ({len(final_content)} 字符)")
        
        return results
    
    def publish(self, contents: List[Dict]):
        """发布内容"""
        if not contents:
            print("\n⚠️ 无内容需要发布")
            return
        
        print("\n" + "="*60)
        print("阶段3: 内容发布")
        print("="*60)
        
        for pub_name, pub_config in self.config.get('publishers', {}).items():
            if pub_config.get('enabled', False):
                try:
                    print(f"\n📤 发布到 {pub_name}...")
                    
                    if pub_name == 'forum':
                        self._publish_to_forum(contents, pub_config)
                    elif pub_name == 'text':
                        self._publish_to_text(contents, pub_config)
                    else:
                        print(f"  ⚠️ 未知发布渠道: {pub_name}")
                    
                except Exception as e:
                    print(f"  ❌ 发布失败: {e}")
    
    def _publish_to_forum(self, contents: List[Dict], config: Dict):
        """发布到论坛（Discord Forum）"""
        from publishers import create_publisher
        
        try:
            publisher = create_publisher('forum', config)
            
            # 转换格式
            forums_contents = []
            for c in contents:
                forums_contents.append({
                    'name': c['name'],
                    'content': c['content'],
                    'url': c['url'],
                    'source': c['source']
                })
            
            published = publisher.publish_batch(forums_contents)
            print(f"  ✅ 论坛发布完成: {published}/{len(contents)} 条成功")
            
        except Exception as e:
            print(f"  ❌ 论坛发布失败: {e}")
    
    def _publish_to_text(self, contents: List[Dict], config: Dict):
        """发布到文字频道"""
        from publishers import create_publisher
        
        try:
            publisher = create_publisher('text', config)
            
            # 转换格式
            text_contents = []
            for c in contents:
                text_contents.append({
                    'name': c['name'],
                    'content': c['content'],
                    'url': c['url'],
                    'source': c['source']
                })
            
            published = publisher.publish_batch(text_contents)
            print(f"  ✅ 文字频道发布完成: {published}/{len(contents)} 条成功")
            
        except Exception as e:
            print(f"  ❌ 文字频道发布失败: {e}")


def load_env():
    """加载环境变量"""
    import os
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ 环境变量加载完成")


def main():
    """主入口"""
    print("="*60)
    print("🎯 AiTrend 模块化系统启动")
    print("="*60)
    
    # 加载环境变量
    load_env()
    
    # 创建启动器
    launcher = Launcher()
    launcher.init_modules()
    
    # 运行流程
    results = launcher.run_pipeline()
    
    # 发布
    launcher.publish(results)
    
    print("\n" + "="*60)
    print(f"✅ 流程完成，共生成 {len(results)} 条内容")
    print("="*60)


if __name__ == '__main__':
    main()
