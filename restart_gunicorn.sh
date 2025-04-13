#!/bin/bash

# 正确重启gunicorn进程
# 创建于: 2025-04-01

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"

echo "重启gunicorn进程..."

# 找出原来的启动命令
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && ${REMOTE_DIR}/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app --timeout 300 --daemon"

echo "等待进程启动..."
sleep 3

echo "检查进程是否已启动..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "ps aux | grep -i 'gunicorn.*app:app' | grep -v grep"

echo "检查80端口是否正常工作..."
ssh ${REMOTE_USER}@${REMOTE_SERVER} "curl -s -I http://localhost:80 | head -1 || curl -s -I http://localhost:8000 | head -1"
