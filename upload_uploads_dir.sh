#!/bin/bash

# 上传uploads目录到远程服务器
# 使用rsync进行高效传输

SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/"
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"
SSH_PASS="85497652Sl."

echo "开始上传uploads目录到 $REMOTE_HOST:$REMOTE_DIR/uploads..."
echo "这可能需要一段时间，取决于uploads目录的大小"

# 确保目标目录存在
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "mkdir -p $REMOTE_DIR/uploads"

# 使用sshpass和rsync上传文件
sshpass -p "$SSH_PASS" rsync -avz --progress \
  --delete \
  "$SOURCE_DIR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

echo "uploads目录上传完成！"
