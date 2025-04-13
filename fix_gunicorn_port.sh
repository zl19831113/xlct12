#!/bin/bash
# 修复Gunicorn和Nginx端口配置问题

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始修复Gunicorn和Nginx端口配置 ====="

# 1. 停止所有相关服务
echo "停止所有相关服务..."
systemctl stop question_bank
systemctl stop nginx

# 2. 杀掉所有旧的Gunicorn进程
echo "杀掉所有旧的Gunicorn进程..."
pkill -f gunicorn || true
sleep 2

# 3. 修改Gunicorn配置文件
echo "修改Gunicorn配置文件..."
cat > /var/www/question_bank/gunicorn_config.py << 'GUNICORN'
# 工作进程数
workers = 4

# 绑定到端口5001
bind = '127.0.0.1:5001'

# 工作模式
worker_class = 'sync'

# 超时时间
timeout = 120

# 访问日志和错误日志
accesslog = '/var/www/question_bank/logs/access.log'
errorlog = '/var/www/question_bank/logs/error.log'

# 增加调试信息
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True

# 确保工作进程能够正确启动
preload_app = True
reload = True
GUNICORN

# 4. 确保日志目录存在
echo "确保日志目录存在..."
mkdir -p /var/www/question_bank/logs

# 5. 修改systemd服务配置
echo "修改systemd服务配置..."
cat > /etc/systemd/system/question_bank.service << 'SERVICE'
[Unit]
Description=Question Bank Web Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/question_bank
ExecStart=/var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# 6. 确保Nginx配置正确
echo "确保Nginx配置正确..."
cat > /etc/nginx/sites-available/default << 'NGINX'
server {
    listen 80;
    listen [::]:80;
    server_name xlct12.com www.xlct12.com;
    
    # 重定向HTTP到HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name xlct12.com www.xlct12.com;
    
    # 使用已存在的Let's Encrypt证书
    ssl_certificate /etc/letsencrypt/live/xlct12.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/xlct12.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 应用程序代理配置 - 确保端口是5001
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}

# 同时保持IP访问可用
server {
    listen 80;
    server_name 120.26.12.100;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}
NGINX

# 7. 重新加载systemd配置
echo "重新加载systemd配置..."
systemctl daemon-reload

# 8. 启动服务
echo "启动服务..."
systemctl start question_bank
systemctl start nginx

# 9. 等待服务启动
echo "等待服务启动..."
sleep 5

# 10. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20
systemctl status nginx | head -10

# 11. 检查端口监听情况
echo "检查端口监听情况..."
netstat -tlnp | grep 5001

# 12. 测试本地访问
echo "测试本地访问..."
curl -s http://localhost:5001/ | head -20

echo "===== Gunicorn和Nginx端口配置修复完成 ====="
EOF
