#!/bin/bash

# zujuanwang76 远程备份脚本 - 优化版
# 创建于: 2025-03-29
# 更新于: 2025-03-29 00:23

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
REMOTE_BACKUP_DIR="/var/www/backups/zujuanwang76"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="backup_${TIMESTAMP}"
REMOTE_BACKUP_PATH="${REMOTE_BACKUP_DIR}/${BACKUP_NAME}"

# SSH 连接保持配置
SSH_OPTS="-o ServerAliveInterval=60 -o ServerAliveCountMax=10 -o ConnectTimeout=60 -o ConnectionAttempts=3"

# 配置 rsync 批次大小
BATCH_SIZE=1000

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
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      将 zujuanwang76 备份到远程服务器 (优化版)    ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "本地路径: ${LOCAL_DIR}"
echo -e "远程备份路径: ${REMOTE_SERVER}:${REMOTE_BACKUP_PATH}"
echo -e "备份时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"
echo -e "${RED}注意: 此备份过程需要输入服务器密码，您将被要求输入至少4次密码${NC}"
echo -e "${RED}提示: 如果要实现无密码备份，请考虑设置SSH密钥认证${NC}"

# 检查本地目录是否存在
if [ ! -d "${LOCAL_DIR}" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

# 在服务器上创建备份目录
echo -e "${YELLOW}在服务器上创建备份目录...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "mkdir -p ${REMOTE_BACKUP_DIR}"

if [ $? -ne 0 ]; then
    echo -e "${RED}无法在服务器上创建备份目录。终止操作。${NC}"
    exit 1
fi

# 在备份前检查远程磁盘空间
echo -e "${YELLOW}检查远程服务器磁盘空间...${NC}"
REMOTE_DISK_SPACE=$(ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "df -h | grep -E '/$|/var' | head -1 | awk '{print \$4}'")
LOCAL_SIZE=$(du -sh "${LOCAL_DIR}" | cut -f1)

echo -e "项目大小: ${LOCAL_SIZE}"
echo -e "远程服务器可用空间: ${REMOTE_DISK_SPACE}"

# 创建本地备份清单以跟踪进度
echo -e "${BLUE}创建文件清单...${NC}"
find "${LOCAL_DIR}" -type f -not -path "*/\.*" -not -path "*/__pycache__/*" -not -path "*/venv/*" -not -path "*/backup_2*/*" -not -path "*/zujuanwang_env/*" > "/tmp/zujuanwang_backup_filelist.txt"
TOTAL_FILES=$(wc -l < "/tmp/zujuanwang_backup_filelist.txt")

echo -e "${BLUE}总共需要备份 ${TOTAL_FILES} 个文件${NC}"

# 分批上传文件，提高稳定性
# 将核心文件和上传目录分开处理
echo -e "${YELLOW}首先备份核心项目文件...${NC}"

# 核心项目文件 - 排除大型uploads目录
rsync -avz --compress --stats --timeout=600 ${EXCLUDE_OPTIONS} --exclude="uploads/*" \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_BACKUP_PATH}/" \
    --rsh="ssh ${SSH_OPTS}"

CORE_RESULT=$?

