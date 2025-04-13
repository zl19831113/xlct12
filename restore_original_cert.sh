#!/bin/bash

# 恢复使用原始SSL证书
# 检测并配置正确的证书路径

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
DOMAIN="xlct12.com"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 恢复原始SSL证书 ====="

# 1. 查找服务器上所有证书文件
echo "1. 查找所有证书文件..."
eval "${SSH_CMD} \"find /etc -name '*.crt' -o -name '*.pem' | grep -v 'nginx-selfsigned'\""

# 2. 查找服务器上原始的Nginx配置
echo "2. 查找原始Nginx SSL配置..."
eval "${SSH_CMD} \"find /etc/nginx -type f -name '*.conf*' | xargs grep -l 'ssl_certificate' | grep -v 'nginx-selfsigned'\""

# 3. 备份当前Nginx配置
echo "3. 备份当前Nginx配置..."
eval "${SSH_CMD} \"cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak.$(date +%s)\""

# 4. 创建使用原始证书的配置
cat << EOF > /tmp/original_ssl.conf
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # 使用Let's Encrypt标准路径(如果存在)
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    # 如果Let's Encrypt路径不存在，脚本会在下一步自动更新为正确路径
    
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

# 上传配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/original_ssl.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default

# 5. 自动检测并修复证书路径
echo "4. 检测并修复证书路径..."
eval "${SSH_CMD} \"
cert_files=\\\$(find /etc -name '*.crt' -o -name '*.pem' | grep -i -e '${DOMAIN}' -e 'ssl')
key_files=\\\$(find /etc -name '*.key' | grep -i -e '${DOMAIN}' -e 'ssl')

if [[ -f /etc/letsencrypt/live/${DOMAIN}/fullchain.pem && -f /etc/letsencrypt/live/${DOMAIN}/privkey.pem ]]; then
    echo 'Let\\'s Encrypt证书已存在，使用标准路径'
elif [[ -n \\\"\\\$cert_files\\\" && -n \\\"\\\$key_files\\\" ]]; then
    cert_file=\\\$(echo \\\"\\\$cert_files\\\" | head -1)
    key_file=\\\$(echo \\\"\\\$key_files\\\" | head -1)
    echo '找到原始证书文件: '\\\$cert_file' 和 '\\\$key_file
    sed -i 's|ssl_certificate .*|ssl_certificate '\\\$cert_file';|' /etc/nginx/sites-available/default
    sed -i 's|ssl_certificate_key .*|ssl_certificate_key '\\\$key_file';|' /etc/nginx/sites-available/default
else
    echo '未找到原始证书，保持现有配置'
fi\""

# 6. 重启Nginx服务
echo "5. 重启Nginx服务..."
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

echo "===== 原始SSL证书恢复完成 ====="
echo "请重新访问 https://${DOMAIN}/ 查看证书是否正确"
echo "如果仍有证书错误，请提供原始证书的具体路径"
