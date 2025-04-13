#!/bin/bash

# 直接启动Flask应用程序的简单脚本
# 创建于: 2025-04-01

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 服务器配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 使用sshpass自动提供密码
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}正在安装sshpass...${NC}"
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法安装sshpass，将使用普通SSH连接${NC}"
        SSH_CMD="ssh"
    else
        SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
    fi
else
    SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
fi

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     直接启动应用程序（简化方式）     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 先停止所有现有的python和gunicorn进程
echo -e "${YELLOW}停止所有现有的Python和Gunicorn进程...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"pkill -f python || true\""
sleep 2

# 确认进程已经停止
echo -e "${YELLOW}验证进程已经停止...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python\\|gunicorn' | grep -v grep || echo '没有找到Python进程'\""

# 检查并创建日志目录
echo -e "${YELLOW}创建日志目录...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"mkdir -p ${REMOTE_DIR}/logs\""

# 设置正确的文件权限
echo -e "${YELLOW}设置文件权限...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod +x ${REMOTE_DIR}/app.py && chown -R root:root ${REMOTE_DIR}\""

# 直接使用python启动应用
echo -e "${YELLOW}使用Python直接启动应用...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && nohup python3 app.py > ${REMOTE_DIR}/logs/app_$(date +%Y%m%d_%H%M%S).log 2>&1 &\""

# 等待应用程序启动
echo -e "${YELLOW}等待应用程序启动...${NC}"
sleep 5

# 检查进程是否在运行
echo -e "${YELLOW}验证应用程序是否正在运行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python\\|app.py' | grep -v grep\""

# 查看应用日志
echo -e "${YELLOW}显示应用日志最后20行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"find ${REMOTE_DIR}/logs -type f -name 'app_*' -exec ls -ltr {} \\; | tail -n 1 | awk '{print \\$9}' | xargs tail -n 20\""

# 更新Nginx配置以正确指向app.py运行的端口
echo -e "${YELLOW}更新Nginx配置...${NC}"
cat << EOF > /tmp/simple_nginx.conf
server {
    listen 80;
    server_name 120.26.12.100;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/question_bank/static;
        expires 1d;
    }

    location /uploads {
        alias /var/www/question_bank/static/uploads;
        expires 1d;
    }

    client_max_body_size 50M;
}
EOF

# 上传新的配置文件并替换现有配置
echo -e "${YELLOW}上传并应用新的Nginx配置...${NC}"
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/simple_nginx.conf ${REMOTE_USER}@${REMOTE_SERVER}:/tmp/simple_nginx.conf
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cp /tmp/simple_nginx.conf /etc/nginx/sites-enabled/default 2>/dev/null || cp /tmp/simple_nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null\""

# 检查Nginx配置语法
echo -e "${YELLOW}检查Nginx配置语法...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"nginx -t\""

# 重启Nginx
echo -e "${YELLOW}重启Nginx服务...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart nginx\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       应用程序启动尝试完成!                    ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站：${YELLOW}http://${REMOTE_SERVER}/${NC}"
echo -e "如果网站仍然无法访问，请检查服务器日志以获取更多信息。"
