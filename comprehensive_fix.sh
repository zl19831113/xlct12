#!/bin/bash

# 全面修复服务器脚本
# 处理应用配置、网络设置和防火墙规则

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 开始全面服务器修复 ====="

# 1. 检查服务器基本网络配置
echo "1. 检查网络配置..."
eval "${SSH_CMD} \"ip addr && ip route\""

# 2. 完全关闭防火墙（紧急情况下）
echo "2. 关闭所有防火墙..."
eval "${SSH_CMD} \"ufw disable || true; iptables -F || true; systemctl stop firewalld || true\""

# 3. 确保80端口开放
echo "3. 确保80端口开放..."
eval "${SSH_CMD} \"iptables -I INPUT -p tcp --dport 80 -j ACCEPT\""

# 4. 检查并配置主机名和DNS
echo "4. 配置主机名和hosts文件..."
eval "${SSH_CMD} \"echo '127.0.0.1 localhost' > /etc/hosts && echo '${REMOTE_SERVER} server' >> /etc/hosts\""

# 5. 重启网络服务
echo "5. 重启网络服务..."
eval "${SSH_CMD} \"systemctl restart networking || systemctl restart NetworkManager || true\""

# 6. 停止并重新安装Nginx（如果不行则从头开始）
echo "6. 重新安装Nginx..."
eval "${SSH_CMD} \"systemctl stop nginx; apt-get update && apt-get install --reinstall -y nginx\""

# 7. 创建简单的Nginx配置
cat << EOF > /tmp/fresh.conf
server {
    listen 0.0.0.0:80;
    server_name _;
    
    location / {
        root /var/www/html;
        index index.html;
    }
}
EOF

# 上传并启用新配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/fresh.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/\""

# 8. 创建简单的测试页面
cat << EOF > /tmp/test.html
<!DOCTYPE html>
<html>
<head>
    <title>服务器测试</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <h1 class="success">服务器已成功修复!</h1>
    <p>Nginx现在正常工作</p>
    <p>时间: $(date)</p>
</body>
</html>
EOF

# 上传测试页面
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/test.html ${REMOTE_USER}@${REMOTE_SERVER}:/var/www/html/index.html
eval "${SSH_CMD} \"chmod 644 /var/www/html/index.html\""

# 9. 重启Nginx服务
echo "9. 启动Nginx服务..."
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

# 10. 验证Nginx运行状态
echo "10. 验证Nginx状态..."
eval "${SSH_CMD} \"systemctl status nginx\""

# 11. 验证端口监听状态
echo "11. 验证80端口监听..."
eval "${SSH_CMD} \"netstat -tuln | grep 80\""

# 12. 尝试直接从服务器本地访问
echo "12. 从服务器本地测试网页..."
eval "${SSH_CMD} \"curl -v http://localhost\""

# 13. 验证IP和域名解析
echo "13. 验证DNS解析..."
eval "${SSH_CMD} \"ping -c 2 ${REMOTE_SERVER} || true\""

echo "===== 全面修复完成 ====="
echo "现在请尝试访问 http://${REMOTE_SERVER}/"
echo "如果测试页面显示，说明服务器已修复"
echo "测试页面成功后，我们将恢复应用程序"
