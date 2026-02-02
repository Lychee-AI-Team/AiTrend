#!/usr/bin/env python3
"""
AiTrend 启动中枢（完整版）
模块化设计，支持发布模块自由切换
"""

import os
import sys
import yaml
from datetime import datetime
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from modules.logger import get_logger
from publishers import create_publisher

logger = get_logger()

class Launcher:
    """启动中枢 - 支持模块化发布切换"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.publisher = None
        
    def _load_config(self, path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"❌ 配置文件不存在: {path}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            'sources': {
                'github_trend': {
                    'enabled': True,
                    'languages': ['python', 'javascript', 'go'],
                    'max_candidates': 5,
                    'growth_threshold': 0.3
                }
            },
            'publishers': {
                'forum': {'enabled': True},   # 默认使用论坛
                'text': {'enabled': False}     # 文字频道禁用
            }
        }
    
    def init_publisher(self) -> bool:
        """
        初始化发布模块
        根据配置自动选择并创建发布模块
        """
        logger.section("🚀 初始化发布模块")
        
        pub_config = self.config.get('publishers', {})
        
        # 优先检查论坛发布
        if pub_config.get('forum', {}).get('enabled', False):
            logger.info("选择发布模块: ForumPublisher (Discord论坛)")
            self.publisher = create_publisher('forum', pub_config.get('forum', {}))
            if self.publisher:
                return True
        
        # 其次检查文字频道发布
        if pub_config.get('text', {}).get('enabled', False):
            logger.info("选择发布模块: TextPublisher (Discord文字频道)")
            self.publisher = create_publisher('text', pub_config.get('text', {}))
            if self.publisher:
                return True
        
        logger.error("❌ 没有启用的发布模块，请检查 config.yaml")
        logger.info("提示: 在 config.yaml 中设置 publishers.forum.enabled: true 或 publishers.text.enabled: true")
        return False
    
    def fetch_candidates(self) -> List[Dict]:
        """获取候选项目"""
        logger.section("📡 从GitHub Trend挖掘项目")
        
        from modules.sources.github_trend import GithubTrend
        
        source_config = self.config.get('sources', {}).get('github_trend', {})
        
        if not source_config.get('enabled', False):
            logger.warning("⚠️ GitHub Trend 源未启用")
            return []
        
        source = GithubTrend(source_config)
        candidates = source.discover()
        
        for c in candidates:
            c['source_name'] = 'github_trend'
        
        logger.info(f"✅ 发现 {len(candidates)} 个候选项目")
        return candidates
    
    def run(self):
        """运行完整流程"""
        logger.section("🎯 AiTrend 启动")
        logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 初始化发布模块
        if not self.init_publisher():
            logger.error("❌ 启动失败: 发布模块初始化失败")
            return
        
        # 2. 获取候选项目
        candidates = self.fetch_candidates()
        
        if not candidates:
            logger.warning("⚠️ 未发现候选项目，流程结束")
            return
        
        # 3. 生成内容（示例：使用预设内容）
        logger.section("📝 准备发布内容")
        
        # 这里可以从LLM获取，现在使用测试内容
        test_contents = [
            {
                'name': 'nanobot',
                'content': 'nanobot 是一个超轻量级的个人 AI 助手...',
                'url': 'https://github.com/HKUDS/nanobot',
                'source': 'GitHub'
            }
        ]
        
        # 4. 发布
        published = self.publisher.publish_batch(test_contents)
        
        # 5. 完成
        logger.section("✅ 流程完成")
        logger.info(f"发布结果: {published}/{len(test_contents)} 条成功")
        logger.info(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主入口"""
    launcher = Launcher()
    launcher.run()

if __name__ == '__main__':
    main()
