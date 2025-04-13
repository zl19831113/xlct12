#!/bin/bash

# 全面修复服务器问题脚本
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
echo -e "${YELLOW}     全面修复服务器配置问题     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 步骤1: 分析现有Nginx配置文件
echo -e "${YELLOW}步骤1: 分析现有Nginx配置文件...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"find /etc/nginx -type f -name '*.conf' | xargs grep -l '120.26.12.100'\""

# 删除冲突的配置
echo -e "${YELLOW}清理冲突的Nginx配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf\""

# 创建一个干净的新配置
echo -e "${YELLOW}创建干净的新Nginx配置...${NC}"
cat << EOF > /tmp/question_bank.conf
server {
    listen 80;
    server_name 120.26.12.100;

    root /var/www/question_bank;
    index index.html index.htm;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8080;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        send_timeout 300;
    }

    location /static {
        alias /var/www/question_bank/static;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }

    location /static/uploads {
        alias /var/www/question_bank/static/uploads;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }

    client_max_body_size 100M;
}
EOF

# 上传新配置并放在正确位置
echo -e "${YELLOW}上传新的Nginx配置...${NC}"
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/question_bank.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/question_bank.conf

# 创建符号链接到sites-enabled目录
echo -e "${YELLOW}启用新的配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ln -sf /etc/nginx/sites-available/question_bank.conf /etc/nginx/sites-enabled/\""

# 检查Nginx配置语法
echo -e "${YELLOW}检查Nginx配置语法...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"nginx -t\""

# 创建proxy_params文件（如果不存在）
echo -e "${YELLOW}确保proxy_params文件存在...${NC}"
cat << EOF > /tmp/proxy_params
proxy_set_header Host \$http_host;
proxy_set_header X-Real-IP \$remote_addr;
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto \$scheme;
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/proxy_params ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/proxy_params
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod 644 /etc/nginx/proxy_params\""

# 步骤2: 准备应用程序环境
echo -e "${YELLOW}步骤2: 准备应用程序环境...${NC}"

# 停止所有现有的Python和Gunicorn进程
echo -e "${YELLOW}停止现有进程...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"pkill -f 'python\\|gunicorn\\|flask' || true\""
sleep 3

# 检查主要配置文件
echo -e "${YELLOW}检查app.py的最后几行(启动配置)...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tail -n 20 app.py\""

# 创建启动脚本
echo -e "${YELLOW}创建应用启动脚本...${NC}"
cat << EOF > /tmp/start_flask_app.sh
#!/bin/bash
cd /var/www/question_bank
export FLASK_APP=app.py
export FLASK_ENV=production
# 尝试多个端口，以防某个端口被占用
nohup python3 -m flask run --host=0.0.0.0 --port=8080 > logs/flask_app.log 2>&1 &
echo "应用已启动在端口8080，日志保存在logs/flask_app.log"
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/start_flask_app.sh ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/start_flask_app.sh
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod +x ${REMOTE_DIR}/start_flask_app.sh\""

# 确保日志目录存在
echo -e "${YELLOW}创建日志目录...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"mkdir -p ${REMOTE_DIR}/logs\""

# 设置正确的权限
echo -e "${YELLOW}设置正确的文件权限...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod +x ${REMOTE_DIR}/app.py && chown -R root:root ${REMOTE_DIR}\""

# 启动应用
echo -e "${YELLOW}启动应用程序...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ./start_flask_app.sh\""

# 等待应用启动
echo -e "${YELLOW}等待应用启动...${NC}"
sleep 5

# 检查应用是否运行
echo -e "${YELLOW}验证应用程序是否运行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python\\|flask' | grep -v grep\""

# 检查日志
echo -e "${YELLOW}检查应用程序日志...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"tail -n 20 ${REMOTE_DIR}/logs/flask_app.log 2>/dev/null || echo '无法读取日志'\""

# 步骤3: 重启Nginx
echo -e "${YELLOW}步骤3: 重启Nginx...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart nginx\""

# 检查Nginx状态
echo -e "${YELLOW}检查Nginx状态...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl status nginx | head -n 20\""

# 测试网站可访问性
echo -e "${YELLOW}测试网站可访问性...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"curl -s -I http://localhost:8080/ | head -n 5 || echo '应用程序未响应本地请求'\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       服务器修复完成!                           ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站：${YELLOW}http://${REMOTE_SERVER}/${NC}"
echo -e "如果网站仍然无法访问，请查看服务器上的日志:"
echo -e "  - ${YELLOW}${REMOTE_DIR}/logs/flask_app.log${NC} (应用日志)"
echo -e "  - ${YELLOW}/var/log/nginx/error.log${NC} (Nginx错误日志)"
