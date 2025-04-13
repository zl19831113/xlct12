#!/bin/bash

# 修复依赖并启动应用程序脚本
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
echo -e "${YELLOW}     安装Python依赖并启动应用     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 步骤1: 检查Python版本
echo -e "${YELLOW}步骤1: 检查Python版本...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"python3 --version\""

# 步骤2: 安装Python依赖
echo -e "${YELLOW}步骤2: 安装Python依赖...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"apt-get update && apt-get install -y python3-pip python3-venv\""

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
echo -e "${YELLOW}安装Python依赖...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && pip3 install -r requirements.txt\""

# 步骤3: 检查数据库和应用配置
echo -e "${YELLOW}步骤3: 检查数据库...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ls -la instance\""

# 创建正确的启动脚本
echo -e "${YELLOW}创建正确的启动脚本...${NC}"
cat << EOF > /tmp/run_app.sh
#!/bin/bash
cd /var/www/question_bank
export FLASK_APP=app.py
export FLASK_ENV=production

# 确保实例目录存在
mkdir -p instance

# 杀掉任何现有的Python进程
pkill -f "python.*app.py" || true
sleep 2

# 检查数据库是否存在
if [ ! -f instance/xlct12.db ]; then
  echo "数据库文件不存在,尝试复制..."
  cp -v xlct12.db instance/ 2>/dev/null || echo "无法找到数据库文件!"
fi

# 启动应用
echo "启动应用..."
nohup python3 app.py > app.log 2>&1 &

echo "应用启动,日志保存在app.log"
EOF

# 上传并设置权限
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/run_app.sh ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/run_app.sh
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"chmod +x ${REMOTE_DIR}/run_app.sh\""

# 步骤4: 运行应用
echo -e "${YELLOW}步骤4: 运行应用...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ./run_app.sh\""

# 等待应用启动
echo -e "${YELLOW}等待应用启动...${NC}"
sleep 5

# 检查应用是否在运行
echo -e "${YELLOW}检查应用是否在运行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python.*app.py' | grep -v grep\""

# 检查日志
echo -e "${YELLOW}检查应用日志...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tail -n 20 app.log\""

# 设置开机自启动
echo -e "${YELLOW}设置应用开机自启动...${NC}"
cat << EOF > /tmp/question_bank.service
[Unit]
Description=Question Bank Web Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/question_bank
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/question_bank.service ${REMOTE_USER}@${REMOTE_SERVER}:/etc/systemd/system/question_bank.service
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl daemon-reload && systemctl enable question_bank.service\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       依赖安装和应用启动完成!                  ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站：${YELLOW}http://${REMOTE_SERVER}/${NC}"
echo -e "如果网站可以访问，系统已经配置为开机自启动。"
echo -e "如果仍然无法访问，请检查日志: ${YELLOW}${REMOTE_DIR}/app.log${NC}"
