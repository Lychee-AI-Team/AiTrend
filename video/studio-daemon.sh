#!/bin/bash
# Remotion Studio 守护脚本
# 自动检测崩溃并重启

LOG_FILE="/tmp/remotion-studio.log"
PID_FILE="/tmp/remotion-studio.pid"
MAX_RESTART=10
RESTART_COUNT=0

cd /home/ubuntu/.openclaw/workspace/AiTrend/video/src

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

while [ $RESTART_COUNT -lt $MAX_RESTART ]; do
    echo "[$(date)] 启动 Studio (第 $RESTART_COUNT 次)..." >> $LOG_FILE
    
    # 启动 Studio
    npx remotion studio index-vertical.tsx --port=3003 >> $LOG_FILE 2>&1 &
    STUDIO_PID=$!
    
    # 记录PID
    echo $STUDIO_PID > $PID_FILE
    
    echo "[$(date)] Studio PID: $STUDIO_PID" >> $LOG_FILE
    
    # 等待进程结束
    wait $STUDIO_PID
    EXIT_CODE=$?
    
    echo "[$(date)] Studio 退出，退出码: $EXIT_CODE" >> $LOG_FILE
    
    RESTART_COUNT=$((RESTART_COUNT + 1))
    
    if [ $RESTART_COUNT -lt $MAX_RESTART ]; then
        echo "[$(date)] 5秒后自动重启..." >> $LOG_FILE
        sleep 5
    fi
done

echo "[$(date)] 达到最大重启次数，停止守护" >> $LOG_FILE
