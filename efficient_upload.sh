#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."
REMOTE_PATH="/var/www/question_bank"
LOCAL_DIR="uploads"
ARCHIVE="uploads.tar.gz"

echo "开始高效上传..."

# 先创建压缩包
echo "正在压缩 $LOCAL_DIR 目录..."
tar -czf $ARCHIVE $LOCAL_DIR

# 使用rsync进行上传（支持断点续传）
echo "开始上传压缩包..."
sshpass -p "$PASS" rsync -avz --progress -e "ssh -o StrictHostKeyChecking=no" $ARCHIVE $USER@$SERVER:$REMOTE_PATH/

# 解压远程文件
echo "解压远程文件..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_PATH && tar -xzf $ARCHIVE && rm $ARCHIVE"

# 删除本地压缩包
rm $ARCHIVE

echo "上传并解压完成！" 