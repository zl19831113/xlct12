#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."
REMOTE_PATH="/var/www/question_bank"

# 今天修改的文件
MODIFIED_FILES=(
  "templates/papers.html"
)

echo "快速上传修改的文件到服务器中..."

# 上传每个修改的文件
for file in "${MODIFIED_FILES[@]}"; do
  echo "上传: $file"
  sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$file" $USER@$SERVER:"$REMOTE_PATH/$file"
  if [ $? -eq 0 ]; then
    echo "成功上传: $file"
  else
    echo "上传失败: $file"
  fi
done

# 重启服务
echo "重启服务..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart gunicorn && systemctl restart nginx"

echo "所有文件上传完成！服务已重启。" 