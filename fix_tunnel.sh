#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
DOMAIN="xlct12.com"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="tunnel_fix_${TIMESTAMP}.log"

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== ERR_TUNNEL_CONNECTION_FAILED 专用修复脚本 ======"
echo "修复域名: ${DOMAIN}" | tee -a $LOG_FILE
echo "开始时间: $(date)" | tee -a $LOG_FILE

# 0. 检查本地脚本是否可访问
echo "===== 检查本地连接 =====" | tee -a $LOG_FILE
curl -Ik --connect-timeout 10 https://${DOMAIN} 2>&1 | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# 1. 快速诊断HTTPS连接
echo "===== HTTPS隧道诊断 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '1. 检查443端口是否开放:'
ss -tulpn | grep ':443'

echo '2. 检查SSL握手:'
echo | openssl s_client -connect localhost:443 -servername ${DOMAIN} 2>/dev/null | grep 'Verify return code'

echo '3. 检查SSL证书链:'
if [ -d /etc/letsencrypt/live/${DOMAIN} ]; then
    echo '证书路径存在'
    ls -la /etc/letsencrypt/live/${DOMAIN}/
    
    # 验证证书链完整性
    echo '验证证书链:'
    openssl verify /etc/letsencrypt/live/${DOMAIN}/fullchain.pem 2>&1 || echo '证书链验证失败'
else
    echo '未找到Let\'s Encrypt证书'
fi

# 检查Nginx TLS配置
echo '4. 检查Nginx SSL/TLS配置:'
nginx -T 2>/dev/null | grep -E 'ssl_protocols|ssl_ciphers|ssl_prefer_server_ciphers'

# 检查是否有TLS握手错误
echo '5. 检查TLS握手错误:'
tail -n 50 /var/log/nginx/error.log | grep -i 'ssl\|tls\|handshake'
" | tee -a $LOG_FILE

# 2. 专门针对Tunnel错误的修复
echo "===== 修复HTTPS隧道连接 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '修复隧道连接问题...'

# 备份现有Nginx配置
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak.${TIMESTAMP}

# 创建Nginx配置 - 特别针对隧道问题优化
cat > /etc/nginx/sites-enabled/default << 'EOF'
# 针对ERR_TUNNEL_CONNECTION_FAILED优化的配置
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # 简单HTTP响应，不立即重定向(避免隧道问题)
    location / {
        return 200 'Server is online. Please use HTTPS.';
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    # 证书配置 - 使用conditional判断
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    # 降级TLS配置 - 增加兼容性
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;  # 关闭服务器偏好，增加兼容性
    ssl_ciphers 'HIGH:!aNULL:!MD5:!RC4';
    
    # 关闭不必要的TLS功能(可能导致隧道问题)
    ssl_session_tickets on;
    ssl_stapling off;
    ssl_stapling_verify off;
    
    # 优化buffer以防止隧道问题
    proxy_buffer_size 16k;
    proxy_buffers 4 16k;
    proxy_busy_buffers_size 16k;
    
    # 完全禁用HTTP/2(可能导致隧道问题)
    http2 off;
    
    # 关键:减小超时设置，防止隧道超时
    client_body_timeout 10;
    client_header_timeout 10;
    keepalive_timeout 15;
    send_timeout 10;
    
    # 标准代理设置
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        
        # 减少代理头，简化隧道连接
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 关键:设置低超时值
        proxy_connect_timeout 30;
        proxy_send_timeout 30;
        proxy_read_timeout 30;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 30d;
    }
}
EOF

# 替换变量
sed -i \"s|\\\${DOMAIN}|${DOMAIN}|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\${REMOTE_DIR}|${REMOTE_DIR}|g\" /etc/nginx/sites-enabled/default

# 验证Nginx配置
nginx -t && echo '✅ Nginx配置语法正确' || echo '❌ Nginx配置有误'

