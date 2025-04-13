#!/bin/bash

# 修复服务器路径问题 - 确保修复应用到正确的目录
# 创建于: 2025-04-01

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_UPLOAD_DIR="/var/www/question_bank"
REMOTE_APP_DIR="/var/www/zujuanwang"

echo "检查服务器上的应用目录..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "ls -la ${REMOTE_APP_DIR} && ls -la ${REMOTE_UPLOAD_DIR}"

echo -e "\n复制修复后的文件到正确的应用程序目录..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cp ${REMOTE_UPLOAD_DIR}/app.py ${REMOTE_APP_DIR}/app.py && echo 'app.py 复制成功'"

echo -e "\n复制修复后的数据库文件..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "mkdir -p ${REMOTE_APP_DIR}/instance && cp ${REMOTE_UPLOAD_DIR}/instance/xlct12.db ${REMOTE_APP_DIR}/instance/xlct12.db && chmod 644 ${REMOTE_APP_DIR}/instance/xlct12.db && echo '数据库复制成功'"

echo -e "\n重启应用程序进程..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "pkill -f 'gunicorn.*app:app' && cd ${REMOTE_APP_DIR} && ${REMOTE_APP_DIR}/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app --timeout 300 --daemon"

echo -e "\n验证应用程序是否已重启..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "ps aux | grep -i 'gunicorn.*app:app' | grep -v grep"

echo -e "\n重启nginx..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart nginx || service nginx restart"

echo "修复完成，应用程序已重启"
