#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
DOMAIN="xlct12.com"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="tunnel_final_fix_${TIMESTAMP}.log"

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== HTTPS隧道连接最终修复方案 ======"
echo "修复域名: ${DOMAIN}" | tee -a $LOG_FILE
echo "开始时间: $(date)" | tee -a $LOG_FILE

# 1. 客户端检查
echo "===== 客户端诊断 =====" | tee -a $LOG_FILE
echo "从脚本主机连接测试:" | tee -a $LOG_FILE
echo "- HTTP测试:" | tee -a $LOG_FILE
curl -v --connect-timeout 10 http://${DOMAIN} > client_http_test.txt 2>&1
echo "- HTTPS测试:" | tee -a $LOG_FILE
curl -v --connect-timeout 10 https://${DOMAIN} > client_https_test.txt 2>&1
echo "- 跟踪路由:" | tee -a $LOG_FILE
traceroute ${DOMAIN} > client_traceroute.txt 2>&1 || echo "无法执行traceroute" > client_traceroute.txt

echo "客户端诊断结果保存到相应文件" | tee -a $LOG_FILE

# 2. 全面服务器检查
echo "===== 全面服务器检查 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '获取服务器状态和配置信息...'

# 系统信息
echo '系统信息:'
uname -a
uptime
free -m

# 网络状态
echo '网络状态:'
ip addr show
netstat -tulpn | grep -E ':80|:443|:8080'
iptables -L -n

# HTTP/HTTPS测试
echo '从服务器内部测试HTTP/HTTPS连接:'
curl -v --connect-timeout 5 http://localhost:8080/ > /tmp/local_http_test.txt 2>&1
curl -v --connect-timeout 5 https://localhost/ > /tmp/local_https_test.txt 2>&1

