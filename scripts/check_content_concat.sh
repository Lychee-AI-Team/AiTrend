#!/bin/bash
# 🔍 严格内容拼接检查脚本
# 根据项目宪法，绝对禁止任何形式的字符串拼接生成内容

set -e

echo "🔍 检查代码中是否存在内容拼接模式..."
echo "==========================================="

# 禁止的模式（正则表达式）- 仅检查内容生成相关的拼接
PATTERNS=(
    # 严格禁止：内容生成中的 parts.append + join 模式
    'parts\s*=\s*\[\]'
    'sections\s*=\s*\[\]'
    'chunks\s*=\s*\[\]'
    'paragraphs\s*=\s*\[\]'
    
    # 严格禁止：content/result 相关的 join（排除变量名如 result_data）
    '"\\\\n\\\\n"\.join'
    '\.join\(parts\b'
    '\.join\(sections\b'
    '\.join\(chunks\b'
    '\.join\(paragraphs\b'
    '\.join\(lines\b'
    
    # 严格禁止：content += 累积拼接（只匹配 += 不匹配 =）
    'content\s*+=\s*'
    'result\s*+=\s*'
)

found_issues=0

for pattern in "${PATTERNS[@]}"; do
    matches=$(grep -rn "$pattern" src/ --include="*.py" 2>/dev/null | grep -v __pycache__ | grep -v ".pyc" || true)
    if [ -n "$matches" ]; then
        echo ""
        echo "🚨 发现禁止的拼接模式: $pattern"
        echo "$matches"
        found_issues=$((found_issues + 1))
    fi
done

# 额外检查：查找 generate_content 函数中的问题模式
echo ""
echo "🔍 深度检查内容生成函数..."

# 检查是否存在返回 "\\n\\n".join() 的模式
if grep -rn 'return.*"\\\\n\\\\n".*join' src/ --include="*.py" 2>/dev/null | grep -v __pycache__ > /dev/null; then
    echo "🚨 发现返回拼接内容的模式！"
    grep -rn 'return.*"\\\\n\\\\n".*join' src/ --include="*.py" | grep -v __pycache__
    found_issues=$((found_issues + 1))
fi

# 检查是否存在多行 f-string 后直接返回（正确做法）
echo ""
echo "✅ 检查是否存在正确的直接返回模式..."
correct_patterns=$(grep -rn 'content\s*=\s*f"""' src/ --include="*.py" 2>/dev/null | grep -v __pycache__ | wc -l)
if [ "$correct_patterns" -gt 0 ]; then
    echo "✅ 发现 $correct_patterns 处使用直接 f-string 赋值的正确模式"
fi

echo ""
echo "==========================================="

if [ $found_issues -gt 0 ]; then
    echo "🚨 检查失败！发现 $found_issues 处内容拼接问题"
    echo ""
    echo "根据项目宪法，严格禁止："
    echo "  ❌ parts = [] + parts.append() + '\\n'.join(parts)"
    echo "  ❌ content += ... 累积拼接"
    echo "  ❌ 任何模板填充式内容生成"
    echo ""
    echo "正确做法："
    echo "  ✅ content = f\"\"\"完整内容...{变量}...\"\"\""
    echo "  ✅ 直接返回完整的 f-string"
    exit 1
else
    echo "✅ 检查通过！未发现内容拼接问题"
    exit 0
fi
