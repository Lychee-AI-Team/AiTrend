#!/bin/bash
# 🔍 全面内容拼接扫描脚本
# 扫描所有 Python 文件，查找可能的内容拼接模式

echo "========================================"
echo "🔍 AiTrend 全面内容拼接扫描"
echo "========================================"
echo ""

# 统计文件数
file_count=$(find src/ -name "*.py" -type f | grep -v __pycache__ | wc -l)
echo "扫描文件数: $file_count"
echo ""

# 关键指标
issues_found=0

echo "----------------------------------------"
echo "1️⃣ 检查内容生成函数中的 .append() 模式"
echo "----------------------------------------"

# 查找内容生成相关的 .append()（排除数据源收集、列表构建、验证报告等正当用途）
# 只检查 generate_*, format_* 等内容生成函数
content_append=$(grep -rn "\.append(" src/ --include="*.py" | grep -v __pycache__ | grep -E "generate_|format_|narrative|content|story" | grep -v "sent_articles\|published_contents\|unique_articles\|diverse_articles\|new_articles\|test_data\|run_record\|contents\|check_structured\|issues\.append" || true)

if [ -n "$content_append" ]; then
    echo "🚨 发现内容生成中的 .append() 模式："
    echo "$content_append"
    issues_found=$((issues_found + 1))
else
    echo "✅ 未发现内容生成中的 .append() 问题"
fi

echo ""
echo "----------------------------------------"
echo "2️⃣ 检查字符串累积拼接 (+=)"
echo "----------------------------------------"

# 查找 content += 或 result += 模式（排除数值计算）
string_concat=$(grep -rn "content\s*+=\s*" src/ --include="*.py" | grep -v __pycache__ | grep -v "^[^:]*:[0-9]*:.*#" || true)

if [ -n "$string_concat" ]; then
    echo "🚨 发现字符串累积拼接："
    echo "$string_concat"
    issues_found=$((issues_found + 1))
else
    echo "✅ 未发现字符串累积拼接问题"
fi

echo ""
echo "----------------------------------------"
echo "3️⃣ 检查 join() 用于内容生成"
echo "----------------------------------------"

# 查找 \\n\\n.join() 或 \\n.join() 用于内容拼接
content_join=$(grep -rn '"\\\\n\\\\n"\.join\|"\\\\n"\.join' src/ --include="*.py" | grep -v __pycache__ | grep -v "twitter.py.*json.loads" || true)

if [ -n "$content_join" ]; then
    echo "🚨 发现 join() 用于内容生成："
    echo "$content_join"
    issues_found=$((issues_found + 1))
else
    echo "✅ 未发现 join() 用于内容生成的问题"
fi

echo ""
echo "----------------------------------------"
echo "4️⃣ 检查 parts = [] 初始化模式"
echo "----------------------------------------"

# 查找内容生成中的 parts = [] 模式
parts_init=$(grep -rn "parts\s*=\s*\[\]" src/ --include="*.py" | grep -v __pycache__ || true)

if [ -n "$parts_init" ]; then
    echo "🚨 发现 parts = [] 拼接模式："
    echo "$parts_init"
    issues_found=$((issues_found + 1))
else
    echo "✅ 未发现 parts = [] 拼接模式"
fi

echo ""
echo "----------------------------------------"
echo "5️⃣ 检查正确的 f-string 模式"
echo "----------------------------------------"

# 统计正确的 f-string 直接赋值
fstring_count=$(grep -rn "content\s*=\s*f\"\"\"" src/ --include="*.py" | grep -v __pycache__ | wc -l)
echo "✅ 发现 $fstring_count 处正确的 f-string 直接赋值"

echo ""
echo "========================================"

if [ $issues_found -gt 0 ]; then
    echo "🚨 扫描完成！发现 $issues_found 类问题"
    echo ""
    echo "根据项目宪法，严格禁止："
    echo "  ❌ parts = [] + parts.append() + join()"
    echo "  ❌ content += ... 累积拼接"
    echo "  ❌ 模板填充式内容生成"
    echo ""
    echo "正确做法："
    echo "  ✅ content = f\"\"\"完整内容...{变量}...\"\"\""
    exit 1
else
    echo "✅ 扫描完成！未发现内容拼接问题"
    echo "✅ 代码完全符合项目宪法要求"
    exit 0
fi
