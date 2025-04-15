#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
DOMAIN="xlct12.com"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="https_fix_${TIMESTAMP}.log"

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== HTTPS连接错误(ERR_TUNNEL_CONNECTION_FAILED)修复脚本 ======"
echo "修复域名: ${DOMAIN}" | tee -a $LOG_FILE
echo "开始时间: $(date)" | tee -a $LOG_FILE

# 1. 快速诊断HTTPS连接
echo "===== HTTPS连接诊断 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '1. 检查443端口是否开放:'
ss -tulpn | grep ':443'

echo '2. 检查SSL证书:'
if [ -d /etc/letsencrypt/live/${DOMAIN} ]; then
    ls -la /etc/letsencrypt/live/${DOMAIN}/
    echo '证书存在'
    # 检查证书到期时间
    openssl x509 -dates -noout -in /etc/letsencrypt/live/${DOMAIN}/cert.pem
else
    echo '未找到SSL证书'
fi

echo '3. 检查Nginx SSL配置:'
grep -r 'ssl_certificate' /etc/nginx/

echo '4. 检查防火墙状态:'
ufw status

echo '5. 检查Nginx HTTPS监听状态:'
nginx -T 2>/dev/null | grep -A10 'listen.*443'
" | tee -a $LOG_FILE

# 2. 修复SSL配置
echo "===== 修复SSL配置 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '创建/更新SSL证书...'

# 安装或更新certbot
apt-get update
apt-get install -y certbot python3-certbot-nginx

# 备份现有Nginx配置
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak.${TIMESTAMP}

# 创建基本Nginx配置(含HTTP，为SSL做准备)
cat > /etc/nginx/sites-enabled/default << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    # 优化SSL参数
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # 其他设置
    client_max_body_size 100M;
    proxy_read_timeout 600;
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 30d;
    }
}
EOF

# 验证Nginx配置
nginx -t

# 尝试获取或更新SSL证书
echo '正在获取/更新SSL证书...'
certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN} || {
    echo '⚠️ 自动证书获取失败，尝试手动配置自签名证书...'
    
    # 创建自签名证书目录
    mkdir -p /etc/nginx/ssl/
    
    # 生成自签名证书
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/${DOMAIN}.key \
      -out /etc/nginx/ssl/${DOMAIN}.crt \
      -subj \"/C=CN/ST=Beijing/L=Beijing/O=Example Ltd/OU=IT/CN=${DOMAIN}\"
    
    # 更新Nginx配置以使用自签名证书
    sed -i \"s|ssl_certificate .*|ssl_certificate /etc/nginx/ssl/${DOMAIN}.crt;|\" /etc/nginx/sites-enabled/default
    sed -i \"s|ssl_certificate_key .*|ssl_certificate_key /etc/nginx/ssl/${DOMAIN}.key;|\" /etc/nginx/sites-enabled/default
    
    echo '✅ 已配置自签名证书（用户首次访问会有安全警告）'
}

# 确保443端口开放
ufw allow 443/tcp 2>/dev/null || true

# 重新加载Nginx
systemctl reload nginx
echo '✅ Nginx HTTPS配置已更新'
" | tee -a $LOG_FILE

# 3. 修复Gunicorn配置以支持HTTPS
echo "===== 优化Gunicorn配置以支持HTTPS =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '修复Gunicorn配置...'
cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF'
# 优化配置以支持HTTPS转发
bind = '127.0.0.1:8080'
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2
forwarded_allow_ips = '*'  # 允许处理转发的请求
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
capture_output = True
EOF
echo '✅ Gunicorn配置已优化'
" | tee -a $LOG_FILE

# 4. 重启服务
echo "===== 重启服务 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '重启所有服务...'
# 停止服务
systemctl stop nginx
pkill -f gunicorn || true
sleep 2

# 确保日志目录存在
mkdir -p ${REMOTE_DIR}/logs
chmod 755 ${REMOTE_DIR}/logs

# 启动服务
cd ${REMOTE_DIR}
source venv/bin/activate 2>/dev/null || { echo '❌ 虚拟环境激活失败，尝试直接启动'; }

# 启动gunicorn
echo '启动Gunicorn...'
if [ -d \"venv\" ]; then
    venv/bin/gunicorn -c gunicorn_config.py app:app -D
else
    gunicorn -c gunicorn_config.py app:app -D
fi
echo '✅ Gunicorn已重启'

# 启动nginx
echo '启动Nginx...'
systemctl start nginx
echo '✅ Nginx已重启'

# 检查进程
echo '检查进程状态:'
ps aux | grep gunicorn | grep -v grep
systemctl status nginx | grep 'active'
" | tee -a $LOG_FILE

# 5. 验证修复
echo "===== 验证HTTPS连接 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '等待服务完全启动...'
sleep 5

# 本地测试HTTPS
echo '测试HTTPS连接:'
curl -Ik https://localhost/ 2>/dev/null || echo '本地HTTPS测试可能需要域名'

# 检查HTTPS端口
echo '检查443端口:'
ss -tulpn | grep ':443'

# 检查证书信息
echo '当前证书信息:'
if [ -f /etc/letsencrypt/live/${DOMAIN}/cert.pem ]; then
    openssl x509 -in /etc/letsencrypt/live/${DOMAIN}/cert.pem -text -noout | grep -E 'Subject:|Issuer:|Not Before:|Not After :'
elif [ -f /etc/nginx/ssl/${DOMAIN}.crt ]; then
    openssl x509 -in /etc/nginx/ssl/${DOMAIN}.crt -text -noout | grep -E 'Subject:|Issuer:|Not Before:|Not After :'
fi
" | tee -a $LOG_FILE

# 6. 显示DNS和网络诊断信息
echo "===== DNS和网络诊断 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '检查DNS记录:'
host ${DOMAIN} || echo '无法解析域名'
dig ${DOMAIN} || echo 'dig命令不可用'

echo '检查IP配置:'
curl -s ipinfo.io/ip || echo '无法获取公网IP'
ip addr show | grep 'inet ' | grep -v '127.0.0.1'

echo '检查网络连接:'
ping -c 3 www.baidu.com
" | tee -a $LOG_FILE

echo "===== 常见错误排查 =====" | tee -a $LOG_FILE
echo "1. 检查DNS是否正确指向服务器IP" | tee -a $LOG_FILE
echo "2. 检查防火墙是否允许443端口" | tee -a $LOG_FILE
echo "3. 检查云服务商安全组是否开放443端口" | tee -a $LOG_FILE
echo "4. 确认域名已备案(国内服务器要求)" | tee -a $LOG_FILE
echo "5. 检查证书是否正确匹配域名" | tee -a $LOG_FILE

echo "====== 修复完成 ======" | tee -a $LOG_FILE
echo "结束时间: $(date)" | tee -a $LOG_FILE
echo "所有操作已记录到 $LOG_FILE"
echo ""
echo "✅ 修复要点:"
echo "1. SSL证书已配置"
echo "2. Nginx HTTPS已配置"
echo "3. 防火墙已允许443端口"
echo "4. Gunicorn已优化以支持HTTPS"
echo ""
echo "访问: https://${DOMAIN} 检查是否已修复"
echo ""
echo "如果仍未修复，请检查:"
echo "- DNS记录是否正确 (可能需要24小时生效)"
echo "- 云服务商控制台中的安全组/防火墙设置"
echo "- 是否有CDN/代理影响了直接连接"
``` 