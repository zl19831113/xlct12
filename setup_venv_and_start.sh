#!/bin/bash

# 使用Python虚拟环境设置应用程序脚本
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
VENV_DIR="${REMOTE_DIR}/venv"

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
echo -e "${YELLOW}     使用Python虚拟环境设置应用程序     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 步骤1: 确保python3-venv已安装
echo -e "${YELLOW}步骤1: 确保python3-venv和python3-full已安装...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"apt-get update && apt-get install -y python3-venv python3-full\""

# 步骤2: 创建并设置虚拟环境
echo -e "${YELLOW}步骤2: 创建并设置Python虚拟环境...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && rm -rf ${VENV_DIR} && python3 -m venv ${VENV_DIR}\""

# 创建requirements.txt文件
echo -e "${YELLOW}创建requirements.txt文件...${NC}"
cat << EOF > /tmp/requirements.txt
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.0.0
Werkzeug==2.0.2
SQLAlchemy==1.4.27
python-docx==0.8.11
gunicorn==20.1.0
Pillow==9.0.0
EOF

# 上传requirements.txt文件
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/requirements.txt ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/requirements.txt

# 安装依赖
echo -e "${YELLOW}在虚拟环境中安装Python依赖...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ${VENV_DIR}/bin/pip install --no-cache-dir -r requirements.txt\""

# 步骤3: 创建应用程序启动脚本
echo -e "${YELLOW}步骤3: 创建应用程序启动脚本...${NC}"
cat << EOF > /tmp/start_app.sh
#!/bin/bash
# 应用程序启动脚本
cd ${REMOTE_DIR}

# 停止任何运行中的Python进程
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# 确保数据库目录存在
mkdir -p instance

# 确保数据库文件在正确的位置
if [ ! -f instance/xlct12.db ]; then
  echo "将数据库文件复制到instance目录..."
  cp -v xlct12.db instance/ 2>/dev/null || echo "警告: 找不到xlct12.db!"
fi

# 使用虚拟环境启动Flask应用程序
echo "启动应用程序..."
source ${VENV_DIR}/bin/activate
nohup python app.py > app.log 2>&1 &

# 显示启动的进程
ps aux | grep -i "python.*app.py" | grep -v grep
echo "应用已启动，日志保存在app.log"
EOF

# 上传并设置启动脚本权限
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/start_app.sh ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/start_app.sh
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod +x ${REMOTE_DIR}/start_app.sh\""

# 步骤4: 创建Systemd服务单元文件以便自动启动
echo -e "${YELLOW}步骤4: 创建Systemd服务单元文件...${NC}"
cat << EOF > /tmp/question-bank.service
[Unit]
Description=Question Bank Web Application
After=network.target

[Service]
User=root
WorkingDirectory=${REMOTE_DIR}
ExecStart=${VENV_DIR}/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 上传服务单元文件
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/question-bank.service ${REMOTE_USER}@${REMOTE_SERVER}:/etc/systemd/system/question-bank.service

# 步骤5: 配置Nginx
echo -e "${YELLOW}步骤5: 确保Nginx配置正确...${NC}"
cat << EOF > /tmp/nginx-site.conf
server {
    listen 80;
    server_name 120.26.12.100;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        
        # 增加缓冲区大小
        proxy_buffer_size 16k;
        proxy_buffers 4 16k;
        
        # 增加超时时间
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    location /static {
        alias ${REMOTE_DIR}/static;
        expires 1d;
    }

    location /static/uploads {
        alias ${REMOTE_DIR}/static/uploads;
        expires 1d;
    }

    client_max_body_size 100M;
}
EOF

# 上传Nginx配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/nginx-site.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/question-bank.conf

# 启用并确保没有冲突
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/question_bank.conf\""
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ln -sf /etc/nginx/sites-available/question-bank.conf /etc/nginx/sites-enabled/\""

# 检查Nginx配置语法
echo -e "${YELLOW}检查Nginx配置语法...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"nginx -t\""

# 步骤6: 重启所有服务
echo -e "${YELLOW}步骤6: 重启所有服务...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl daemon-reload && systemctl enable question-bank.service\""
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ./start_app.sh\""
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart nginx\""

# 步骤7: 验证应用是否运行
echo -e "${YELLOW}步骤7: 验证应用是否运行...${NC}"
sleep 5
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python.*app.py' | grep -v grep\""

# 检查日志
echo -e "${YELLOW}检查应用日志(最后10行)...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tail -n 10 app.log\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}     安装和配置完成! 应用程序已启动     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站: ${YELLOW}http://${REMOTE_SERVER}/${NC}"
echo -e "如果可以访问，系统已经配置为开机自启动。"
echo -e "如果仍然出现502错误，请检查以下日志获取更多信息:"
echo -e "  - 应用日志: ${YELLOW}${REMOTE_DIR}/app.log${NC}"
echo -e "  - Nginx错误日志: ${YELLOW}/var/log/nginx/error.log${NC}"
