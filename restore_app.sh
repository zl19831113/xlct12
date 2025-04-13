#!/bin/bash

# 恢复应用程序脚本
# 从测试页面恢复到实际应用程序

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 恢复应用程序 ====="

# 1. 确认所有文件仍然存在
echo "1. 检查应用程序文件..."
eval "${SSH_CMD} \"ls -la ${REMOTE_DIR} | head\""

# 2. 创建针对应用程序的Nginx配置
cat << EOF > /tmp/app.conf
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5001;  # 使用app.py中定义的端口5001
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias ${REMOTE_DIR}/static;
    }
}
EOF

# 上传并应用配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/app.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/\""

# 3. 停止所有Python进程并重启应用
echo "2. 重启应用程序..."
eval "${SSH_CMD} \"pkill -f python || true\""
sleep 2
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && nohup python3 app.py > app.log 2>&1 &\""

# 4. 确认应用正在运行
echo "3. 检查应用程序是否运行..."
sleep 3
eval "${SSH_CMD} \"ps aux | grep 'python3.*app.py' | grep -v grep\""

# 5. 检查是否监听正确端口
echo "4. 检查端口5001是否在监听..."
eval "${SSH_CMD} \"netstat -tuln | grep 5001\""

# 6. 重启Nginx
echo "5. 重启Nginx..."
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

# 7. 检查最近的日志
echo "6. 查看应用程序日志..."
eval "${SSH_CMD} \"tail -n 20 ${REMOTE_DIR}/app.log\""

echo "===== 恢复完成 ====="
echo "请访问: http://${REMOTE_SERVER}/"
echo "您的应用程序应该已恢复正常"
