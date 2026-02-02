"""
诊断日志追踪系统

功能：
- 为每个信息生成唯一追踪ID
- 记录各模块处理日志
- 支持按ID回溯查询
- 日志持久化存储
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    module: str
    level: str  # DEBUG, INFO, WARNING, ERROR
    message: str
    data: Optional[Dict[str, Any]] = None


class TraceLogger:
    """
    追踪日志器
    
    为每个信息生成唯一追踪ID，记录全流程日志
    """
    
    def __init__(self, log_dir: str = "logs/traces"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
    def generate_trace_id(self, content: Dict[str, Any]) -> str:
        """
        生成追踪ID
        
        基于内容生成确定性ID，同时保证唯一性
        格式: AIT-YYYYMMDD-XXXXXX-RAND
        """
        # 清理内容，移除不可序列化的对象
        clean_content = {}
        for key, value in content.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                clean_content[key] = value
            elif hasattr(value, 'isoformat'):  # datetime
                clean_content[key] = value.isoformat()
            else:
                clean_content[key] = str(value)
        
        # 基于内容生成哈希
        content_str = json.dumps(clean_content, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.md5(content_str.encode())
        short_hash = hash_obj.hexdigest()[:6].upper()
        
        # 日期前缀
        date_prefix = datetime.now().strftime("%Y%m%d")
        
        # 添加随机后缀确保唯一性（避免内容相似导致ID冲突）
        import random
        rand_suffix = ''.join(random.choices('0123456789ABCDEF', k=4))
        
        return f"AIT-{date_prefix}-{short_hash}-{rand_suffix}"
    
    def create_trace(self, trace_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新的追踪记录
        
        Args:
            trace_id: 追踪ID
            initial_data: 初始数据（如原始信息）
            
        Returns:
            追踪记录结构
        """
        trace = {
            'trace_id': trace_id,
            'created_at': datetime.now().isoformat(),
            'status': 'started',
            'source': initial_data.get('source', 'unknown'),
            'name': initial_data.get('name', 'unknown'),
            'url': initial_data.get('url', ''),
            'logs': [],
            'modules': {},
            'final_output': None,
            'errors': []
        }
        
        self._save_trace(trace_id, trace)
        return trace
    
    def log(self, trace_id: str, module: str, level: str, message: str, data: Optional[Dict] = None):
        """
        记录日志
        
        Args:
            trace_id: 追踪ID
            module: 模块名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            message: 日志消息
            data: 附加数据
        """
        with self._lock:
            trace = self._load_trace(trace_id)
            if not trace:
                return
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'module': module,
                'level': level,
                'message': message,
                'data': data or {}
            }
            
            trace['logs'].append(entry)
            
            # 如果是错误，单独记录
            if level == 'ERROR':
                trace['errors'].append(entry)
                trace['status'] = 'error'
            
            # 更新模块状态
            if module not in trace['modules']:
                trace['modules'][module] = {
                    'started_at': entry['timestamp'],
                    'status': 'running',
                    'log_count': 0
                }
            
            trace['modules'][module]['log_count'] += 1
            if level == 'ERROR':
                trace['modules'][module]['status'] = 'error'
            elif level != 'DEBUG':
                trace['modules'][module]['status'] = 'success'
            
            self._save_trace(trace_id, trace)
    
    def log_module_start(self, trace_id: str, module: str, input_data: Dict):
        """记录模块开始"""
        self.log(trace_id, module, 'INFO', f'模块 {module} 开始处理', {
            'input_summary': str(input_data)[:200]
        })
    
    def log_module_end(self, trace_id: str, module: str, output_data: Dict, duration_ms: int):
        """记录模块结束"""
        self.log(trace_id, module, 'INFO', f'模块 {module} 处理完成', {
            'output_summary': str(output_data)[:200],
            'duration_ms': duration_ms
        })
    
    def log_source_discover(self, trace_id: str, source: str, count: int):
        """记录信息源发现"""
        self.log(trace_id, 'source', 'INFO', f'信息源 {source} 发现 {count} 条候选', {
            'source': source,
            'count': count
        })
    
    def log_processor(self, trace_id: str, processor: str, input_len: int, output_len: int):
        """记录处理器执行"""
        self.log(trace_id, processor, 'INFO', f'处理器 {processor} 完成', {
            'input_length': input_len,
            'output_length': output_len
        })
    
    def log_composition(self, trace_id: str, composer: str, final_length: int):
        """记录内容合成"""
        self.log(trace_id, composer, 'INFO', '内容合成完成', {
            'final_length': final_length
        })
    
    def log_publish(self, trace_id: str, publisher: str, success: bool, response: str = ''):
        """记录发布"""
        level = 'INFO' if success else 'ERROR'
        self.log(trace_id, publisher, level, f'发布{"成功" if success else "失败"}', {
            'success': success,
            'response': response[:500] if response else ''
        })
        
        # 更新整体状态
        trace = self._load_trace(trace_id)
        if trace:
            trace['status'] = 'completed' if success else 'failed'
            self._save_trace(trace_id, trace)
    
    def set_final_output(self, trace_id: str, output: str):
        """设置最终输出"""
        trace = self._load_trace(trace_id)
        if trace:
            trace['final_output'] = output[:1000]  # 限制存储大小
            trace['status'] = 'completed'
            self._save_trace(trace_id, trace)
    
    def get_trace(self, trace_id: str) -> Optional[Dict]:
        """获取完整追踪记录"""
        return self._load_trace(trace_id)
    
    def diagnose(self, trace_id: str) -> str:
        """
        诊断报告
        
        生成可读的诊断信息
        """
        trace = self._load_trace(trace_id)
        if not trace:
            return f"❌ 未找到追踪ID: {trace_id}"
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"🔍 诊断报告: {trace_id}")
        lines.append("=" * 60)
        lines.append("")
        
        # 基本信息
        lines.append(f"📋 基本信息:")
        lines.append(f"  信息名称: {trace['name']}")
        lines.append(f"  信息源: {trace['source']}")
        lines.append(f"  创建时间: {trace['created_at']}")
        lines.append(f"  当前状态: {trace['status']}")
        lines.append("")
        
        # 模块执行情况
        lines.append(f"🔧 模块执行 ({len(trace['modules'])} 个):")
        for module, info in trace['modules'].items():
            status_icon = "✅" if info['status'] == 'success' else "❌" if info['status'] == 'error' else "⏳"
            lines.append(f"  {status_icon} {module}: {info['status']} ({info['log_count']} 条日志)")
        lines.append("")
        
        # 错误信息
        if trace['errors']:
            lines.append(f"❌ 错误 ({len(trace['errors'])} 个):")
            for error in trace['errors'][:5]:  # 最多显示5个
                lines.append(f"  [{error['module']}] {error['message']}")
                if error.get('data'):
                    lines.append(f"    数据: {str(error['data'])[:100]}")
            lines.append("")
        
        # 关键日志
        lines.append(f"📝 关键日志:")
        important_logs = [log for log in trace['logs'] if log['level'] in ['INFO', 'ERROR']]
        for log in important_logs[-10:]:  # 最近10条
            time_short = log['timestamp'].split('T')[1][:8] if 'T' in log['timestamp'] else log['timestamp'][-8:]
            icon = "🔴" if log['level'] == 'ERROR' else "🟢"
            lines.append(f"  {icon} [{time_short}] {log['module']}: {log['message'][:60]}")
        lines.append("")
        
        # 原始链接
        lines.append(f"🔗 原始链接: {trace['url']}")
        lines.append("")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def _get_trace_path(self, trace_id: str) -> Path:
        """获取追踪文件路径"""
        # 按日期分目录
        date_str = trace_id.split('-')[1] if '-' in trace_id else 'unknown'
        dir_path = self.log_dir / date_str
        dir_path.mkdir(exist_ok=True)
        return dir_path / f"{trace_id}.json"
    
    def _save_trace(self, trace_id: str, trace: Dict):
        """保存追踪记录"""
        try:
            path = self._get_trace_path(trace_id)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(trace, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存追踪记录失败: {e}")
    
    def _load_trace(self, trace_id: str) -> Optional[Dict]:
        """加载追踪记录"""
        try:
            path = self._get_trace_path(trace_id)
            if not path.exists():
                return None
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载追踪记录失败: {e}")
            return None
    
    def list_recent(self, limit: int = 10) -> List[Dict]:
        """列出最近的追踪记录"""
        traces = []
        
        # 遍历所有日期目录
        for date_dir in sorted(self.log_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            
            for trace_file in sorted(date_dir.iterdir(), reverse=True):
                if trace_file.suffix == '.json':
                    try:
                        with open(trace_file, 'r', encoding='utf-8') as f:
                            trace = json.load(f)
                            traces.append({
                                'trace_id': trace['trace_id'],
                                'name': trace['name'][:50],
                                'source': trace['source'],
                                'status': trace['status'],
                                'created_at': trace['created_at']
                            })
                            
                            if len(traces) >= limit:
                                return traces
                    except:
                        continue
        
        return traces


# 全局实例
trace_logger = TraceLogger()


def get_trace_logger() -> TraceLogger:
    """获取全局追踪日志器"""
    return trace_logger


if __name__ == "__main__":
    # 测试
    logger = TraceLogger()
    
    # 创建追踪
    test_content = {
        'name': 'Test Project',
        'source': 'GitHub',
        'url': 'https://github.com/test'
    }
    
    trace_id = logger.generate_trace_id(test_content)
    print(f"生成追踪ID: {trace_id}")
    
    logger.create_trace(trace_id, test_content)
    
    # 模拟处理流程
    logger.log_source_discover(trace_id, 'GitHub', 5)
    logger.log_module_start(trace_id, 'readme_processor', {'url': 'https://github.com/test'})
    logger.log(trace_id, 'readme_processor', 'INFO', '正在获取README...')
    logger.log(trace_id, 'readme_processor', 'INFO', 'README获取成功', {'length': 1500})
    logger.log_module_end(trace_id, 'readme_processor', {'features': ['AI', 'Fast']}, 1200)
    
    logger.log_composition(trace_id, 'narrative_composer', 350)
    logger.log_publish(trace_id, 'forum_publisher', True)
    logger.set_final_output(trace_id, '这是最终输出内容...')
    
    # 诊断
    print("\n" + logger.diagnose(trace_id))
    
    # 列出最近
    print("\n最近追踪:")
    for t in logger.list_recent(5):
        print(f"  {t['trace_id']}: {t['name'][:30]} ({t['status']})")
