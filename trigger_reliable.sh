#!/bin/bash
# trigger_reliable.sh - 触发可靠的平台（跳过有问题的平台）

echo "🚀 AiTrend 可靠平台触发脚本"
echo "============================"
echo ""

# 设置工作目录
cd "$(dirname "$0")"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 可靠平台列表（已测试通过）
RELIABLE_PLATFORMS=("github" "arxiv")

# 需要API Token的平台（可选）
if [ -n "$PRODUCTHUNT_TOKEN" ]; then
    RELIABLE_PLATFORMS+=("producthunt")
fi

MIN_COUNT=3

echo "📋 触发计划:"
echo "  平台: ${RELIABLE_PLATFORMS[@]}"
echo "  每平台: $MIN_COUNT 条"
echo ""

# 逐个触发平台
for platform in "${RELIABLE_PLATFORMS[@]}"; do
    echo -e "${YELLOW}▶ 触发平台: $platform${NC}"
    
    python3 launcher.py --source "$platform" --min "$MIN_COUNT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $platform 完成${NC}"
    else
        echo -e "${RED}❌ $platform 失败${NC}"
    fi
    
    echo ""
    sleep 3
done

echo "============================"
echo "🎉 可靠平台触发完成"
echo ""

# 显示统计
echo "📊 各平台发布统计:"
python3 launcher.py --recent | head -20
