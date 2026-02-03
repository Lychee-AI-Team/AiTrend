#!/bin/bash
# 📦 密钥文件自动备份脚本

BACKUP_DIR=".backup"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 备份密钥文件
if [ -f ".env.keys" ]; then
    cp ".env.keys" "$BACKUP_DIR/.env.keys.$DATE"
    chmod 600 "$BACKUP_DIR/.env.keys.$DATE"
    echo "✅ 已备份 .env.keys"
fi

# 保留最近 10 个备份
cd "$BACKUP_DIR"
ls -t .env.keys.* 2>/dev/null | tail -n +11 | xargs -r rm -f

echo "✅ 备份完成"
