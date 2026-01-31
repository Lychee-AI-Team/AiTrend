#!/bin/bash
# AI Hotspot Collector - 详细调试版

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

log "=== 发送到飞书群聊 ==="

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
    
    log "步骤2: 发送消息到群聊..."
    
    # 测试发送简单消息
    test_content="AI 热点测试 $(date '+%H:%M:%S')"
    
    log "发送测试消息: $test_content"
    
    # 使用 curl -v 获取详细响应
    msg_resp=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"receive_id\": \"$FEISHU_GROUP_ID\",
            \"msg_type\": \"text\",
            \"content\": \"{\\\"text\\\": \\\"$test_content\\\"}\"
        }")
    
    # 分离 HTTP 状态码和响应体
    http_code=$(echo "$msg_resp" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$msg_resp" | grep -v "HTTP_CODE:")
    
    log "HTTP 状态码: $http_code"
    log "响应体: $body"
    
    if [ "$http_code" = "200" ] || [ "$(echo "$body" | jq -r '.code')" = "0" ]; then
        log "发送成功！✅"
    else
        log "发送失败"
    fi
else
    log "飞书参数未配置"
fi

log "=== 完成 ==="
