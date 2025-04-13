#!/bin/bash

# 全项目同步脚本 - 将本地项目完整同步到远程服务器
# 创建于: 2025-04-01

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
REMOTE_PASSWORD="85497652Sl."
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
    "*sync_*.sh"
    "*backup_*.sh"
    "*full_server_sync.sh"
    "*external_drive_backup.sh"
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     全项目同步到服务器 (含uploads目录)         ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "本地路径: ${LOCAL_DIR}"
echo -e "远程路径: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "同步时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查本地目录是否存在
if [ ! -d "${LOCAL_DIR}" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

# 使用sshpass自动提供密码，避免重复输入
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}安装sshpass工具以避免多次输入密码...${NC}"
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法安装sshpass，将使用普通SSH连接${NC}"
        SSH_CMD="ssh ${SSH_OPTS}"
        RSYNC_SSH="ssh ${SSH_OPTS}"
    else
        SSH_CMD="sshpass -p '${REMOTE_PASSWORD}' ssh ${SSH_OPTS}"
        RSYNC_SSH="sshpass -p '${REMOTE_PASSWORD}' ssh ${SSH_OPTS}"
    fi
else
    SSH_CMD="sshpass -p '${REMOTE_PASSWORD}' ssh ${SSH_OPTS}"
    RSYNC_SSH="sshpass -p '${REMOTE_PASSWORD}' ssh ${SSH_OPTS}"
fi

# 在服务器上创建备份
echo -e "${YELLOW}在服务器上创建当前文件的备份...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && tar -czf backup_before_sync_\$(date +%Y%m%d_%H%M%S).tar.gz . --exclude='./uploads' --exclude='./backup_*.tar.gz'\""

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

# 第1步: 同步核心文件（排除uploads目录）
echo -e "${YELLOW}第1步: 开始同步核心文件到服务器...${NC}"
echo -e "这将保持文件权限并仅传输有变更的文件..."
echo -e "${BLUE}同步中...(可能需要一些时间)${NC}"

if [[ "${SSH_CMD}" == *"sshpass"* ]]; then
    # 使用sshpass自动提供密码
    rsync -avz --compress --stats --delete --timeout=600 ${EXCLUDE_OPTIONS} \
        --exclude='/static/uploads/' \
        "${LOCAL_DIR}/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/" \
        --rsh="${RSYNC_SSH}"
else
    # 普通模式需要手动输入密码
    rsync -avz --compress --stats --delete --timeout=600 ${EXCLUDE_OPTIONS} \
        --exclude='/static/uploads/' \
        "${LOCAL_DIR}/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/" \
        --rsh="ssh ${SSH_OPTS}"
fi

CORE_SYNC_RESULT=$?

if [ ${CORE_SYNC_RESULT} -ne 0 ]; then
    echo -e "${RED}核心文件同步过程中出现错误。${NC}"
    echo -e "${YELLOW}是否继续同步uploads目录? (y/n)${NC}"
    read -p "" choice
    if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
        echo -e "${RED}同步已取消。${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}核心文件同步成功。${NC}"
fi

# 第2步: 同步uploads目录
echo -e "${YELLOW}第2步: 开始同步uploads目录到服务器...${NC}"
echo -e "这可能需要较长时间，取决于uploads目录的大小..."
echo -e "${BLUE}同步中...(可能需要很长时间)${NC}"

# 确保服务器上的uploads目录存在
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"mkdir -p ${REMOTE_DIR}/static/uploads/papers/papers\""

if [[ "${SSH_CMD}" == *"sshpass"* ]]; then
    # 使用sshpass自动提供密码
    rsync -avz --compress --stats --timeout=1800 \
        "${LOCAL_DIR}/static/uploads/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/static/uploads/" \
        --rsh="${RSYNC_SSH}"
else
    # 普通模式需要手动输入密码
    rsync -avz --compress --stats --timeout=1800 \
        "${LOCAL_DIR}/static/uploads/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/static/uploads/" \
        --rsh="ssh ${SSH_OPTS}"
fi

UPLOADS_SYNC_RESULT=$?

if [ ${UPLOADS_SYNC_RESULT} -ne 0 ]; then
    echo -e "${RED}uploads目录同步过程中出现错误。${NC}"
    echo -e "${YELLOW}核心文件可能已同步成功，但uploads目录同步失败。${NC}"
else
    echo -e "${GREEN}uploads目录同步成功。${NC}"
fi

# 重启服务
echo -e "${YELLOW}重启服务器应用...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart gunicorn || systemctl restart nginx\""

if [ $? -ne 0 ]; then
    echo -e "${RED}警告: 无法重启服务器服务。${NC}"
    echo -e "${YELLOW}可能需要手动重启服务器上的服务。${NC}"
else
    echo -e "${GREEN}服务器服务已成功重启。${NC}"
fi

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           全项目同步完成!                       ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "同步时间: $(date)"
echo -e "核心文件同步: " $([ ${CORE_SYNC_RESULT} -eq 0 ] && echo -e "${GREEN}成功${NC}" || echo -e "${RED}失败${NC}")
echo -e "uploads目录同步: " $([ ${UPLOADS_SYNC_RESULT} -eq 0 ] && echo -e "${GREEN}成功${NC}" || echo -e "${RED}失败${NC}")
echo -e "${YELLOW}请访问服务器网站验证功能是否正常${NC}"
