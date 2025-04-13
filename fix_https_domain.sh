#!/bin/bash

# 修复HTTPS和域名配置
# 处理HTTPS访问和域名临时访问方案

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
DOMAIN="xlct12.com"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 修复HTTPS和域名配置 ====="

# 1. 添加域名到hosts文件（临时解决方案）
echo "1. 添加本地hosts记录（临时方案）..."
echo "请手动执行以下命令修改本地hosts文件："
echo "sudo echo \"${REMOTE_SERVER} ${DOMAIN} www.${DOMAIN}\" >> /etc/hosts"
echo "这将允许您的电脑临时解析域名到正确的IP，直到DNS更新完成"

# 2. 安装SSL证书工具
echo "2. 安装SSL证书工具..."
eval "${SSH_CMD} \"apt-get update && apt-get install -y certbot python3-certbot-nginx\""

# 3. 创建配置文件支持HTTPS
cat << EOF > /tmp/ssl.conf
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
    
    # 自签名证书配置
    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
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
        alias ${REMOTE_DIR}/static;
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
        alias ${REMOTE_DIR}/static;
    }
}
EOF

# 4. 生成自签名证书（一般浏览器会警告，但可以临时使用）
echo "3. 生成自签名SSL证书..."
eval "${SSH_CMD} \"mkdir -p /etc/ssl/private && 
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx-selfsigned.key \
    -out /etc/ssl/certs/nginx-selfsigned.crt \
    -subj '/CN=${DOMAIN}'\""

# 5. 上传配置文件
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/ssl.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/\""

# 6. 开放443端口
echo "4. 确保443端口开放..."
eval "${SSH_CMD} \"iptables -I INPUT -p tcp --dport 443 -j ACCEPT\""

# 7. 重启Nginx服务
echo "5. 重启Nginx服务..."
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

# 8. 检查应用程序是否运行
echo "6. 检查应用程序是否运行..."
eval "${SSH_CMD} \"ps aux | grep 'python3.*app.py' | grep -v grep || (cd ${REMOTE_DIR} && nohup python3 app.py > app.log 2>&1 &)\""

# 9. 检查服务状态
echo "7. 检查服务状态..."
eval "${SSH_CMD} \"systemctl status nginx && netstat -tuln | grep -E '80|443|5001'\""

echo "===== HTTPS配置完成 ====="
echo
echo "现在您可以通过以下方式访问网站："
echo "1. http://${REMOTE_SERVER}/ - 使用IP直接访问（HTTP）"
echo "2. https://${DOMAIN}/ - 使用HTTPS访问域名（需要临时配置hosts或等待DNS更新）"
echo 
echo "注意："
echo "- 使用自签名证书访问HTTPS时，浏览器会显示安全警告，这是正常的"
echo "- 您可以点击'高级'并选择'继续访问'以查看网站"
echo "- 一旦DNS更新完成，可以使用Let's Encrypt申请正式SSL证书"
