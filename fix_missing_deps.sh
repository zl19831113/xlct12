#!/bin/bash

# 安装缺失依赖并重启应用程序
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
echo -e "${YELLOW}     安装缺失依赖并重启应用     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 安装缺失的依赖
echo -e "${YELLOW}步骤1: 安装缺失的tqdm库和其他可能需要的库...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ${VENV_DIR}/bin/pip install tqdm pandas matplotlib requests\""

# 重启应用
echo -e "${YELLOW}步骤2: 停止当前运行的应用...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"pkill -f 'python.*app.py' || true\""
sleep 2

# 使用启动脚本重新启动应用
echo -e "${YELLOW}步骤3: 重新启动应用...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && source ${VENV_DIR}/bin/activate && python app.py > app.log 2>&1 &\""

# 等待应用启动
echo -e "${YELLOW}等待应用启动...${NC}"
sleep 5

# 检查应用是否在运行
echo -e "${YELLOW}步骤4: 验证应用是否在运行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'python.*app.py' | grep -v grep\""

# 检查日志
echo -e "${YELLOW}步骤5: 检查应用日志最后20行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tail -n 20 app.log\""

# 检查Nginx错误日志
echo -e "${YELLOW}步骤6: 检查Nginx错误日志...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"tail -n 20 /var/log/nginx/error.log\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}     依赖安装并重启应用完成!     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在再次尝试访问网站: ${YELLOW}http://${REMOTE_SERVER}/${NC}"
echo -e "如果仍有问题，请检查上面显示的日志信息以获取更多细节。"
