#!/bin/bash

# 直接上传脚本 - 跳过服务器端备份，聚焦于上传进度显示
# 创建于: 2025-04-01

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"

# 要排除的文件/目录
EXCLUDE_PATTERNS=(
    "*.git*"
    "*__pycache__*"
    "*.pyc"
    "*/\.*"
    "*.DS_Store"
    "*deploy_to_server.sh"
    "*direct_upload.sh"
    "*system_backup_*"
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      直接上传至服务器 - 带详细进度        ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "本地路径: ${LOCAL_DIR}"
echo -e "远程路径: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查本地目录是否存在
if [ ! -d "${LOCAL_DIR}" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

# 设置密码认证
REMOTE_PASSWORD="85497652Sl."

# 检查sshpass是否已安装
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}正在安装sshpass工具...${NC}"
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法安装sshpass，将使用普通SSH连接，需要手动输入密码${NC}"
        USE_PASSWORD=false
    else
        USE_PASSWORD=true
    fi
else
    USE_PASSWORD=true
fi

# 直接上传文件
echo -e "${YELLOW}开始上传文件到服务器...${NC}"
echo -e "根据您的连接速度，此过程可能需要一些时间。"
echo -e "${YELLOW}您将看到详细的上传进度：${NC}"

# 使用--progress选项显示文件传输进度，--stats显示传输统计信息
if [ "$USE_PASSWORD" = true ]; then
    # 使用sshpass提供密码
echo -e "${YELLOW}使用密码认证自动上传...${NC}"
sshpass -p "${REMOTE_PASSWORD}" rsync -avz --progress --stats --delete ${EXCLUDE_OPTIONS} \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/"
else
    # 普通模式，需要手动输入密码
    echo -e "${YELLOW}使用密码认证，需要输入密码: ${REMOTE_PASSWORD}${NC}"
    rsync -avz --progress --stats --delete ${EXCLUDE_OPTIONS} \
        "${LOCAL_DIR}/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}上传文件到服务器失败。${NC}"
    exit 1
fi

echo -e "${GREEN}文件上传成功。${NC}"

# 确保数据库和应用配置的一致性
echo -e "${YELLOW}验证服务器端配置...${NC}"
if [ "$USE_PASSWORD" = true ]; then
    sshpass -p "${REMOTE_PASSWORD}" ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && ls -la instance/xlct12.db && chmod 644 instance/xlct12.db 2>/dev/null"
else
    echo -e "${YELLOW}请输入密码: ${REMOTE_PASSWORD}${NC}"
    ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && ls -la instance/xlct12.db && chmod 644 instance/xlct12.db 2>/dev/null"
fi

# 重启服务器应用程序
echo -e "${YELLOW}重启服务器应用程序...${NC}"
if [ "$USE_PASSWORD" = true ]; then
    sshpass -p "${REMOTE_PASSWORD}" ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart gunicorn && systemctl restart nginx"
else
    echo -e "${YELLOW}请输入密码: ${REMOTE_PASSWORD}${NC}"
    ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart gunicorn && systemctl restart nginx"
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}警告: 无法重启服务器服务。${NC}"
    echo -e "${YELLOW}您可能需要手动重启服务器上的服务。${NC}"
else
    echo -e "${GREEN}服务器服务已成功重启。${NC}"
fi

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}            上传完成!                 ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "应用程序现已在服务器上运行。"
echo -e "上传内容包括："
echo -e " - 修复后的应用程序代码"
echo -e " - 修复后的xlct12.db数据库（文件关联已修复）"
echo -e " - 修复后的文件路径配置"
echo -e "请验证所有功能是否正常工作，特别是文件下载功能。"
