#!/bin/bash
# 🔥 紧急清理旧代码脚本
# 删除仍在使用内容拼接的旧 modules 和 launcher 文件

echo "🔥 紧急清理旧代码"
echo "========================================"
echo ""

# 检查当前目录
if [ ! -f "skill.yaml" ]; then
    echo "❌ 错误：必须在 AiTrend 根目录运行"
    exit 1
fi

echo "发现以下文件仍在使用内容拼接（parts.append + join）："
echo ""

# 列出违规文件
echo "📁 modules/ 目录（旧代码）:"
grep -l "parts\.append\|\.join(parts" modules/*.py modules/**/*.py 2>/dev/null | head -10 || echo "  无.py文件"

echo ""
echo "📁 launcher 文件（引用旧代码）:"
for f in launcher.py launcher_openclaw.py launcher_v2.py auto_publish.py demo_new_architecture.py demo_switching.py run_flow.py run_full_flow.py run_hackernews.py run_producthunt.py run_reddit.py test_publisher.py; do
    if [ -f "$f" ]; then
        echo "  - $f"
    fi
done

echo ""
echo "========================================"
echo ""

# 询问是否删除
read -p "⚠️  是否删除这些旧文件？(yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo ""
    echo "🗑️  正在删除..."
    
    # 删除旧的 launcher 文件
    for f in launcher.py launcher_openclaw.py launcher_v2.py auto_publish.py demo_new_architecture.py demo_switching.py run_flow.py run_full_flow.py run_hackernews.py run_producthunt.py run_reddit.py test_publisher.py; do
        if [ -f "$f" ]; then
            git rm "$f" 2>/dev/null || rm "$f"
            echo "  ✅ 已删除: $f"
        fi
    done
    
    # 删除旧的 modules 目录
    if [ -d "modules" ]; then
        git rm -rf modules/ 2>/dev/null || rm -rf modules/
        echo "  ✅ 已删除: modules/"
    fi
    
    # 保留最新的 run_producthunt_direct.py（如果它是新版本）
    # 检查是否使用旧模式
    if grep -q "parts\.append\|\.join(parts" run_producthunt_direct.py 2>/dev/null; then
        git rm run_producthunt_direct.py 2>/dev/null || rm run_producthunt_direct.py
        echo "  ✅ 已删除: run_producthunt_direct.py（使用旧模式）"
    fi
    
    echo ""
    echo "✅ 清理完成！"
    echo ""
    echo "现在只使用新的 src/ 架构："
    echo "  python3 -m src.hourly"
    
else
    echo ""
    echo "❌ 已取消"
    exit 1
fi
