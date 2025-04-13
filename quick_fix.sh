#!/bin/bash

# 超简化的快速修复脚本
# 创建于: 2025-04-01

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 快速修复服务器应用 (预计需要1分钟) ====="

# 1. 杀掉所有Python进程
echo "1. 清理所有进程..."
eval "${SSH_CMD} \"pkill -f python || true\""

# 2. 安装tqdm包 - 主要缺失的依赖
echo "2. 安装缺失依赖..."
eval "${SSH_CMD} \"pip3 install --break-system-packages tqdm\""

# 3. 直接用原始的方式启动应用
echo "3. 直接启动应用..."
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && nohup python3 app.py > direct_app.log 2>&1 &\""

# 4. 验证是否启动
echo "4. 验证应用是否启动..."
sleep 3
eval "${SSH_CMD} \"ps aux | grep 'python3.*app.py' | grep -v grep\""

# 5. 简化Nginx配置
echo "5. 简化Nginx配置..."
cat << EOF > /tmp/quick_nginx.conf
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

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/quick_nginx.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default.conf
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default.conf /etc/nginx/sites-enabled/ && nginx -t && systemctl restart nginx\""

echo "===== 快速修复完成 ====="
echo "请立即访问: http://${REMOTE_SERVER}/"
echo "如果30秒内仍无法访问，我们将尝试最后的备选方案"
