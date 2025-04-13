#!/bin/bash

# 修复502错误的脚本
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

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       修复502 Bad Gateway错误                    ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "目标服务器: ${REMOTE_SERVER}"
echo -e "应用目录: ${REMOTE_DIR}"
echo -e "诊断时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查服务状态
echo -e "${BLUE}正在检查zujuanwang服务状态...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl status zujuanwang.service"

echo -e "${BLUE}正在检查nginx服务状态...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl status nginx.service"

# 检查日志文件
echo -e "${BLUE}正在检查zujuanwang日志...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "journalctl -u zujuanwang.service --no-pager -n 50"

echo -e "${BLUE}正在检查nginx错误日志...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "tail -n 50 /var/log/nginx/error.log"

# 检查端口监听情况
echo -e "${BLUE}检查进程和端口监听情况...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "ps aux | grep -E 'gunicorn|python'"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "netstat -tulpn | grep -E '5000|5001|80|8000'"

# 尝试手动启动应用
echo -e "${YELLOW}正在尝试手动启动应用...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && pkill -f gunicorn && pkill -f 'app.py' && sleep 2"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && python3 -m venv venv || true"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && source venv/bin/activate && pip install -r requirements.txt || true"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && source venv/bin/activate && gunicorn -c gunicorn_config.py app:app --daemon"

# 检查服务是否成功启动
echo -e "${BLUE}检查应用是否成功启动...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "ps aux | grep -E 'gunicorn|python'"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "netstat -tulpn | grep -E '5000|5001|80|8000'"

# 重启nginx
echo -e "${YELLOW}重新启动Nginx...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart nginx"

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           服务修复尝试完成!                     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "完成时间: $(date)"
echo -e "${YELLOW}请再次访问服务器网站验证问题是否解决${NC}"
echo -e "${YELLOW}如果仍然出现502错误，可能需要进一步检查服务器配置${NC}"
