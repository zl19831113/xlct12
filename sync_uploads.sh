#!/bin/bash

# 同步uploads目录的脚本
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/static/uploads"
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank/static/uploads"

# SSH 连接保持配置
SSH_OPTS="-o ServerAliveInterval=60 -o ServerAliveCountMax=10 -o ConnectTimeout=60 -o ConnectionAttempts=3"

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     同步uploads目录到服务器                     ${NC}"
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

# 在服务器上创建目标目录
echo -e "${YELLOW}确保服务器上的目标目录存在...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "mkdir -p ${REMOTE_DIR}/papers/papers"

# 使用rsync同步文件
echo -e "${YELLOW}开始同步uploads目录到服务器...${NC}"
echo -e "这将保持文件权限并仅传输有变更的文件..."
echo -e "${BLUE}同步中...(可能需要一些时间)${NC}"

rsync -avz --compress --stats --timeout=600 \
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

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           uploads目录同步完成!                  ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "同步时间: $(date)"
echo -e "${YELLOW}请访问服务器网站验证试卷下载功能是否正常${NC}"
