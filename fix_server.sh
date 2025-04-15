#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== 开始一键修复 502 Bad Gateway (${TIMESTAMP}) ======"

# 1. 确保目录存在
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}/logs"

# 2. 更新依赖
echo "===== 修复依赖冲突 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && source venv/bin/activate && pip install --upgrade pip && pip install Flask==2.0.1 flask_sqlalchemy==2.5.1 gunicorn==20.1.0 werkzeug==2.0.1 --no-cache-dir"

# 3. 备份并修复gunicorn配置
echo "===== 修复 gunicorn 配置 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
if [ -f \"${REMOTE_DIR}/gunicorn_config.py\" ]; then
    cp ${REMOTE_DIR}/gunicorn_config.py ${REMOTE_DIR}/gunicorn_config.py.bak
    cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF'
bind = '0.0.0.0:8080'
workers = 3
timeout = 120
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
EOF
    echo '✅ gunicorn 配置已修复'
else
    cat > ${REMOTE_DIR}/gunicorn_config.py << 'EOF'
bind = '0.0.0.0:8080'
workers = 3
timeout = 120
accesslog = './logs/access.log'
errorlog = './logs/error.log'
loglevel = 'debug'
EOF
    echo '✅ gunicorn 配置已创建'
fi
"

# 4. 确保nginx配置正确
echo "===== 修复 nginx 配置 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak
cat > /etc/nginx/sites-enabled/default << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 30d;
    }
}
EOF
echo '✅ nginx 配置已修复'
"

# 5. 重启服务
echo "===== 重启服务 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
# 停止所有现有的gunicorn进程
pkill -f gunicorn || true
sleep 2

# 重新启动gunicorn
cd ${REMOTE_DIR}
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app -D --log-level debug
echo '✅ gunicorn 已重启'

# 验证gunicorn是否启动
ps aux | grep -i gunicorn | grep -v grep

# 重启nginx
systemctl restart nginx
echo '✅ nginx 已重启'
"

# 6. 验证服务是否正常运行
echo "===== 验证服务 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
sleep 3
# 检查gunicorn是否响应
curl -s http://localhost:8080 > /dev/null
if [ \$? -eq 0 ]; then
    echo '✅ gunicorn 响应正常'
else
    echo '❌ gunicorn 响应异常，检查日志'
    tail -n 20 ${REMOTE_DIR}/logs/error.log
fi

# 检查nginx是否响应
curl -s http://localhost > /dev/null
if [ \$? -eq 0 ]; then
    echo '✅ nginx 响应正常'
else
    echo '❌ nginx 响应异常，检查日志'
    tail -n 20 /var/log/nginx/error.log
fi
"

echo "====== 修复完成 (${TIMESTAMP}) ======"
echo "如果页面仍然显示502错误，请运行以下命令检查具体错误："
echo "- 检查gunicorn日志: ${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} \"tail -f ${REMOTE_DIR}/logs/error.log\""
echo "- 检查nginx日志: ${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} \"tail -f /var/log/nginx/error.log\"" 