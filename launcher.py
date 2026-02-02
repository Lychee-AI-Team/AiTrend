#!/usr/bin/env python3
"""
AiTrend 启动中枢 v3 (Launcher)
统一调度、配置管理、流程控制
支持模块化信息源 + 全流程追踪日志
"""

import yaml
import json
import importlib
import time
from typing import List, Dict, Any, Tuple
from datetime import datetime
from modules.trace_logger import TraceLogger, get_trace_logger

# 信息源模块映射表
SOURCE_MAP = {
    'github_trend': ('modules.sources.github_trend', 'GithubTrend'),
    'producthunt': ('modules.sources.producthunt', 'Producthunt'),
    'hackernews': ('modules.sources.hackernews', 'Hackernews'),
    'reddit': ('modules.sources.reddit', 'Reddit'),
    'arxiv_papers': ('modules.sources.arxiv_papers', 'ArxivPapers'),
}


class Launcher:
    """启动中枢 - 统一调度所有模块，支持全流程追踪"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.sources = []
        self.processors = []
        self.output_module = None
        self.publishers = []
        self.trace_logger = get_trace_logger()
        
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
            'sources': {'github_trend': {'enabled': True}},
            'processors': {'readme': {'enabled': True}},
            'output': {'style': 'natural_narrative'},
            'publishers': {'forum': {'enabled': True}},
            'system': {'max_iterations': 10, 'enable_trace': True}
        }
    
    def init_modules(self):
        """初始化所有模块"""
        print("🚀 启动中枢初始化...")
        
        # 1. 初始化信息源模块
        print("\n📡 初始化信息源模块...")
        for source_name, source_config in self.config.get('sources', {}).items():
            if source_config.get('enabled', False):
                try:
                    if source_name in SOURCE_MAP:
                        module_path, class_name = SOURCE_MAP[source_name]
                        module = importlib.import_module(module_path)
                        source_class = getattr(module, class_name)
                        source_instance = source_class(source_config)
                        self.sources.append(source_instance)
                        print(f"  ✅ {source_name}")
                    else:
                        print(f"  ❌ {source_name}: 未知模块")
                except Exception as e:
                    print(f"  ❌ {source_name}: {e}")
        
        # 2. 初始化整理模块
        print("\n🔧 初始化整理模块...")
        for proc_name, proc_config in self.config.get('processors', {}).items():
            if proc_config.get('enabled', False):
                try:
                    module = importlib.import_module(f'modules.processors.{proc_name}_processor')
                    proc_class = getattr(module, f'{proc_name.title()}Processor')
                    proc_instance = proc_class(proc_config)
                    self.processors.append(proc_instance)
                    print(f"  ✅ {proc_name}")
                except Exception as e:
                    print(f"  ❌ {proc_name}: {e}")
        
        # 3. 初始化输出模块
        print("\n✍️ 初始化输出模块...")
        try:
            from modules.output.narrative_composer import NarrativeComposer
            self.output_module = NarrativeComposer(self.config.get('output', {}))
            print(f"  ✅ narrative_composer")
        except Exception as e:
            print(f"  ⚠️ narrative_composer: {e}")
        
        print(f"\n📊 模块加载: {len(self.sources)} 源, {len(self.processors)} 处理器")
    
    def run_pipeline(self) -> List[Dict]:
        """
        运行完整流程，带追踪日志
        
        Returns:
            包含 trace_id 的内容列表
        """
        results = []
        enable_trace = self.config.get('system', {}).get('enable_trace', True)
        
        # 阶段1: 信息源挖掘
        print("\n" + "="*60)
        print("阶段1: 信息源挖掘")
        print("="*60)
        
        all_candidates = []
        for source in self.sources:
            try:
                source_name = getattr(source, 'name', source.__class__.__name__)
                print(f"\n📡 {source_name} 挖掘...")
                
                candidates = source.discover()
                print(f"  ✅ {len(candidates)} 个候选")
                
                for c in candidates:
                    c['source_name'] = source_name
                    # 为每个候选生成追踪ID
                    if enable_trace:
                        c['trace_id'] = self.trace_logger.generate_trace_id(c)
                        self.trace_logger.create_trace(c['trace_id'], c)
                        self.trace_logger.log_source_discover(c['trace_id'], source_name, len(candidates))
                
                all_candidates.extend(candidates)
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        print(f"\n📊 共 {len(all_candidates)} 个候选 (每个都有唯一追踪ID)")
        
        if not all_candidates:
            return results
        
        # 阶段2: 信息整理
        print("\n" + "="*60)
        print("阶段2: 信息整理")
        print("="*60)
        
        max_to_process = min(len(all_candidates), 
                           self.config.get('system', {}).get('max_iterations', 10))
        
        for i, candidate in enumerate(all_candidates[:max_to_process], 1):
            trace_id = candidate.get('trace_id', 'unknown')
            name = candidate.get('name', 'Unknown')[:40]
            
            print(f"\n🔍 [{i}/{max_to_process}] {name}")
            print(f"   追踪ID: {trace_id}")
            
            # 处理器链
            processed_fragments = []
            
            if self.processors:
                for processor in self.processors:
                    proc_name = getattr(processor, 'name', processor.__class__.__name__)
                    start_time = time.time()
                    
                    try:
                        print(f"   📄 {proc_name}...", end=' ')
                        
                        if enable_trace:
                            self.trace_logger.log_module_start(trace_id, proc_name, 
                                                               {'input': candidate.get('url', '')})
                        
                        fragment = processor.process(candidate)
                        duration = int((time.time() - start_time) * 1000)
                        
                        if fragment:
                            processed_fragments.append(fragment)
                            print(f"✅ ({len(fragment)}字, {duration}ms)")
                            
                            if enable_trace:
                                self.trace_logger.log_module_end(trace_id, proc_name, 
                                                                  {'output_length': len(fragment)}, 
                                                                  duration)
                        else:
                            print(f"⚠️ 无输出")
                            if enable_trace:
                                self.trace_logger.log(trace_id, proc_name, 'WARNING', 
                                                      '处理器无输出')
                    except Exception as e:
                        duration = int((time.time() - start_time) * 1000)
                        print(f"❌ {e}")
                        if enable_trace:
                            self.trace_logger.log(trace_id, proc_name, 'ERROR', 
                                                  f'处理器异常: {str(e)}')
            
            # 阶段3: 内容合成
            print(f"   ✍️ 合成内容...", end=' ')
            try:
                if processed_fragments and self.output_module:
                    final_content = self.output_module.compose(
                        candidate=candidate,
                        fragments=processed_fragments
                    )
                elif 'arxiv_id' in candidate:
                    # arXiv 专用处理
                    from modules.output.arxiv_composer import ArxivContentComposer
                    composer = ArxivContentComposer()
                    final_content = composer.compose_narrative(candidate)
                else:
                    # 通用处理
                    final_content = self._generic_compose(candidate)
                
                # 添加追踪ID到内容底部
                final_content_with_id = self._add_trace_id(final_content, trace_id)
                
                if enable_trace:
                    self.trace_logger.log_composition(trace_id, 'narrative_composer', 
                                                      len(final_content))
                    self.trace_logger.set_final_output(trace_id, final_content)
                
                print(f"✅ ({len(final_content)}字)")
                
                results.append({
                    'name': candidate.get('name', ''),
                    'source': candidate.get('source_name', ''),
                    'content': final_content_with_id,
                    'raw_content': final_content,
                    'url': candidate.get('url', ''),
                    'trace_id': trace_id,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ {e}")
                if enable_trace:
                    self.trace_logger.log(trace_id, 'composition', 'ERROR', 
                                          f'合成失败: {str(e)}')
        
        return results
    
    def _generic_compose(self, candidate: Dict) -> str:
        """通用内容合成"""
        lines = [
            f"**{candidate.get('name', '')}**",
            "",
            f"📌 来源: {candidate.get('source_name', 'Unknown')}",
            "",
            candidate.get('description', '')[:400],
            "",
            f"🔗 {candidate.get('url', '')}"
        ]
        return '\n'.join(lines)
    
    def _add_trace_id(self, content: str, trace_id: str) -> str:
        """
        在内容底部添加追踪ID
        
        格式:
        ---
        🆔 追踪ID: AIT-20260203-XXXXXX
        💡 如发现内容问题，请将此ID发送给管理员进行诊断
        """
        footer = f"\n\n---\n🆔 **追踪ID**: `{trace_id}`\n💡 如发现内容问题，请发送此ID进行诊断"
        return content + footer
    
    def publish(self, contents: List[Dict]):
        """发布内容，记录发布日志"""
        if not contents:
            print("\n⚠️ 无内容需要发布")
            return
        
        print("\n" + "="*60)
        print("阶段3: 内容发布")
        print("="*60)
        
        for pub_name, pub_config in self.config.get('publishers', {}).items():
            if not pub_config.get('enabled', False):
                continue
            
            try:
                print(f"\n📤 {pub_name}...")
                
                if pub_name == 'forum':
                    self._publish_to_forum(contents, pub_config)
                elif pub_name == 'text':
                    self._publish_to_text(contents, pub_config)
                else:
                    print(f"  ⚠️ 未知渠道: {pub_name}")
                
            except Exception as e:
                print(f"  ❌ 失败: {e}")
    
    def _publish_to_forum(self, contents: List[Dict], config: Dict):
        """发布到论坛"""
        from publishers import create_publisher
        
        try:
            publisher = create_publisher('forum', config)
            
            forums_contents = []
            for c in contents:
                forums_contents.append({
                    'name': c['name'],
                    'content': c['content'],  # 包含追踪ID
                    'url': c['url'],
                    'source': c['source']
                })
            
            published = publisher.publish_batch(forums_contents)
            print(f"  ✅ {published}/{len(contents)} 条成功")
            
            # 记录发布日志
            for c in contents:
                trace_id = c.get('trace_id', '')
                if trace_id:
                    self.trace_logger.log_publish(trace_id, 'forum_publisher', 
                                                  published > 0)
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            for c in contents:
                if c.get('trace_id'):
                    self.trace_logger.log_publish(c['trace_id'], 'forum_publisher', 
                                                  False, str(e))
    
    def _publish_to_text(self, contents: List[Dict], config: Dict):
        """发布到文字频道"""
        from publishers import create_publisher
        
        try:
            publisher = create_publisher('text', config)
            
            text_contents = []
            for c in contents:
                text_contents.append({
                    'name': c['name'],
                    'content': c['content'],
                    'url': c['url'],
                    'source': c['source']
                })
            
            published = publisher.publish_batch(text_contents)
            print(f"  ✅ {published}/{len(contents)} 条成功")
            
            for c in contents:
                if c.get('trace_id'):
                    self.trace_logger.log_publish(c['trace_id'], 'text_publisher', 
                                                  published > 0)
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")


def diagnose(trace_id: str) -> str:
    """
    诊断命令 - 根据追踪ID生成诊断报告
    
    用法: python3 launcher.py --diagnose AIT-20260203-XXXXXX
    """
    logger = get_trace_logger()
    return logger.diagnose(trace_id)


def load_env():
    """加载环境变量"""
    import os
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value


def main():
    """主入口"""
    import sys
    
    # 检查诊断命令
    if len(sys.argv) > 1 and sys.argv[1] == '--diagnose':
        if len(sys.argv) > 2:
            trace_id = sys.argv[2]
            print(diagnose(trace_id))
            return
        else:
            print("用法: python3 launcher.py --diagnose <追踪ID>")
            print("示例: python3 launcher.py --diagnose AIT-20260203-A1B2C3")
            return
    
    print("="*60)
    print("🎯 AiTrend 模块化系统 v3 (支持追踪日志)")
    print("="*60)
    
    load_env()
    
    launcher = Launcher()
    launcher.init_modules()
    
    results = launcher.run_pipeline()
    launcher.publish(results)
    
    print("\n" + "="*60)
    print(f"✅ 完成: {len(results)} 条内容")
    print(f"📁 追踪日志: logs/traces/")
    print(f"🔍 诊断命令: python3 launcher.py --diagnose <追踪ID>")
    print("="*60)


if __name__ == '__main__':
    main()
