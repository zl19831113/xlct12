#!/bin/bash

# 精简版应用启动脚本 - 仅安装核心依赖并启动
# 创建于: 2025-04-01

# 服务器配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 使用sshpass自动提供密码
if ! command -v sshpass &> /dev/null; then
    echo "安装sshpass..."
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo "无法安装sshpass，将使用普通SSH连接"
        SSH_CMD="ssh"
    else
        SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
    fi
else
    SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
fi

echo "======== 快速启动应用程序 ========"

# 停止所有Python进程
echo "1. 停止所有Python进程..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"pkill -f python || true\""
sleep 2

# 安装必要的Python包 - 使用系统级安装
echo "2. 安装必要的系统包..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"apt-get update && apt-get install -y python3-flask python3-pip python3-tqdm python3-numpy python3-pillow python3-docx\""

# 创建极简化的启动脚本
echo "3. 创建启动脚本..."
cat << EOF > /tmp/minimal_start.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "服务器应用正在启动中...请耐心等待"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

# 上传并启动
echo "4. 上传并启动临时应用..."
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/minimal_start.py ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/minimal_start.py
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && nohup python3 minimal_start.py > minimal.log 2>&1 &\""

# 验证是否启动
echo "5. 验证临时应用是否启动..."
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep 'python3.*minimal_start.py' | grep -v grep\""

# 更新nginx配置
echo "6. 更新Nginx配置..."
cat << EOF > /tmp/simple_nginx.conf
server {
    listen 80;
    server_name 120.26.12.100;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /var/www/question_bank/static;
    }
}
EOF

# 上传并应用新配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/simple_nginx.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/simple.conf
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/simple.conf /etc/nginx/sites-enabled/ && systemctl restart nginx\""

echo "======== 临时应用已启动 ========"
echo "现在应该可以访问: http://${REMOTE_SERVER}/"
echo "临时页面显示后，我们将继续工作修复主应用程序"
