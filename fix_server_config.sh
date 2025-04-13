#!/bin/bash
# 修复服务器配置，确保Gunicorn和Nginx正确连接

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始修复服务器配置 ====="

# 1. 停止服务
echo "停止服务..."
systemctl stop question_bank

# 2. 检查systemd服务配置
echo "检查systemd服务配置..."
cat /etc/systemd/system/question_bank.service

# 3. 修改systemd服务配置以使用Gunicorn
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

# 4. 修改Gunicorn配置，确保端口与Nginx匹配
echo "修改Gunicorn配置..."
sed -i 's/bind = .*/bind = "127.0.0.1:5001"/' /var/www/question_bank/gunicorn_config.py

# 5. 重新加载systemd配置
echo "重新加载systemd配置..."
systemctl daemon-reload

# 6. 启动服务
echo "启动服务..."
systemctl start question_bank

# 7. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 8. 等待服务启动
echo "等待服务启动..."
sleep 5

# 9. 检查端口监听情况
echo "检查端口监听情况..."
netstat -tlnp | grep 5001

# 10. 测试本地访问
echo "测试本地访问..."
curl -s http://localhost:5001/ | head -20

echo "===== 服务器配置修复完成 ====="
EOF