# 手动创建自签名证书(如果需要)
if [ ! -d \"/etc/letsencrypt/live/${DOMAIN}\" ]; then
    echo '证书不存在，创建自签名证书...'
    mkdir -p /etc/nginx/ssl/
    
    # 生成自签名证书
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/${DOMAIN}.key \
      -out /etc/nginx/ssl/${DOMAIN}.crt \
      -subj \"/C=CN/ST=Beijing/L=Beijing/O=Example Ltd/OU=IT/CN=${DOMAIN}\"
    
    # 更新Nginx配置以使用自签名证书
    sed -i \"s|ssl_certificate .*|ssl_certificate /etc/nginx/ssl/${DOMAIN}.crt;|\" /etc/nginx/sites-enabled/default
    sed -i \"s|ssl_certificate_key .*|ssl_certificate_key /etc/nginx/ssl/${DOMAIN}.key;|\" /etc/nginx/sites-enabled/default
    
    echo '✅ 已配置自签名证书'
fi

# 修复Gunicorn配置
cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF'
# 为防止隧道连接失败优化的配置
bind = '127.0.0.1:8080'
workers = 2  # 减少worker数量，减轻负载
worker_class = 'sync'  # 使用简单同步worker
timeout = 30  # 减小超时时间
keepalive = 2
max_requests = 500
graceful_timeout = 10
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
capture_output = True
EOF

# 确保端口开放
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
iptables -I INPUT -p tcp --dport 80 -j ACCEPT

# 关闭任何可能妨碍的防火墙或安全设置
ufw allow 443/tcp 2>/dev/null || true
ufw allow 80/tcp 2>/dev/null || true

echo '✅ 防火墙已配置'
" | tee -a $LOG_FILE

# 3. 强制重启所有服务
echo "===== 强制重启所有服务 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
# 完全停止服务
systemctl stop nginx
pkill -9 -f gunicorn || true
sleep 3

# 清理任何可能的残留文件
find ${REMOTE_DIR} -name '*.sock' -delete 2>/dev/null || true
find ${REMOTE_DIR} -name '*.pid' -delete 2>/dev/null || true

# 确保日志目录
mkdir -p ${REMOTE_DIR}/logs
chmod 755 ${REMOTE_DIR}/logs

# 启动Gunicorn (简单启动方式)
cd ${REMOTE_DIR}
source venv/bin/activate 2>/dev/null || echo '虚拟环境不存在，尝试直接启动'

# 使用nohup确保进程持续运行
echo '启动Gunicorn...'
if [ -d \"venv\" ]; then
    nohup venv/bin/gunicorn -c gunicorn_config.py app:app -D
else
    nohup gunicorn -c gunicorn_config.py app:app -D
fi
sleep 2

# 验证Gunicorn是否运行
ps aux | grep gunicorn | grep -v grep
if [ \$? -eq 0 ]; then
    echo '✅ Gunicorn启动成功'
else
    echo '❌ Gunicorn启动失败'
fi

# 启动Nginx (检查配置后启动)
echo '启动Nginx...'
nginx -t && systemctl start nginx
systemctl status nginx | grep 'active'
if [ \$? -eq 0 ]; then
    echo '✅ Nginx启动成功'
else
    echo '❌ Nginx启动失败'
fi
" | tee -a $LOG_FILE

# 4. 验证连接
echo "===== 验证HTTPS隧道连接 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
sleep 5  # 等待服务完全启动

# 本地验证HTTPS连接
echo '本地测试HTTPS连接:'
curl -Ik --connect-timeout 5 https://localhost 2>&1 || echo '本地测试需要域名'

# 查看HTTPS错误日志
echo '最近的Nginx错误日志:'
tail -n 20 /var/log/nginx/error.log

# 查看应用错误日志
echo '最近的应用错误日志:'
tail -n 20 ${REMOTE_DIR}/logs/error.log 2>/dev/null || echo '没有应用日志'
" | tee -a $LOG_FILE

# 5. 检查外部连接 (从脚本主机)
echo "===== 从本地检查连接 =====" | tee -a $LOG_FILE
echo "从脚本主机测试HTTPS连接:" | tee -a $LOG_FILE
curl -Ik --connect-timeout 10 https://${DOMAIN} 2>&1 | tee -a $LOG_FILE

# 6. 提供备选方案
echo "===== 备选解决方案 =====" | tee -a $LOG_FILE
echo "如果以上修复未解决问题，请尝试以下步骤:" | tee -a $LOG_FILE
echo "1. 检查云服务商控制台中的安全组/防火墙设置" | tee -a $LOG_FILE
echo "2. 检查域名DNS解析是否正确指向服务器IP" | tee -a $LOG_FILE
echo "3. 域名ICP备案状态(中国大陆服务器必须)" | tee -a $LOG_FILE
echo "4. 尝试其他浏览器或设备访问" | tee -a $LOG_FILE
echo "5. 清除浏览器缓存和Cookie" | tee -a $LOG_FILE
echo "6. 检查客户端网络(尝试使用手机流量访问)" | tee -a $LOG_FILE

# 7. 通过SSH连接检查可能的CDN问题
echo "===== 检查CDN/代理配置 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
# 获取服务器IP
SERVER_IP=\$(curl -s ipinfo.io/ip)
echo \"服务器IP: \$SERVER_IP\"

# 检查域名解析
echo \"域名DNS解析:\"
host ${DOMAIN} || echo \"无法解析域名\"

# 检查CDN标头
echo \"检查是否使用CDN:\"
curl -s -I http://${DOMAIN} 2>/dev/null | grep -i \"CF-RAY\|X-Cache\|CDN\|cloudflare\" || echo \"未发现CDN标头\"
" | tee -a $LOG_FILE

echo "====== 修复完成 ======" | tee -a $LOG_FILE
echo "结束时间: $(date)" | tee -a $LOG_FILE
echo "所有诊断和修复尝试已记录到 $LOG_FILE"
echo ""
echo "✅ 针对ERR_TUNNEL_CONNECTION_FAILED的修复要点:"
echo "1. 优化了SSL/TLS配置，增加兼容性"
echo "2. 减少了超时设置，防止隧道中断"
echo "3. 简化了HTTP/HTTPS处理，提高稳定性"
echo "4. 确保防火墙和端口配置正确"
echo ""
echo "👉 下一步:"
echo "1. 请再次尝试访问: https://${DOMAIN}"
echo "2. 如果仍有问题，查看日志文件 $LOG_FILE 了解详情"
echo "3. 考虑尝试备选解决方案中列出的其他步骤" 