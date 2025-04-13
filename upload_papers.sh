#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."
REMOTE_PATH="/var/www/question_bank/uploads/papers"
LOCAL_PATH="uploads/papers"

echo "开始上传 $LOCAL_PATH 中的文件到服务器..."

# 确保本地目录存在
if [ ! -d "$LOCAL_PATH" ]; then
    echo "错误：本地目录 $LOCAL_PATH 不存在！"
    exit 1
fi

# 显示要上传的文件数量
FILE_COUNT=$(find "$LOCAL_PATH" -type f | wc -l)
echo "共发现 $FILE_COUNT 个文件需要上传"

# 直接使用rsync上传文件，显示详细进度
echo "开始上传文件..."
sshpass -p "$PASS" rsync -avz --progress --stats -e "ssh -o StrictHostKeyChecking=no" "$LOCAL_PATH/" "$USER@$SERVER:$REMOTE_PATH/"

echo "文件上传完成，正在重启服务..."

# 在服务器上执行重启和清理缓存操作
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd /var/www/question_bank && \
    php artisan cache:clear && \
    php artisan config:clear && \
    php artisan route:clear && \
    php artisan view:clear && \
    sudo systemctl restart php8.1-fpm && \
    sudo systemctl restart nginx && \
    echo '服务重启完成'"

echo "所有操作已完成！" 