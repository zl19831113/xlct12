#!/bin/bash

# 修复500内部服务器错误脚本
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"
SSH_PASS="85497652Sl."

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       修复500 Internal Server Error               ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "目标服务器: ${REMOTE_SERVER}"
echo -e "应用目录: ${REMOTE_DIR}"
echo -e "修复时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 尝试一次性执行所有修复命令，避免多次SSH连接
echo -e "${YELLOW}正在执行全套修复步骤...${NC}"

ssh ${REMOTE_USER}@${REMOTE_SERVER} << 'ENDSSH'
# 1. 停止所有现有的gunicorn进程
echo "停止所有gunicorn进程..."
pkill -f gunicorn || true

# 2. 停止存在问题的服务
echo "停止zujuanwang服务..."
systemctl stop zujuanwang.service || true

# 3. 创建必要的日志目录
echo "创建日志目录..."
mkdir -p /var/www/question_bank/logs

# 4. 修复gunicorn配置文件 - 确保日志路径正确
echo "检查gunicorn配置..."
if [ -f /var/www/question_bank/gunicorn_config.py ]; then
    # 备份原配置
    cp /var/www/question_bank/gunicorn_config.py /var/www/question_bank/gunicorn_config.py.bak
    
    # 更新配置文件确保日志路径正确
    cat > /var/www/question_bank/gunicorn_config.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
timeout = 300
accesslog = "/var/www/question_bank/logs/access.log"
errorlog = "/var/www/question_bank/logs/error.log"
capture_output = True
loglevel = "info"
EOF
    echo "已更新gunicorn配置文件"
fi

# 5. 检查和修复环境
echo "检查虚拟环境..."
cd /var/www/question_bank
if [ ! -d "venv" ]; then
    echo "创建新的虚拟环境..."
    python3 -m venv venv
fi

# 6. 确保依赖正确安装
echo "安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 7. 检查并修复systemd服务配置
echo "修复systemd服务配置..."
cat > /etc/systemd/system/zujuanwang.service << 'EOF'
[Unit]
Description=Zujuanwang Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/question_bank
ExecStart=/var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. 重新加载systemd配置并启动服务
echo "重新加载systemd配置..."
systemctl daemon-reload
systemctl restart zujuanwang.service

# 9. 确保nginx配置正确
echo "检查nginx配置..."
if [ -f /etc/nginx/sites-available/default ]; then
    # 备份现有配置
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
    
    # 更新nginx配置
    cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
    
    location /uploads {
        alias /var/www/question_bank/uploads;
    }
}
EOF
    echo "已更新nginx配置"
fi

# 10. 重启nginx
echo "重启nginx..."
systemctl restart nginx

# 11. 验证服务状态
echo "验证服务状态..."
systemctl status zujuanwang.service
systemctl status nginx
ps aux | grep -E 'gunicorn|python' | grep -v grep
netstat -tulpn | grep -E '8000|80'

echo "修复过程完成"
ENDSSH

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           服务修复尝试完成!                     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "完成时间: $(date)"
echo -e "${YELLOW}请再次访问服务器网站验证问题是否解决${NC}"
echo -e "${YELLOW}网站地址: https://xlct12.com/papers${NC}"
