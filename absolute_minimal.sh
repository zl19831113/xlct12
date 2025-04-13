#!/bin/bash

# 最简单紧急修复 - 不用任何复杂配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

# 1. 直接用最少的命令将Nginx配置为静态服务器
cat << EOF > /tmp/static.conf
server {
    listen 80 default_server;
    root /var/www/html;
    index index.html;
    server_name _;
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

# 创建测试页面
cat << EOF > /tmp/index.html
<!DOCTYPE html>
<html>
<head>
    <title>服务器测试页面</title>
</head>
<body>
    <h1>服务器正常工作</h1>
    <p>当前时间: $(date)</p>
</body>
</html>
EOF

# 上传并配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/static.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/index.html ${REMOTE_USER}@${REMOTE_SERVER}:/var/www/html/index.html

# 重启Nginx，强制模式
eval "${SSH_CMD} \"pkill -9 -f nginx || true; rm -f /etc/nginx/sites-enabled/*; ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/; nginx -t && nginx\""

# 确保网站开放80端口
eval "${SSH_CMD} \"iptables -I INPUT -p tcp --dport 80 -j ACCEPT\""
