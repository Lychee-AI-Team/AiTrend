#!/bin/bash
# trigger_all_platforms.sh - 触发所有平台，每个至少3条消息

echo "🚀 AiTrend 全平台触发脚本"
echo "============================"
echo ""

# 设置工作目录
cd "$(dirname "$0")"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# 确保nvm可用
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 平台列表
PLATFORMS=("github" "arxiv" "hackernews" "reddit" "twitter")
MIN_COUNT=3

echo "📋 触发计划:"
echo "  平台数量: ${#PLATFORMS[@]} 个"
echo "  每平台至少: $MIN_COUNT 条"
echo ""

# 逐个触发平台
for platform in "${PLATFORMS[@]}"; do
    echo -e "${YELLOW}▶ 触发平台: $platform${NC}"
    
    python3 launcher.py --source "$platform" --min "$MIN_COUNT" --max-total "$MIN_COUNT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $platform 完成${NC}"
    else
        echo -e "${RED}❌ $platform 失败${NC}"
    fi
    
    echo ""
    
    # 平台间延迟，避免速率限制
    sleep 3
done

echo "============================"
echo "🎉 全平台触发完成"
echo ""

# 显示最近记录
echo "📊 最近发布记录:"
python3 launcher.py --recent | tail -20
