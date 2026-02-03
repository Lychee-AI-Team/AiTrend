#!/bin/bash
# 🛡️ 安全的 git clean 包装脚本

echo "🛡️ AiTrend 安全清理工具"
echo "==========================================="
echo ""

# 显示将要删除的文件
echo "📋 以下文件将被清理："
echo "-------------------------------------------"
git clean -fd --dry-run -e ".env*" -e "*.keys" | grep -v "Would remove \.env" | grep -v "Would remove .*\.keys" || echo "  (无)"
echo "-------------------------------------------"
echo ""
echo "🔒 注意: 所有 .env* 和 *.keys 文件已自动排除"
echo ""

read -p "⚠️  确认执行清理？(输入 'yes' 确认): " confirm

if [ "$confirm" = "yes" ]; then
    echo ""
    echo "🧹 执行安全清理..."
    git clean -fd -e ".env*" -e "*.keys" -e "*.keys.*"
    echo ""
    echo "✅ 清理完成！密钥文件已保护"
else
    echo ""
    echo "❌ 已取消"
fi
