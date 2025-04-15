#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="502_fix_${TIMESTAMP}.log"

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== Nginx 1.24.0 (Ubuntu) 502错误专用修复脚本 ======"
echo "开始时间: $(date)" | tee -a $LOG_FILE

# 1. 快速检查 - 仅检查核心问题
echo "===== 快速诊断 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '1. Nginx状态检查:'
systemctl status nginx | grep 'active' 
echo '2. Gunicorn进程检查:'
ps aux | grep gunicorn | grep -v grep
echo '3. 检查连接:'
ss -tunap | grep 8080
echo '4. 检查Nginx错误日志最后10行:'
tail -n 10 /var/log/nginx/error.log
" | tee -a $LOG_FILE

# 2. 应用专用修复
echo "===== 应用专用修复 =====" | tee -a $LOG_FILE

# 2.1 修复Socket权限问题 (常见原因)
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '修复Socket权限问题...'
find ${REMOTE_DIR} -type s -exec chmod 777 {} \; 2>/dev/null || true
" | tee -a $LOG_FILE

# 2.2 修复Nginx到Gunicorn的连接问题
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '修复Nginx连接配置...'
cat > /etc/nginx/sites-enabled/default << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;
    
    # 扩展超时设置
    proxy_read_timeout 600;
    proxy_connect_timeout 600;
    proxy_send_timeout 600;
    
    # 增加缓冲区设置
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_intercept_errors on;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 30d;
    }
    
    # 增加错误页面
    error_page 502 /502.html;
    location = /502.html {
        root /usr/share/nginx/html;
        internal;
    }
}
EOF
echo '✅ Nginx配置已优化'
" | tee -a $LOG_FILE

# 2.3 修复Gunicorn配置 - 优化健壮性
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '修复Gunicorn配置...'
cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF'
# Nginx 1.24.0 (Ubuntu)专用优化配置
bind = '127.0.0.1:8080'
workers = 4  # 增加工作进程
worker_class = 'sync'  # 使用同步工作进程
worker_connections = 1000
timeout = 300  # 增加超时时间
keepalive = 2  # 保持连接
max_requests = 1000  # 限制最大请求数以防内存泄漏
max_requests_jitter = 100
graceful_timeout = 60
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
preload_app = False  # 设为False以避免内存问题
EOF
echo '✅ Gunicorn配置已优化'
" | tee -a $LOG_FILE

# 2.4 强制重启服务
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '强制重启所有服务...'
# 停止服务
systemctl stop nginx
pkill -9 -f gunicorn || true
sleep 2

# 清理旧的sock文件
find ${REMOTE_DIR} -name '*.sock' -delete 2>/dev/null || true

# 确保日志目录存在并有权限
mkdir -p ${REMOTE_DIR}/logs
chmod 755 ${REMOTE_DIR}/logs
chown -R www-data:www-data ${REMOTE_DIR}/logs 2>/dev/null || true

# 启动服务
cd ${REMOTE_DIR}
source venv/bin/activate || { echo '❌ 虚拟环境激活失败'; exit 1; }
# 使用nohup确保gunicorn不会被SSH会话终止影响
nohup gunicorn -c gunicorn_config.py app:app --preload > ${REMOTE_DIR}/logs/startup.log 2>&1 &
echo $! > ${REMOTE_DIR}/gunicorn.pid
echo '✅ Gunicorn已重启'

# 启动nginx前检查配置
nginx -t && systemctl start nginx
echo '✅ Nginx已重启'

# 检查进程
echo '检查进程状态:'
ps aux | grep gunicorn | grep -v grep
systemctl status nginx | grep 'active'
" | tee -a $LOG_FILE

# 3. 验证修复
echo "===== 验证修复 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '等待服务完全启动...'
sleep 10

# 检查gunicorn是否响应
echo '测试Gunicorn响应:'
curl -v http://localhost:8080/ -o /dev/null 2>&1 | grep '< HTTP'

# 检查nginx是否响应
echo '测试Nginx响应:'
curl -v http://localhost/ -o /dev/null 2>&1 | grep '< HTTP'

# 检查内存使用情况
echo '检查内存使用:'
free -m
" | tee -a $LOG_FILE

echo "===== 收集诊断信息 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
echo '最近错误日志:'
echo '--- Nginx错误日志 ---'
tail -n 20 /var/log/nginx/error.log
echo '--- Gunicorn错误日志 ---'
tail -n 20 ${REMOTE_DIR}/logs/error.log
echo '--- Flask启动日志 ---'
tail -n 20 ${REMOTE_DIR}/logs/startup.log 2>/dev/null || echo '日志文件不存在'
" | tee -a $LOG_FILE

echo "====== 修复完成 ======" | tee -a $LOG_FILE
echo "结束时间: $(date)" | tee -a $LOG_FILE
echo "所有操作和诊断已记录到 $LOG_FILE"
echo "如果仍有问题, 查看日志文件找出根本原因"
echo "你还可以运行以下命令实时监控:"
echo "- 查看Nginx错误: ${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} \"tail -f /var/log/nginx/error.log\""
echo "- 查看应用错误: ${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} \"tail -f ${REMOTE_DIR}/logs/error.log\"" 