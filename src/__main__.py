"""
AiTrend Skill 主入口 - 纯标准库版本
"""
import json
import logging
import os
from pathlib import Path

# 先加载环境变量
from src.utils import load_env_file
from pathlib import Path
env_path = Path(__file__).parent.parent / ".env"
load_env_file(str(env_path))

from src.core.collector import TrendCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def resolve_env_vars(obj):
    """递归解析配置中的环境变量引用 ${VAR}"""
    if isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        import re
        # 匹配 ${VAR} 格式
        pattern = r'\$\{([^}]+)\}'
        def replace_var(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))
        return re.sub(pattern, replace_var, obj)
    else:
        return obj

def load_config(config_path: str = None) -> dict:
    """加载配置文件（JSON 格式，纯标准库）"""
    if config_path is None:
        base_dir = Path(__file__).parent.parent
        config_path = base_dir / "config" / "config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 解析环境变量
            return resolve_env_vars(config)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {config_path}")
        return get_default_config()
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return get_default_config()

def get_default_config() -> dict:
    """获取默认配置"""
    return {
        "sources": {
            "github_trending": {
                "enabled": True,
                "languages": ["python"],
                "min_stars": 50
            }
        },
        "summarizer": {
            "enabled": False
        },
        "channels": {
            "console": {
                "enabled": True
            }
        },
        "advanced": {
            "validation": {
                "enabled": True,
                "auto_fix": True
            },
            "max_retries": 3
        }
    }

def main():
    """主函数"""
    logger.info("🦞 AiTrend Skill v0.1.0 (纯标准库) 启动")
    
    # 加载配置
    config = load_config()
    
    # 创建收集器并运行
    collector = TrendCollector(config)
    success, result = collector.run()
    
    if success:
        logger.info("✅ 任务完成")
        return result
    else:
        logger.error(f"❌ 任务失败: {result}")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(result)
