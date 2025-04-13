#!/bin/bash

# 连接到远程服务器并重启应用
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
APP_DIR="/var/www/question_bank"

echo "正在连接到服务器 $REMOTE_HOST 并重启应用..."

# 使用sshpass避免手动输入密码，执行更细致的重启命令
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "cd $APP_DIR && \
  echo '查找运行中的Python进程...' && \
  pgrep -f 'python.*app\.py' && \
  echo '关闭现有的Python进程...' && \
  pkill -f 'python.*app\.py' && \
  echo '等待进程关闭...' && \
  sleep 2 && \
  echo '启动应用程序...' && \
  cd $APP_DIR && \
  nohup python app.py > app.log 2>&1 & \
  echo '应用已在后台重新启动' || \
  echo '没有找到运行中的应用，正在启动新实例...' && \
  cd $APP_DIR && \
  nohup python app.py > app.log 2>&1 & \
  echo '应用已在后台启动'"

echo "命令已执行，服务器应用应已重启。"
echo "提示：请等待几秒钟，然后再刷新浏览器，以便应用完全启动。"
