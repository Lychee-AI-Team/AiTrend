"""
配置加载器
支持从 config.json 和 config.yaml 加载配置
"""
import json
import os
from typing import Dict, Any

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.json')

def load_config(config_path: str = None) -> Dict[str, Any]:
    """加载配置文件"""
    config_path = config_path or DEFAULT_CONFIG_PATH
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 解析环境变量占位符
    config = _resolve_env_vars(config)
    
    return config

def _resolve_env_vars(obj: Any) -> Any:
    """递归解析 ${ENV_VAR} 格式的环境变量"""
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        env_var = obj[2:-1]
        return os.getenv(env_var, '')
    return obj

def get_channel_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """获取渠道配置"""
    return config.get('channels', {'console': {'enabled': True}})

def get_enabled_channels(config: Dict[str, Any]) -> Dict[str, Any]:
    """获取启用的渠道"""
    channels = get_channel_config(config)
    return {name: cfg for name, cfg in channels.items() if cfg.get('enabled', False)}
