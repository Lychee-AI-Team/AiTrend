"""
环境变量加载器 - 纯标准库版本
读取 .env 文件并加载到环境变量
"""
import os
from pathlib import Path

def load_env_file(env_path: str = None) -> dict:
    """
    加载 .env 文件
    纯标准库实现，无需 python-dotenv
    """
    if env_path is None:
        base_dir = Path(__file__).parent.parent
        env_path = base_dir / ".env"
    
    env_vars = {}
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 去除可能的引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                    # 同时设置到环境变量
                    os.environ[key] = value
        
        return env_vars
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"警告: 加载 .env 文件失败: {e}")
        return {}

def get_env(key: str, default: str = None) -> str:
    """获取环境变量"""
    return os.environ.get(key, default)
