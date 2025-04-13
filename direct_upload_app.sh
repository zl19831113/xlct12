#!/bin/bash
# 直接上传修复后的app.py到服务器（不创建备份）

SERVER="root@120.26.12.100"
REMOTE_PATH="/var/www/question_bank"
LOCAL_FILE="app.py"

echo "正在直接上传 $LOCAL_FILE 到服务器..."
scp "$LOCAL_FILE" "$SERVER:$REMOTE_PATH"

if [ $? -eq 0 ]; then
  echo "上传成功！"
  echo "正在重启服务器程序..."
  ssh $SERVER "cd $REMOTE_PATH && sudo systemctl restart question_bank"
  echo "服务已重启，修复完成。"
else
  echo "上传失败，请检查网络连接或服务器状态。"
  exit 1
fi
