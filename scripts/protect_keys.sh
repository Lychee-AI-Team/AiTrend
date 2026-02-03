#!/bin/bash
# 🔐 密钥保护检查脚本

set -e

KEY_FILES=(".env.keys" ".env" ".env.keys.backup")

echo "🔐 AiTrend 密钥保护检查"
echo "==========================================="

failed=0

for file in "${KEY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo ""
        echo "📄 检查 $file..."
        
        # 检查是否在 .gitignore 中
        if git check-ignore -q "$file" 2>/dev/null; then
            echo "  ✅ 受 .gitignore 保护"
        else
            echo "  🚨 $file 不在 .gitignore 中！"
            failed=1
        fi
        
        # 检查权限
        perms=$(stat -c "%a" "$file" 2>/dev/null || stat -f "%Lp" "$file" 2>/dev/null)
        if [ "$perms" = "600" ]; then
            echo "  ✅ 权限正确 (600)"
        else
            echo "  ⚠️  权限为 $perms"
        fi
    fi
done

echo ""
echo "==========================================="

if [ $failed -eq 0 ]; then
    echo "✅ 密钥保护检查通过"
    exit 0
else
    echo "🚨 密钥保护检查失败！"
    exit 1
fi
