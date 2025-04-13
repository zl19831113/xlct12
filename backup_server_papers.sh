#!/bin/bash

# 从服务器备份uploads/papers目录到本地
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
REMOTE_PAPERS_DIR="/var/www/question_bank/uploads/papers"
SSH_PASS="85497652Sl."

# 本地备份目录
LOCAL_BACKUP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/server_papers_backup"
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${LOCAL_BACKUP_DIR}/papers_backup_${BACKUP_DATE}"

echo "开始从服务器备份uploads/papers目录..."
echo "备份将保存到: ${BACKUP_DIR}"

# 创建本地备份目录
mkdir -p "${BACKUP_DIR}"

# 使用sshpass和rsync从服务器获取papers目录
sshpass -p "${SSH_PASS}" rsync -avz --progress \
  "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PAPERS_DIR}/" \
  "${BACKUP_DIR}/"

echo "备份完成！文件保存在: ${BACKUP_DIR}"
echo "在阿里云回滚系统后，可以使用以下命令将文件重新上传到服务器:"
echo "sshpass -p \"${SSH_PASS}\" rsync -avz --progress \"${BACKUP_DIR}/\" \"${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PAPERS_DIR}/\""

# 创建一个恢复脚本便于日后使用
RESTORE_SCRIPT="${LOCAL_BACKUP_DIR}/restore_papers_${BACKUP_DATE}.sh"

cat > "${RESTORE_SCRIPT}" << EOF
#!/bin/bash

# 恢复papers目录到服务器
REMOTE_HOST="${REMOTE_HOST}"
REMOTE_USER="${REMOTE_USER}"
REMOTE_PAPERS_DIR="${REMOTE_PAPERS_DIR}"
SSH_PASS="${SSH_PASS}"
BACKUP_DIR="${BACKUP_DIR}"

echo "开始将备份的papers目录恢复到服务器..."

# 确保服务器上的目标目录存在
sshpass -p "\${SSH_PASS}" ssh -o StrictHostKeyChecking=no "\${REMOTE_USER}@\${REMOTE_HOST}" "mkdir -p \${REMOTE_PAPERS_DIR}"

# 使用rsync将备份文件上传到服务器
sshpass -p "\${SSH_PASS}" rsync -avz --progress \\
  "\${BACKUP_DIR}/" \\
  "\${REMOTE_USER}@\${REMOTE_HOST}:\${REMOTE_PAPERS_DIR}/"

echo "恢复完成！文件已上传到服务器: \${REMOTE_PAPERS_DIR}"
EOF

chmod +x "${RESTORE_SCRIPT}"

echo "------------------------"
echo "已创建恢复脚本: ${RESTORE_SCRIPT}"
echo "阿里云回滚系统后，运行此脚本即可将备份的文件恢复到服务器。"
