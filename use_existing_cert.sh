#!/bin/bash

# 直接使用已存在的证书
# 修复HTTPS访问

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
DOMAIN="xlct12.com"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 应用现有SSL证书 ====="

# 创建直接使用已知证书的配置
cat << EOF > /tmp/direct_cert.conf
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # 重定向HTTP到HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # 使用已存在的Let's Encrypt证书
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 应用程序代理配置
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}

# 同时保持IP访问可用
server {
    listen 80;
    server_name ${REMOTE_SERVER};
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}
EOF

# 上传并应用配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/direct_cert.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/\""

# 检查配置并重启Nginx
echo "应用配置并重启Nginx..."
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

echo "===== 证书配置完成 ====="
echo "请重新访问 https://${DOMAIN}/ 查看网站是否正常"
echo "证书应该已正确配置，不再显示安全警告"
