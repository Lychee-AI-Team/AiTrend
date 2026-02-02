"""
AiTrend 智能启动中枢 v4

支持多种触发机制：
1. 命令行参数触发
2. 定时任务触发
3. 手动指定平台和数量
4. 智能补全机制（确保每个平台至少3条）
"""

import yaml
import json
import importlib
import time
import argparse
import sys
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from modules.trace_logger import TraceLogger, get_trace_logger

# 信息源模块映射表
SOURCE_MAP = {
    'github_trend': ('modules.sources.github_trend', 'GithubTrend'),
    'producthunt': ('modules.sources.producthunt', 'Producthunt'),
    'hackernews': ('modules.sources.hackernews', 'Hackernews'),
    'reddit': ('modules.sources.reddit', 'Reddit'),
    'arxiv_papers': ('modules.sources.arxiv_papers', 'ArxivPapers'),
    'twitter': ('modules.sources.twitter', 'TwitterSource'),
}

# 平台名称映射
PLATFORM_NAMES = {
    'github': 'github_trend',
    'github_trend': 'github_trend',
    'producthunt': 'producthunt',
    'ph': 'producthunt',
    'hackernews': 'hackernews',
    'hn': 'hackernews',
    'reddit': 'reddit',
    'arxiv': 'arxiv_papers',
    'twitter': 'twitter',
    'x': 'twitter',
}


