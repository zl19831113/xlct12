#!/bin/bash

# 断点续传脚本 - 排除所有备份内容
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
    "*resume_upload.sh"
    "*system_backup_*"
    "*_backup_*"
    "*uploads_backup_*"
    "backup_*"
    "*backup/*"
    ".venv/*"
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      断点续传 - 排除备份内容        ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "本地路径: ${LOCAL_DIR}"
echo -e "远程路径: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查本地目录是否存在
if [ ! -d "${LOCAL_DIR}" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

# 测试SSH连接
echo -e "${YELLOW}测试SSH连接...${NC}"
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ${REMOTE_USER}@${REMOTE_SERVER} "echo 连接成功"; then
    echo -e "${RED}SSH连接失败。请确保已正确设置SSH密钥认证。${NC}"
    echo -e "${YELLOW}尝试使用以下命令设置：${NC}"
    echo -e "ssh-copy-id ${REMOTE_USER}@${REMOTE_SERVER}"
    exit 1
fi

# 先上传关键文件
echo -e "${YELLOW}首先上传最重要的文件...${NC}"
echo -e "上传app.py和数据库文件..."

rsync -avz --progress ${EXCLUDE_OPTIONS} \
    "${LOCAL_DIR}/app.py" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/"

rsync -avz --progress ${EXCLUDE_OPTIONS} \
    "${LOCAL_DIR}/instance/" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/instance/"

# 上传其他必要文件，排除uploads目录
echo -e "${YELLOW}上传其他必要文件（排除uploads和备份）...${NC}"
rsync -avz --progress --partial ${EXCLUDE_OPTIONS} --exclude="uploads*" \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/"

# 询问是否上传uploads目录
echo -e "${YELLOW}是否需要上传uploads目录？（大量文件，可能需要较长时间）${NC}"
read -p "上传uploads目录? (y/n): " upload_uploads

if [[ "$upload_uploads" == "y" ]]; then
    echo -e "${YELLOW}开始上传uploads目录（排除备份文件）...${NC}"
    echo -e "这可能需要很长时间，您可以随时按Ctrl+C暂停，之后可以重新运行此脚本继续上传。"
    
    # 使用--partial保留部分传输的文件，实现断点续传
    rsync -avz --progress --partial ${EXCLUDE_OPTIONS} \
        "${LOCAL_DIR}/uploads/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/uploads/"
fi

# 确保数据库和应用配置的一致性
echo -e "${YELLOW}验证服务器端配置...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "cd ${REMOTE_DIR} && ls -la instance/xlct12.db && chmod 644 instance/xlct12.db 2>/dev/null"

# 重启服务器应用程序
echo -e "${YELLOW}重启服务器应用程序...${NC}"
ssh ${REMOTE_USER}@${REMOTE_SERVER} "systemctl restart gunicorn && systemctl restart nginx"

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
