#!/bin/bash

# 最终修复 - 使用正确的端口5001
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 最终修复 (使用正确端口5001) ====="

# 创建最终Nginx配置
cat << EOF > /tmp/final.conf
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/final.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/ && systemctl restart nginx\""

# 彻底杀掉所有Python进程
eval "${SSH_CMD} \"pkill -9 -f python || true\""
sleep 2

# 启动应用
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && nohup python3 app.py > app.log 2>&1 &\""
sleep 5

# 验证应用启动
echo "检查应用是否在运行..."
eval "${SSH_CMD} \"ps aux | grep 'python3.*app.py' | grep -v grep\""

# 验证端口5001是否被监听
echo "检查端口5001是否被监听..."
eval "${SSH_CMD} \"netstat -tuln | grep 5001\""

echo "===== 修复完成 ====="
echo "请立即访问: http://120.26.12.100/"
