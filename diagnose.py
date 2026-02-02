#!/usr/bin/env python3
"""
诊断工具

用法:
    python3 diagnose.py <追踪ID>
    
示例:
    python3 diagnose.py AIT-20260203-A1B2C3
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.trace_logger import get_trace_logger


def show_help():
    """显示帮助信息"""
    print("""
🔍 AiTrend 诊断工具

用法:
    python3 diagnose.py <追踪ID>
    
示例:
    python3 diagnose.py AIT-20260203-A1B2C3
    
功能:
    - 查看信息处理全流程日志
    - 定位错误发生的模块
    - 追踪信息转换过程

追踪ID格式:
    AIT-YYYYMMDD-XXXXXX
    可在每条消息的底部找到
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    trace_id = sys.argv[1]
    
    # 验证ID格式
    if not trace_id.startswith('AIT-') or len(trace_id) < 15:
        print(f"❌ 无效的追踪ID格式: {trace_id}")
        print("\n正确格式: AIT-YYYYMMDD-XXXXXX")
        print("示例: AIT-20260203-A1B2C3")
        return
    
    # 获取诊断报告
    logger = get_trace_logger()
    report = logger.diagnose(trace_id)
    
    print(report)
    
    # 如果追踪不存在，提供建议
    if "未找到" in report:
        print("\n💡 建议:")
        print("  1. 检查ID是否正确复制")
        print("  2. 确认该消息是否由当前系统生成")
        print("  3. 查看最近的消息列表:")
        print("     python3 diagnose.py --recent")


def show_recent():
    """显示最近的追踪记录"""
    logger = get_trace_logger()
    traces = logger.list_recent(20)
    
    print("📋 最近的消息追踪记录:\n")
    print(f"{'追踪ID':<25} {'信息源':<12} {'状态':<8} {'名称':<40}")
    print("-" * 90)
    
    for t in traces:
        status_icon = "✅" if t['status'] == 'completed' else "❌" if t['status'] == 'error' else "⏳"
        name = t['name'][:38] if len(t['name']) > 38 else t['name']
        print(f"{t['trace_id']:<25} {t['source']:<12} {status_icon} {t['status']:<6} {name}")
    
    print(f"\n💡 使用 `python3 diagnose.py <追踪ID>` 查看详情")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--recent':
        show_recent()
    else:
        main()
