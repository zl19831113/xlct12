#!/bin/bash

# 尝试多种方式重启服务器应用程序
# 创建于: 2025-04-01

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 检查sshpass是否已安装
if ! command -v sshpass &> /dev/null; then
    echo "正在安装sshpass工具..."
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo "无法安装sshpass，将使用普通SSH连接，需要手动输入密码"
        SSH_CMD="ssh"
    else
        SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
    fi
else
    SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
fi

echo "开始尝试重启服务器应用程序..."

# 列出正在运行的进程，查找应用程序进程
echo "查找正在运行的Python应用程序进程..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i python | grep -v grep\""

# 尝试通过不同的服务管理器重启
echo "尝试通过systemctl重启服务..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart gunicorn 2>/dev/null || systemctl restart uwsgi 2>/dev/null || systemctl restart www 2>/dev/null || systemctl restart web 2>/dev/null || echo '无法通过systemctl重启'\""

echo "尝试在/etc/init.d中查找服务..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ls -la /etc/init.d/ | grep -i 'web\|www\|nginx\|gunicorn\|uwsgi\|flask'\""

echo "尝试通过supervisor重启服务..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"command -v supervisorctl && supervisorctl restart all || echo '未安装supervisor'\""

# 检查应用程序目录及日志文件
echo "检查应用程序目录和日志..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ls -la | grep -i 'log\|wsgi\|conf'\""

# 直接启动方式 - 先杀掉旧进程，再启动新进程
echo "尝试直接重启Python进程..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && pkill -f \\\"python.*app.py\\\" && nohup python3 app.py > app.log 2>&1 &\""

# 重启nginx
echo "重启nginx..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart nginx || service nginx restart || /etc/init.d/nginx restart || echo '无法重启nginx'\""

echo "所有重启方式已尝试完毕，请检查应用程序是否正常运行"
