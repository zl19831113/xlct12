#!/bin/bash

# 修复和重启Gunicorn服务脚本
# 创建于: 2025-04-01

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 检查sshpass是否已安装
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}正在安装sshpass工具...${NC}"
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法安装sshpass，将使用普通SSH连接，需要手动输入密码${NC}"
        SSH_CMD="ssh"
    else
        SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
    fi
else
    SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
fi

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     诊断并修复Gunicorn服务问题     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 检查当前Gunicorn进程
echo -e "${YELLOW}正在检查当前Gunicorn进程...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'gunicorn' | grep -v grep\""

# 收集当前配置信息
echo -e "${YELLOW}收集Gunicorn配置信息...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && cat gunicorn_config.py\""

# 检查权限和所有权
echo -e "${YELLOW}检查应用目录权限和所有权...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ls -la ${REMOTE_DIR} | head -n 20\""

# 检查虚拟环境
echo -e "${YELLOW}检查Python虚拟环境...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && ls -la venv/bin | grep -i 'python\\|gunicorn'\""

# 检查Nginx配置
echo -e "${YELLOW}检查Nginx配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && cat nginx.conf 2>/dev/null || echo 'Nginx配置文件不存在'\""

echo -e "${YELLOW}检查Nginx站点配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cat /etc/nginx/sites-enabled/* 2>/dev/null || cat /etc/nginx/conf.d/* 2>/dev/null || echo '找不到Nginx站点配置'\""

# 重启应用 - 使用正确的方式停止和启动Gunicorn
echo -e "${YELLOW}正在重启Gunicorn应用...${NC}"

# 杀掉现有的Gunicorn进程
echo -e "${YELLOW}停止现有Gunicorn进程...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"pkill -f gunicorn\""

# 等待进程完全停止
echo -e "${YELLOW}等待进程完全停止...${NC}"
sleep 3

# 确保app.py具有正确的权限
echo -e "${YELLOW}设置正确的文件权限...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && chmod +x app.py && chown -R root:root .\""

# 在后台启动Gunicorn
echo -e "${YELLOW}启动Gunicorn...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && source venv/bin/activate && nohup gunicorn -c gunicorn_config.py app:app > gunicorn.log 2>&1 &\""

# 验证Gunicorn是否已启动
echo -e "${YELLOW}验证Gunicorn是否已成功启动...${NC}"
sleep 5
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'gunicorn' | grep -v grep\""

# 重启Nginx
echo -e "${YELLOW}重启Nginx...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"service nginx restart || /etc/init.d/nginx restart\""

# 检查Nginx是否在运行
echo -e "${YELLOW}验证Nginx是否在运行...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"service nginx status || /etc/init.d/nginx status || ps aux | grep -i nginx | grep -v grep\""

# 检查日志
echo -e "${YELLOW}检查最新的应用日志...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tail -n 20 gunicorn.log 2>/dev/null || tail -n 20 app.log 2>/dev/null\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       服务重启完成!                       ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站，如果仍然无法访问，请查看上面的日志输出寻找错误原因。"
echo -e "服务器网址：http://${REMOTE_SERVER}/"