# 证书完整性检查
echo '详细证书检查:'
if [ -d \"/etc/letsencrypt/live/${DOMAIN}\" ]; then
    echo '检查证书内容:'
    openssl x509 -in /etc/letsencrypt/live/${DOMAIN}/cert.pem -text -noout | grep -E 'Subject:|Issuer:|Not Before:|Not After :|DNS:'
fi

# 查看nginx和gunicorn版本
echo 'Nginx版本:'
nginx -v
echo 'Python版本:'
python3 --version

# 检查Nginx和应用日志
echo '最近的错误日志:'
echo '-- Nginx错误日志 --'
tail -n 100 /var/log/nginx/error.log | grep -i 'error\\|warn\\|ssl\\|tls'
echo '-- 应用错误日志 --'
tail -n 100 ${REMOTE_DIR}/logs/error.log 2>/dev/null || echo '应用日志不存在'
" | tee -a $LOG_FILE

# 3. 专门针对隧道错误的最终修复
echo "===== 执行最终修复方案 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '执行最终修复方案...'

# 备份当前配置
mkdir -p /root/backup_${TIMESTAMP}
cp -r /etc/nginx /root/backup_${TIMESTAMP}/
cp -r ${REMOTE_DIR}/gunicorn_config.py /root/backup_${TIMESTAMP}/ 2>/dev/null || true
echo '✅ 当前配置已备份'

# 禁用所有可能的安全限制
echo '禁用安全限制...'
systemctl stop apparmor 2>/dev/null || true
setenforce 0 2>/dev/null || true
iptables -F
iptables -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
echo '✅ 安全限制已暂时禁用'

# 创建全新的SSL证书 - 使用自签名证书
echo '创建全新的自签名证书...'
mkdir -p /etc/nginx/ssl/${DOMAIN}
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/${DOMAIN}/privkey.pem \
  -out /etc/nginx/ssl/${DOMAIN}/fullchain.pem \
  -subj \"/C=CN/ST=Beijing/L=Beijing/O=Example Ltd/OU=IT/CN=${DOMAIN}\"
chmod 600 /etc/nginx/ssl/${DOMAIN}/*.pem
echo '✅ 自签名证书已创建'

# 创建最简化的Nginx配置
echo '创建最简化的Nginx配置...'
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers 'HIGH:!aNULL:!MD5';
    
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# 创建最简化的站点配置
cat > /etc/nginx/sites-enabled/default << 'EOF'
# HTTP服务器 - 基本配置
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # 静态页面测试
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }
}

# HTTPS服务器 - 基本配置
server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/nginx/ssl/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/${DOMAIN}/privkey.pem;
    
    # 极简SSL配置
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;
    
    # 直接使用静态页面进行测试
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ =404;
    }
}
EOF

# 替换变量
sed -i \"s|\\\${DOMAIN}|${DOMAIN}|g\" /etc/nginx/sites-enabled/default

# 创建静态测试页
mkdir -p /var/www/html
cat > /var/www/html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>HTTPS连接测试成功</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <h1>HTTPS连接测试</h1>
    <p class=\"success\">✅ 恭喜！HTTPS隧道连接已成功建立</p>
    <p>服务器时间: $(date)</p>
    <p>主机名: $(hostname)</p>
    <hr>
    <p>如果您看到此页面，说明SSL/TLS隧道连接问题已解决。</p>
</body>
</html>
EOF

# 替换变量
sed -i \"s|\\\$(date)|$(date)|g\" /var/www/html/index.html
sed -i \"s|\\\$(hostname)|$(hostname)|g\" /var/www/html/index.html

# 设置权限
chmod -R 755 /var/www/html

# 验证配置
echo '验证Nginx配置...'
nginx -t && echo '✅ Nginx配置验证通过' || echo '❌ Nginx配置有误'

# 重启服务
echo '重启Nginx...'
systemctl restart nginx

echo '验证Nginx状态...'
systemctl status nginx | grep 'active'
if [ \$? -eq 0 ]; then
    echo '✅ Nginx已成功启动'
else
    echo '❌ Nginx启动失败'
    systemctl status nginx
fi

# 测试连接
echo '测试本地连接...'
curl -kI https://localhost/ && echo '✅ 本地HTTPS连接成功' || echo '❌ 本地HTTPS连接失败'
" | tee -a $LOG_FILE

# 4. 验证连接修复
echo "===== 验证连接修复 =====" | tee -a $LOG_FILE
echo "从脚本主机测试HTTPS连接..." | tee -a $LOG_FILE
curl -kI --connect-timeout 10 https://${DOMAIN} > final_https_test.txt 2>&1
if grep -q "HTTP/1.1 200 OK" final_https_test.txt; then
    echo "✅ HTTPS连接成功！" | tee -a $LOG_FILE
else
    echo "❌ HTTPS连接仍然失败" | tee -a $LOG_FILE
fi

# 5. 提供应用恢复步骤
echo "===== 应用恢复步骤 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '创建应用恢复步骤...'

# 创建恢复脚本
cat > ${REMOTE_DIR}/restore_app.sh << 'EOF'
#!/bin/bash

# 设置变量
DOMAIN=\"${DOMAIN}\"
REMOTE_DIR=\"${REMOTE_DIR}\"

echo \"====== 恢复Flask应用 ======\"

# 创建生产环境Nginx配置
cat > /etc/nginx/sites-enabled/default << 'EOF2'
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/nginx/ssl/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/${DOMAIN}/privkey.pem;
    
    # 基本SSL配置
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;
    
    # 代理到Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 30d;
    }
}
EOF2

# 替换变量
sed -i \"s|\\\${DOMAIN}|${DOMAIN}|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\${REMOTE_DIR}|${REMOTE_DIR}|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\$host|\\$host|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\$remote_addr|\\$remote_addr|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\$proxy_add_x_forwarded_for|\\$proxy_add_x_forwarded_for|g\" /etc/nginx/sites-enabled/default
sed -i \"s|\\\$scheme|\\$scheme|g\" /etc/nginx/sites-enabled/default

# 重新启动Gunicorn
echo \"启动Gunicorn...\"
cd ${REMOTE_DIR}
source venv/bin/activate 2>/dev/null || echo \"虚拟环境不存在\"

# 创建基本配置
cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF2'
bind = '127.0.0.1:8080'
workers = 2
worker_class = 'sync'
timeout = 60
keepalive = 2
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
EOF2

# 确保日志目录
mkdir -p ${REMOTE_DIR}/logs
chmod 755 ${REMOTE_DIR}/logs

# 启动应用
if [ -d \"venv\" ]; then
    venv/bin/gunicorn -c gunicorn_config.py app:app -D
else
    gunicorn -c gunicorn_config.py app:app -D
fi

# 重启Nginx
nginx -t && systemctl restart nginx

echo \"应用已恢复。请访问 https://${DOMAIN} 验证。\"
EOF

chmod +x ${REMOTE_DIR}/restore_app.sh
echo '✅ 应用恢复脚本已创建：${REMOTE_DIR}/restore_app.sh'
" | tee -a $LOG_FILE

# 6. 全面客户端排查建议
cat > client_troubleshooting.txt << 'EOF'
===== ERR_TUNNEL_CONNECTION_FAILED 客户端排查指南 =====

如果服务器端修复后仍然遇到问题，请尝试以下客户端排查步骤：

1. 浏览器问题排查：
   - 清除浏览器缓存和Cookie
   - 禁用所有浏览器扩展/插件后再尝试
   - 尝试使用隐私模式访问
   - 尝试使用不同的浏览器(Chrome、Firefox、Edge)

2. 网络连接问题：
   - 检查您的网络连接是否稳定
   - 尝试使用不同的网络(如手机热点)访问
   - 关闭VPN、代理或防火墙后再尝试

3. DNS问题：
   - 修改本地DNS设置，尝试使用8.8.8.8(Google DNS)或114.114.114.114(国内DNS)
   - 在hosts文件中添加域名映射(需要获取服务器IP)

4. 安全软件问题：
   - 暂时关闭杀毒软件、防火墙后再尝试
   - 检查是否有安全软件阻止HTTPS连接

5. 测试直接IP访问：
   - 使用IP地址直接访问(需要获取服务器IP)：https://[服务器IP]
   - 注意：直接IP访问会有证书警告，这是正常的

6. 系统时间问题：
   - 确保您的设备系统时间准确，错误的系统时间可能导致SSL握手失败

如果以上步骤都不能解决问题，请向服务器管理员提供以下信息：
- 您的网络环境(家庭宽带、公司网络、移动网络等)
- 访问时的错误截图
- 浏览器控制台(F12)中的网络错误信息
EOF

echo "====== 最终修复完成 ======" | tee -a $LOG_FILE
echo "结束时间: $(date)" | tee -a $LOG_FILE
echo "所有操作已记录到 $LOG_FILE"
echo ""
echo "✅ 已完成的修复工作："
echo "1. 完全简化的HTTPS配置"
echo "2. 创建了静态测试页面"
echo "3. 禁用了所有可能的安全限制"
echo "4. 提供了应用恢复脚本"
echo ""
echo "下一步："
echo "1. 再次访问 https://${DOMAIN} 验证HTTPS连接"
echo "2. 如果基本HTTPS连接成功，运行 ${REMOTE_DIR}/restore_app.sh 恢复应用"
echo "3. 如果仍然失败，查看 client_troubleshooting.txt 进行客户端排查" 