class Launcher:
    """智能启动中枢 - 支持多种触发机制"""
    
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
            return self._default_config()
        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'sources': {k: {'enabled': True} for k in SOURCE_MAP.keys()},
            'processors': {},
            'output': {'style': 'natural_narrative'},
            'publishers': {'forum': {'enabled': True}},
            'system': {'max_iterations': 10, 'enable_trace': True}
        }
    
    def init_modules(self, specific_sources: List[str] = None):
        """初始化模块（可指定特定源）"""
        print("🚀 启动中枢初始化...")
        
        sources_to_init = specific_sources or list(self.config.get('sources', {}).keys())
        
        # 初始化信息源
        print("\n📡 初始化信息源模块...")
        for source_name in sources_to_init:
            source_config = self.config.get('sources', {}).get(source_name, {})
            if not source_config.get('enabled', False):
                continue
                
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
        
        # 初始化输出模块
        print("\n✍️ 初始化输出模块...")
        try:
            from modules.output.narrative_composer import NarrativeComposer
            self.output_module = NarrativeComposer(self.config.get('output', {}))
            print(f"  ✅ narrative_composer")
        except Exception as e:
            print(f"  ⚠️ {e}")
        
        print(f"\n📊 模块加载: {len(self.sources)} 个源")
    
    def ensure_minimum_content(self, min_per_source: int = 3) -> List[Dict]:
        """
        确保每个平台至少获取指定数量的内容
        
        Args:
            min_per_source: 每个源的最小内容数，默认3
        
        Returns:
            所有内容列表
        """
        all_candidates = []
        enable_trace = self.config.get('system', {}).get('enable_trace', True)
        
        print("\n" + "="*60)
        print(f"智能内容采集 (每源至少{min_per_source}条)")
        print("="*60)
        
        for source in self.sources:
            try:
                source_name = getattr(source, 'name', source.__class__.__name__)
                print(f"\n📡 {source_name} 挖掘...")
                
                candidates = []
                attempts = 0
                max_attempts = 3
                
                # 尝试多次获取足够内容
                while len(candidates) < min_per_source and attempts < max_attempts:
                    attempts += 1
                    
                    # 动态调整配置以获取更多内容
                    if hasattr(source, 'config'):
                        original_max = source.config.get('max_results', 10)
                        # 临时增加获取数量
                        source.config['max_results'] = min_per_source * 3
                    
                    new_candidates = source.discover()
                    
                    # 恢复原始配置
                    if hasattr(source, 'config') and 'max_results' in source.config:
                        source.config['max_results'] = original_max
                    
                    # 过滤已存在的
                    existing_ids = {c.get('url', '') for c in candidates}
                    for c in new_candidates:
                        if c.get('url', '') not in existing_ids:
                            c['source_name'] = source_name
                            if enable_trace:
                                c['trace_id'] = self.trace_logger.generate_trace_id(c)
                                self.trace_logger.create_trace(c['trace_id'], c)
                                self.trace_logger.log_source_discover(
                                    c['trace_id'], source_name, len(new_candidates)
                                )
                            candidates.append(c)
                            existing_ids.add(c.get('url', ''))
                    
                    if len(candidates) < min_per_source:
                        print(f"  ⚠️ 第{attempts}次获取: {len(candidates)}/{min_per_source} 条")
                        time.sleep(1)
                    else:
                        break
                
                # 如果还是不够，记录警告但仍然使用
                if len(candidates) < min_per_source:
                    print(f"  ⚠️ 最终获取: {len(candidates)}/{min_per_source} 条 (不足)")
                else:
                    print(f"  ✅ 获取 {len(candidates)} 条 (满足要求)")
                
                all_candidates.extend(candidates[:max(min_per_source * 2, len(candidates))])
                
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        print(f"\n📊 总计: {len(all_candidates)} 条内容")
        return all_candidates
    
    def process_content(self, candidates: List[Dict], max_total: int = None) -> List[Dict]:
        """处理内容（生成中文介绍）- 确保每个平台都有内容"""
        results = []
        enable_trace = self.config.get('system', {}).get('enable_trace', True)
        
        # 按平台分组，确保每个平台都有内容被处理
        source_groups = {}
        for c in candidates:
            src = c.get('source_name', 'Unknown')
            if src not in source_groups:
                source_groups[src] = []
            source_groups[src].append(c)
        
        # 计算每个平台的最大数量
        num_sources = len(source_groups)
        if max_total and num_sources > 0:
            per_source = max_total // num_sources
            # 从每个平台取相同数量
            balanced_candidates = []
            for src, items in source_groups.items():
                balanced_candidates.extend(items[:per_source])
            candidates = balanced_candidates
            print(f"   平衡分配: {num_sources}个平台, 每平台最多{per_source}条")
        
        print(f"   待处理: {len(candidates)} 条内容")
        
        print("\n" + "="*60)
        print("内容处理与生成")
        print("="*60)
        
        for i, candidate in enumerate(candidates, 1):
            trace_id = candidate.get('trace_id', 'unknown')
            name = candidate.get('name', 'Unknown')[:40]
            source = candidate.get('source_name', 'Unknown')
            
            print(f"\n[{i}/{len(candidates)}] {source}: {name}")
            print(f"   Trace: {trace_id}")
            
            try:
                # Twitter质量筛选
                if source == 'Twitter' and candidate.get('meets_data_threshold'):
                    from modules.processors.twitter_quality_filter import TwitterQualityFilter
                    filter_proc = TwitterQualityFilter()
                    filtered = filter_proc.process(candidate)
                    if not filtered:
                        print(f"   ❌ 未通过质量筛选")
                        continue
                    candidate = filtered
                
                # 生成内容 - 使用LLM生成中文总结
                if 'arxiv_id' in candidate:
                    # arXiv论文使用专用composer
                    from modules.output.arxiv_composer import ArxivContentComposer
                    composer = ArxivContentComposer()
                    final_content = composer.compose_narrative(candidate)
                elif source == 'Twitter':
                    # Twitter使用专用composer
                    from modules.output.twitter_composer import TwitterContentComposer
                    composer = TwitterContentComposer()
                    final_content = composer.compose_narrative(candidate)
                else:
                    # GitHub/PH/HN/Reddit等使用LLM生成中文总结
                    final_content = self._generate_chinese_summary(candidate)
                
                # 添加trace_id
                final_content_with_id = self._add_trace_id(final_content, trace_id)
                
                if enable_trace:
                    self.trace_logger.set_final_output(trace_id, final_content)
                
                print(f"   ✅ 生成完成 ({len(final_content)}字)")
                
                results.append({
                    'name': candidate.get('name', ''),
                    'source': source,
                    'content': final_content_with_id,
                    'raw_content': final_content,
                    'url': candidate.get('url', ''),
                    'trace_id': trace_id,
                })
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        return results
    
    def publish(self, contents: List[Dict]):
        """发布内容"""
        if not contents:
            print("\n⚠️ 无内容需要发布")
            return
        
        print("\n" + "="*60)
        print("内容发布")
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
                    
            except Exception as e:
                print(f"  ❌ {e}")
    
    def _publish_to_forum(self, contents: List[Dict], config: Dict):
        """发布到论坛"""
        from publishers import create_publisher
        
        try:
            publisher = create_publisher('forum', config)
            
            forums_contents = []
            for c in contents:
                forums_contents.append({
                    'name': c['name'],
                    'content': c['content'],
                    'url': c['url'],
                    'source': c['source']
                })
            
            published = publisher.publish_batch(forums_contents)
            print(f"  ✅ {published}/{len(contents)} 条成功")
            
            for c in contents:
                if c.get('trace_id'):
                    self.trace_logger.log_publish(
                        c['trace_id'], 'forum_publisher', published > 0
                    )
            
        except Exception as e:
            print(f"  ❌ {e}")
    
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
            
        except Exception as e:
            print(f"  ❌ {e}")
    
    def _generate_chinese_summary(self, candidate: Dict) -> str:
        """
        使用LLM生成中文内容总结
        
        针对GitHub/PH/HN/Reddit等平台生成中文介绍
        """
        import os
        import requests
        
        source = candidate.get('source_name', 'Unknown')
        name = candidate.get('name', '')
        description = candidate.get('description', '')
        url = candidate.get('url', '')
        
        # 检查是否有API Key (支持Gemini/OpenAI/Kimi)
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('KIMI_API_KEY')
        
        if not api_key:
            raise RuntimeError(f"未配置LLM API Key (GEMINI_API_KEY/OPENAI_API_KEY/KIMI_API_KEY)，无法生成内容: {source}/{name}")
        
        # 构建提示词
        system_prompt = """你是技术内容编辑，擅长用自然的中文介绍开源项目。
要求：
1. 用连续段落叙述，不要列表、序号
2. 说明项目是什么、能做什么、为什么值得关注
3. 突出最特别的功能或亮点
4. 300字以内，口语化表达
5. 不要"最近"、"刚刚"等时间词"""

        user_prompt = f"请介绍以下{source}项目：\n\n项目名称：{name}\n\n项目描述：{description[:1000]}"

        print(f"   🤖 LLM生成中文总结...", end=' ')
        
        try:
            # 使用项目中已有的llm_client模块
            print(f"   🤖 使用OpenClaw大模型生成...", end=' ')
            
            from modules.llm_client import LLMClient
            import time
            
            client = LLMClient()
            
            # 添加延迟避免API速率限制
            time.sleep(1)
            
            chinese_content = client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=800
            )
            
            if not chinese_content or len(chinese_content) <= 50:
                raise RuntimeError(f"LLM生成内容失败或内容太短: {source}/{name}")
            
            # 确保包含链接
            if url not in chinese_content:
                chinese_content += f"\n\n🔗 {url}"
            print("✅")
            return chinese_content
                
        except Exception as e:
            # LLM调用失败，立即报错退出
            raise RuntimeError(f"LLM调用失败，无法生成内容: {source}/{name}. 错误: {e}") from e
    
    def _fallback_compose(self, candidate: Dict) -> str:
        """备用内容合成（当LLM失败时使用）- 生成中文描述"""
        import re
        
        name = candidate.get('name', '')
        source = candidate.get('source_name', 'Unknown')
        url = candidate.get('url', '')
        description = candidate.get('description', '') or candidate.get('title', '')
        
        # 从英文描述中提取关键信息
        # 清理描述
        desc_clean = re.sub(r'http\S+', '', description)  # 移除链接
        desc_clean = re.sub(r'[#*`]', '', desc_clean)     # 移除markdown
        desc_clean = desc_clean.strip()
        
        # 提取关键词
        keywords = []
        tech_keywords = ['AI', 'ML', 'LLM', 'GPT', 'API', 'tool', 'framework', 'library']
        for kw in tech_keywords:
            if kw.lower() in desc_clean.lower():
                keywords.append(kw)
        
        # 构建中文描述
        parts = [f"**{name}**"]
        parts.append("")
        
        # 根据来源生成不同的描述
        if 'github' in source.lower():
            parts.append(f"这是一个GitHub上的开源项目。{desc_clean[:150]}..." if len(desc_clean) > 150 else f"这是一个GitHub上的开源项目。{desc_clean}")
            if keywords:
                parts.append(f"项目涉及{ '、'.join(keywords[:3]) }等技术。")
            parts.append("适合开发者关注和学习。")
        elif 'producthunt' in source.lower():
            parts.append(f"这是一个Product Hunt上的新产品。{desc_clean[:150]}..." if len(desc_clean) > 150 else f"这是一个Product Hunt上的新产品。{desc_clean}")
            parts.append("值得关注其产品设计和用户反馈。")
        elif 'hackernews' in source.lower() or 'hn' in source.lower():
            parts.append(f"这是HackerNews上的热门讨论。{desc_clean[:150]}..." if len(desc_clean) > 150 else f"这是HackerNews上的热门讨论。{desc_clean}")
            parts.append("技术社区正在关注这个话题。")
        elif 'reddit' in source.lower():
            parts.append(f"这是Reddit上的热门帖子。{desc_clean[:150]}..." if len(desc_clean) > 150 else f"这是Reddit上的热门帖子。{desc_clean}")
            parts.append("社区用户正在讨论这个内容。")
        else:
            parts.append(f"这是来自{source}的内容。{desc_clean[:150]}..." if len(desc_clean) > 150 else f"这是来自{source}的内容。{desc_clean}")
        
        parts.append("")
        parts.append(f"🔗 {url}")
        
        return '\n'.join(parts)
    
    def _generic_compose(self, candidate: Dict) -> str:
        """通用内容合成（已弃用，保留兼容）"""
        return self._generate_chinese_summary(candidate)
    
    def _add_trace_id(self, content: str, trace_id: str) -> str:
        """添加追踪ID"""
        footer = f"\n\n{trace_id}"
        return content + footer


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='AiTrend 智能启动中枢',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 launcher.py                    # 运行所有源，每源至少3条
  python3 launcher.py --source github    # 只运行GitHub
  python3 launcher.py --source twitter --min 5   # Twitter至少5条
  python3 launcher.py --all --min 3      # 所有源，每源3条
  python3 launcher.py --diagnose AIT-xxx # 诊断指定ID
        '''
    )
    
    parser.add_argument('--source', '-s', action='append',
                       help='指定信息源（可多次使用，如: github twitter）')
    parser.add_argument('--min', '-m', type=int, default=3,
                       help='每源最小内容数（默认3）')
    parser.add_argument('--max-total', type=int,
                       help='总内容数上限')
    parser.add_argument('--all', action='store_true',
                       help='启用所有配置的源')
    parser.add_argument('--diagnose', metavar='TRACE_ID',
                       help='诊断指定追踪ID')
    parser.add_argument('--recent', action='store_true',
                       help='列出最近的追踪记录')
    parser.add_argument('--dry-run', action='store_true',
                       help='试运行（不发布）')
    
    return parser.parse_args()


def main():
    """主入口"""
    args = parse_args()
    
    # 诊断模式
    if args.diagnose:
        print(get_trace_logger().diagnose(args.diagnose))
        return
    
    # 最近记录模式
    if args.recent:
        traces = get_trace_logger().list_recent(20)
        print("📋 最近的追踪记录:\n")
        print(f"{'追踪ID':<30} {'信息源':<12} {'状态':<8} {'名称':<40}")
        print("-" * 95)
        for t in traces:
            status_icon = "✅" if t['status'] == 'completed' else "❌" if t['status'] == 'error' else "⏳"
            name = t['name'][:38] if len(t['name']) > 38 else t['name']
            print(f"{t['trace_id']:<30} {t['source']:<12} {status_icon} {t['status']:<6} {name}")
        return
    
    print("="*60)
    print("🎯 AiTrend 智能启动中枢 v4")
    print("="*60)
    
    # 确定要运行的源
    sources_to_run = None
    if args.source:
        # 解析平台名称别名
        sources_to_run = []
        for s in args.source:
            normalized = PLATFORM_NAMES.get(s.lower(), s)
            if normalized in SOURCE_MAP:
                sources_to_run.append(normalized)
            else:
                print(f"⚠️ 未知平台: {s}")
    
    # 加载环境变量
    load_env()
    
    # 创建启动器
    launcher = Launcher()
    launcher.init_modules(sources_to_run)
    
    if not launcher.sources:
        print("\n❌ 没有可用的信息源")
        return
    
    # 确保每个平台至少获取指定数量
    candidates = launcher.ensure_minimum_content(min_per_source=args.min)
    
    if not candidates:
        print("\n❌ 未获取到任何内容")
        return
    
    # 处理内容
    results = launcher.process_content(candidates, max_total=args.max_total)
    
    if not results:
        print("\n❌ 未生成任何内容")
        return
    
    # 发布（如果不是dry-run）
    if not args.dry_run:
        launcher.publish(results)
    else:
        print("\n📝 Dry-run模式，跳过发布")
        print(f"   将发布 {len(results)} 条内容")
    
    # 统计
    print("\n" + "="*60)
    print("📊 执行统计")
    print("="*60)
    
    source_counts = {}
    for r in results:
        src = r['source']
        source_counts[src] = source_counts.get(src, 0) + 1
    
    print("\n各平台发布数量:")
    for src, count in sorted(source_counts.items()):
        status = "✅" if count >= args.min else "⚠️"
        print(f"  {status} {src}: {count} 条")
    
    print(f"\n总计: {len(results)} 条内容")
    print("="*60)


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
        print("✅ 环境变量已加载")


if __name__ == '__main__':
    main()
