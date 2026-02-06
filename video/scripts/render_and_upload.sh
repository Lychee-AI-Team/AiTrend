#!/bin/bash
# 渲染视频并上传到七牛云
# 使用: ./render_and_upload.sh

set -e  # 遇到错误立即退出

echo "🎬 AiTrend 视频渲染上传脚本"
echo "=============================="

# 配置
TEMPLATE="index-final.tsx"
COMPOSITION="DailyNewsFinal"
OUTPUT_DIR="../output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/aitrend_${TIMESTAMP}.mp4"

# 确保输出目录存在
mkdir -p ${OUTPUT_DIR}

echo ""
echo "📹 步骤1: 渲染视频"
echo "------------------------------"
cd /home/ubuntu/.openclaw/workspace/AiTrend/video/src

echo "渲染中... (这可能需要5-10分钟)"
npx remotion render ${TEMPLATE} ${COMPOSITION} ${OUTPUT_FILE} \
  --browser-executable=$(find ~/.cache/ms-playwright -name "chrome" -type f | head -1) \
  --concurrency=2 \
  --overwrite

if [ ! -f "${OUTPUT_FILE}" ]; then
    echo "❌ 视频渲染失败"
    exit 1
fi

echo "✅ 视频渲染完成: ${OUTPUT_FILE}"

# 获取文件大小
FILE_SIZE=$(du -h ${OUTPUT_FILE} | cut -f1)
echo "   文件大小: ${FILE_SIZE}"

echo ""
echo "☁️  步骤2: 上传到七牛云"
echo "------------------------------"
cd /home/ubuntu/.openclaw/workspace/AiTrend/video/scripts

python3 upload_to_qiniu.py ${OUTPUT_FILE}

if [ $? -ne 0 ]; then
    echo "❌ 上传失败"
    exit 1
fi

echo ""
echo "📢 步骤3: 发送飞书通知"
echo "------------------------------"

# 读取上传结果
UPLOAD_INFO="${OUTPUT_FILE}.upload.json"
if [ -f "${UPLOAD_INFO}" ]; then
    VIDEO_URL=$(python3 -c "import json; print(json.load(open('${UPLOAD_INFO}'))['url'])")
    python3 notify_feishu.py "${VIDEO_URL}" "AiTrend ${TIMESTAMP}"
fi

echo ""
echo "🎉 全部完成!"
echo "=============================="
echo "视频文件: ${OUTPUT_FILE}"
echo "上传信息: ${UPLOAD_INFO}"
