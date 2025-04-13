#!/bin/bash

# 同步核心文件脚本（排除uploads目录）
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"

# SSH 连接保持配置
SSH_OPTS="-o ServerAliveInterval=60 -o ServerAliveCountMax=10 -o ConnectTimeout=60 -o ConnectionAttempts=3"

# 要排除的文件和目录
EXCLUDE_PATTERNS=(
    "*.git*"
    "*__pycache__*"
    "*.pyc"
    "*/\.*"
    "*instance/questions.db-journal"
    "*.DS_Store"
    "*backup_2*"
    "*venv*"
    "*zujuanwang_env*"
    "*/uploads/*"
    "*sync_core_files.sh"
    "*backup_to_server.sh"
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     同步核心文件到服务器（排除uploads目录）      ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "本地路径: ${LOCAL_DIR}"
echo -e "远程路径: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "同步时间: $(date)"
echo -e "${RED}注意: 此同步过程需要输入服务器密码${NC}"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查本地目录是否存在
if [ ! -d "${LOCAL_DIR}" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

# 在服务器上创建备份
echo -e "${YELLOW}在服务器上创建当前文件的备份...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && tar -czf backup_before_sync_\$(date +%Y%m%d_%H%M%S).tar.gz . --exclude='./uploads' --exclude='./backup_*.tar.gz'"

if [ $? -ne 0 ]; then
    echo -e "${RED}警告: 无法在服务器上创建备份。是否继续? (y/n)${NC}"
    read -p "" choice
    if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
        echo -e "${RED}同步已取消。${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}服务器备份已创建。${NC}"
fi

# 使用rsync同步文件（排除uploads目录）
echo -e "${YELLOW}开始同步核心文件到服务器...${NC}"
echo -e "这将保持文件权限并仅传输有变更的文件..."
echo -e "${BLUE}同步中...(可能需要一些时间)${NC}"

rsync -avz --compress --stats --delete --timeout=600 ${EXCLUDE_OPTIONS} \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/" \
    --rsh="ssh ${SSH_OPTS}"

SYNC_RESULT=$?

if [ ${SYNC_RESULT} -ne 0 ]; then
    echo -e "${RED}同步过程中出现错误。${NC}"
    exit 1
else
    echo -e "${GREEN}文件同步成功。${NC}"
fi

# 重启服务
echo -e "${YELLOW}重启服务器应用...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart gunicorn || systemctl restart nginx"

if [ $? -ne 0 ]; then
    echo -e "${RED}警告: 无法重启服务器服务。${NC}"
    echo -e "${YELLOW}可能需要手动重启服务器上的服务。${NC}"
else
    echo -e "${GREEN}服务器服务已成功重启。${NC}"
fi

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           核心文件同步完成!                     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "同步时间: $(date)"
echo -e "说明: 已同步除uploads目录外的所有文件"
echo -e "      服务器与本地内容现在一致"
echo -e "${YELLOW}如需验证，请访问服务器网站${NC}"