# 如果核心文件备份成功，继续备份uploads目录
if [ ${CORE_RESULT} -eq 0 ]; then
    echo -e "${GREEN}核心项目文件备份成功。${NC}"
    echo -e "${YELLOW}正在备份uploads目录...${NC}"
    echo -e "这可能需要较长时间，请耐心等待..."
    
    # 使用选项减少连接中断问题
    rsync -avz --compress --stats --timeout=1800 --partial --partial-dir=.rsync-partial \
        --bwlimit=2000 --max-size=100m ${EXCLUDE_OPTIONS} \
        "${LOCAL_DIR}/uploads/" \
        "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_BACKUP_PATH}/uploads/" \
        --rsh="ssh ${SSH_OPTS}"
    
    UPLOADS_RESULT=$?
    
    if [ ${UPLOADS_RESULT} -ne 0 ]; then
        echo -e "${RED}备份uploads目录时出错，尝试分批备份...${NC}"
        
        # 分批处理大文件夹
        for dir in "${LOCAL_DIR}"/uploads/*; do
            if [ -d "$dir" ]; then
                dir_name=$(basename "$dir")
                echo -e "${BLUE}备份 uploads/${dir_name} 目录...${NC}"
                
                rsync -avz --compress --stats --timeout=600 --partial --partial-dir=.rsync-partial \
                    ${EXCLUDE_OPTIONS} \
                    "${dir}/" \
                    "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_BACKUP_PATH}/uploads/${dir_name}/" \
                    --rsh="ssh ${SSH_OPTS}"
                
                if [ $? -ne 0 ]; then
                    echo -e "${RED}警告: 备份 ${dir_name} 时出错，将在下次备份时重试。${NC}"
                else
                    echo -e "${GREEN}成功备份 ${dir_name}${NC}"
                fi
            fi
        done
    else
        echo -e "${GREEN}uploads目录备份成功。${NC}"
    fi
else
    echo -e "${RED}核心项目文件备份失败，终止操作。${NC}"
    exit 1
fi

# 在服务器上创建备份信息文件
echo -e "${YELLOW}创建备份信息文件...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "cat > ${REMOTE_BACKUP_PATH}/backup_info.txt << EOF
===========================================
              项目备份信息                
===========================================

备份创建时间: $(date)
备份源目录: ${LOCAL_DIR}
备份内容: 完整项目备份
备份时间戳: ${TIMESTAMP}

系统信息:
- 操作系统: $(uname -s)
- 主机名: $(hostname)
- 用户: $(whoami)
- Python版本: $(python3 --version 2>&1)

备份说明:
- 使用优化的备份脚本，提高稳定性
- 使用压缩传输减少网络流量
- 分批处理大型目录以防连接中断
EOF"

# 在服务器上创建备份的符号链接 (最新备份)
echo -e "${YELLOW}创建最新备份的符号链接...${NC}"
ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "ln -sf ${REMOTE_BACKUP_PATH} ${REMOTE_BACKUP_DIR}/latest"

# 统计备份数量和大小
echo -e "${YELLOW}计算备份统计信息...${NC}"
BACKUP_SIZE=$(ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "du -sh ${REMOTE_BACKUP_PATH} | cut -f1")
TOTAL_BACKUPS=$(ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "find ${REMOTE_BACKUP_DIR} -maxdepth 1 -type d -name 'backup_*' | wc -l")

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}            备份完成!                           ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "备份时间: $(date)"
echo -e "备份大小: ${BACKUP_SIZE}"
echo -e "备份路径: ${REMOTE_SERVER}:${REMOTE_BACKUP_PATH}"
echo -e "服务器上的备份总数: ${TOTAL_BACKUPS}"
echo -e "${YELLOW}最新备份的符号链接: ${REMOTE_BACKUP_DIR}/latest${NC}"

# 添加删除旧备份的选项（保留最近5个备份即可）
echo -e "${YELLOW}检查旧备份...${NC}"
if [ ${TOTAL_BACKUPS} -gt 5 ]; then
    TO_DELETE=$((${TOTAL_BACKUPS} - 5))
    echo -e "发现超过5个备份。将删除最早的 ${TO_DELETE} 个备份..."
    
    ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_SERVER} "find ${REMOTE_BACKUP_DIR} -maxdepth 1 -type d -name 'backup_*' | sort | head -n ${TO_DELETE} | xargs rm -rf"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}警告: 删除旧备份时出错。${NC}"
    else
        echo -e "${GREEN}已删除最早的 ${TO_DELETE} 个备份，保留最新的5个备份。${NC}"
    fi
else
    echo -e "${GREEN}备份数量未超过5个，无需删除旧备份。${NC}"
fi

# 清理临时文件
rm -f "/tmp/zujuanwang_backup_filelist.txt"

echo -e "${GREEN}备份过程完成!${NC}"
echo -e "${BLUE}提示: 如需查看最近的备份，请使用 ssh ${REMOTE_USER}@${REMOTE_SERVER} 'ls -l ${REMOTE_BACKUP_DIR}/latest'${NC}"
