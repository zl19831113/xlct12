#!/bin/bash

# 修复域名和HTTPS配置
# 解决ERR_TUNNEL_CONNECTION_FAILED错误

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
DOMAIN="xlct12.com"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 修复域名和HTTPS问题 ====="

# 1. 检查域名DNS解析情况
echo "1. 检查域名解析..."
dig +short $DOMAIN
nslookup $DOMAIN

# 2. 在服务器上安装certbot获取SSL证书
echo "2. 设置域名和SSL..."
eval "${SSH_CMD} \"apt-get update && apt-get install -y certbot python3-certbot-nginx\""

# 3. 创建正确的nginx配置，支持HTTP重定向到HTTPS
cat << EOF > /tmp/domain.conf
server {
    listen 80;
    listen [::]:80;
    server_name xlct12.com www.xlct12.com;
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name xlct12.com www.xlct12.com;
    
    # SSL配置
    ssl_certificate /etc/letsencrypt/live/xlct12.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xlct12.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    
    # Web根目录
    root /var/www/html;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

# 上传Nginx配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/domain.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/xlct12.conf

# 4. 开放443端口
echo "3. 开放HTTPS端口(443)..."
eval "${SSH_CMD} \"iptables -I INPUT -p tcp --dport 443 -j ACCEPT\""

# 5. 自动获取Let's Encrypt证书 (使用--dry-run进行测试)
echo "4. 尝试获取SSL证书..."
eval "${SSH_CMD} \"certbot --nginx -d xlct12.com -d www.xlct12.com --non-interactive --agree-tos --email admin@xlct12.com || echo '证书获取失败 - 备用计划'\""

# 6. 如果证书获取失败，使用自签名证书
eval "${SSH_CMD} \"if [ ! -f /etc/letsencrypt/live/xlct12.com/fullchain.pem ]; then 
  mkdir -p /etc/ssl/private
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj '/CN=xlct12.com' 
  sed -i 's|/etc/letsencrypt/live/xlct12.com/fullchain.pem|/etc/ssl/certs/nginx-selfsigned.crt|g' /etc/nginx/sites-available/xlct12.conf
  sed -i 's|/etc/letsencrypt/live/xlct12.com/privkey.pem|/etc/ssl/private/nginx-selfsigned.key|g' /etc/nginx/sites-available/xlct12.conf
  echo '已创建自签名证书'
fi\""

# 7. 启用新配置并重启Nginx
echo "5. 应用新配置..."
eval "${SSH_CMD} \"ln -sf /etc/nginx/sites-available/xlct12.conf /etc/nginx/sites-enabled/ && nginx -t && systemctl restart nginx\""

# 8. 将Flask应用配置为使用HTTPS
echo "6. 配置应用使用HTTPS..."
eval "${SSH_CMD} \"cd /var/www/question_bank && pip3 install --break-system-packages flask-talisman && nohup python3 app.py > app.log 2>&1 &\""

echo "===== 域名和HTTPS修复完成 ====="
echo "请尝试访问: https://xlct12.com/"
echo "如果仍无法访问，可能需要:"
echo "1. 检查域名DNS记录是否正确指向 $REMOTE_SERVER"
echo "2. 确认阿里云安全组已开放443端口"
echo "3. 联系阿里云客服获取更多帮助"
