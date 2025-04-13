#!/bin/bash

# 安装pandas和其他缺失依赖
# 创建于: 2025-04-01

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 安装pandas和其他依赖 ====="

# 1. 安装pandas和其他可能需要的库
echo "1. 安装缺失的依赖库..."
eval "${SSH_CMD} \"pip3 install --break-system-packages pandas matplotlib numpy openpyxl\""

# 2. 停止所有Python进程
echo "2. 停止当前运行的应用程序..."
eval "${SSH_CMD} \"pkill -f python || true\""
sleep 2

# 3. 启动应用程序
echo "3. 启动应用程序..."
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && nohup python3 app.py > app.log 2>&1 &\""
sleep 5

# 4. 检查应用程序是否在运行
echo "4. 检查应用程序是否运行..."
eval "${SSH_CMD} \"ps aux | grep 'python3.*app.py' | grep -v grep\""

# 5. 检查最新的日志
echo "5. 查看应用程序日志..."
eval "${SSH_CMD} \"tail -n 30 ${REMOTE_DIR}/app.log\""

echo "===== 依赖安装完成 ====="
echo "请访问: http://${REMOTE_SERVER}/"
echo "您的应用程序应该已经正常启动"
