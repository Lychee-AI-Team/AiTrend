#!/usr/bin/env python3
"""
AiTrend 安装向导
零配置启动，引导用户逐步添加 API Key
"""

import os
import sys

def check_gemini_key():
    """检查 Gemini API Key 是否配置"""
    # 检查环境变量
    if os.getenv('GEMINI_API_KEY'):
        return True
    
    # 检查 .env 文件
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and 'your_' not in content:
                return True
    
    return False

def setup_gemini_key():
    """引导用户设置 Gemini Key"""
    print("=" * 60)
    print("🚀 AiTrend Skill 首次启动")
    print("=" * 60)
    print()
    print("我需要 Gemini API Key 来生成 AI 内容总结。")
    print()
    print("获取方式：")
    print("1. 访问 https://ai.google.dev/")
    print("2. 登录 Google 账号")
    print("3. 创建 API Key（免费）")
    print()
    
    key = input("请输入你的 Gemini API Key: ").strip()
    
    if not key or 'your_' in key:
        print("❌ 无效的 API Key")
        return False
    
    # 保存到 .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path, 'w') as f:
        f.write(f"GEMINI_API_KEY={key}\n")
    
    print(f"✅ API Key 已保存到 {env_path}")
    return True

def show_first_run_success():
    """首次运行成功后的提示"""
    print()
    print("=" * 60)
    print("✅ 首次运行完成！")
    print("=" * 60)
    print()
    print("当前数据源：")
    print("  • HackerNews - 开发者社区热门")
    print("  • Reddit - AI 社区讨论")
    print("  • GitHub - AI 开源项目")
    print()
    print("可选增强数据源：")
    print("  • Twitter - 实时 viral 内容 (需要 Cookie)")
    print("  • Product Hunt - 新产品发布 (需要 Token)")
    print("  • Brave Search - 全网搜索 (需要 API Key)")
    print()
    print("如需配置更多数据源，请编辑 config/config.json")

def main():
    """主函数"""
    # 检查 Gemini Key
    if not check_gemini_key():
        if not setup_gemini_key():
            print("❌ 无法继续，Gemini API Key 是必需的")
            sys.exit(1)
    
    # 导入并运行主程序
    try:
        from src import main as run_main
        run_main()
        show_first_run_success()
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
