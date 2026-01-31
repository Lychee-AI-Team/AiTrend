#!/bin/bash
# AI Hotspot Collector - 简化测试

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/ai-hotspot-collector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

FEISHU_APP_ID="${FEISHU_APP_ID:-}"
FEISHU_SECRET_KEY="${FEISHU_SECRET_KEY:-}"
FEISHU_GROUP_ID="${FEISHU_GROUP_ID:-}"

log "=== 测试飞书发送 ==="

if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_SECRET_KEY" ] && [ -n "$FEISHU_GROUP_ID" ]; then
    log "步骤1: 获取 tenant_access_token..."
    resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$FEISHU_APP_ID\", \"app_secret\": \"$FEISHU_SECRET_KEY\"}")
    
    if [ "$(echo "$resp" | jq -r '.code')" != "0" ]; then
        log "获取 token 失败: $(echo "$resp" | jq -r '.msg')"
        exit 1
    fi
    token=$(echo "$resp" | jq -r '.tenant_access_token')
    log "获取 token 成功"
    
    log "步骤2: 发送测试消息到群聊..."
    
    # 发送最简单的文本消息
    test_content="AI 热点测试消息 - $(date '+%H:%M:%S')"
    
    msg_resp=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"receive_id\": \"$FEISHU_GROUP_ID\",
            \"msg_type\": \"text\",
            \"content\": \"{\\\"text\\\": \\\"$test_content\\\"}\"
        }")
    
    log "响应: $msg_resp"
    
    if [ "$(echo "$msg_resp" | jq -r '.code')" = "0" ]; then
        log "发送成功！✅"
    else
        log "发送失败: $(echo "$msg_resp" | jq -r '.msg')"
    fi
else
    log "飞书参数未配置"
fi

log "=== 完成 ==="
