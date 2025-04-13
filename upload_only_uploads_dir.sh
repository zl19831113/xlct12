#!/bin/bash

# 上传uploads目录到远程服务器（仅覆盖uploads目录）
# 使用rsync进行高效传输

SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/"
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root" 
REMOTE_DIR="/var/www/question_bank/uploads"  # 直接指定远程uploads目录
SSH_PASS="85497652Sl."

echo "开始上传本地uploads目录内容到 $REMOTE_HOST:$REMOTE_DIR..."
echo "这只会覆盖远程uploads目录，不会影响其他文件"

# 确保远程服务器上的uploads目录存在
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

# 使用rsync上传文件，确保源目录以/结尾，这样会上传目录内容而不是目录本身
sshpass -p "$SSH_PASS" rsync -avz --progress \
  "$SOURCE_DIR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

echo "uploads目录内容上传完成！"
