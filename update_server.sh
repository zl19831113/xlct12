#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
LOCAL_DIR="."
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# 定义要排除的文件和目录
EXCLUDES=(
    "--exclude=.git"
    "--exclude=.DS_Store"
    "--exclude=__pycache__"
    "--exclude=venv"
    "--exclude=instance/questions.db*"
    "--exclude=instance/xlct12.db*"
    "--exclude=uploads/papers"
    "--exclude=*.pyc"
    "--exclude=*.log"
    "--exclude=.vscode"
    "--exclude=*.bak"
    "--exclude=*.backup"
    "--exclude=backups"
    "--exclude=*.sh"
    "--exclude=*.py.orig"
    "--exclude=*.py.bak*"
    "--exclude=*.html.bak*"
    "--exclude=system_backup*"
)

# 设置更快的rsync选项
RSYNC_OPTS="-avz --compress --compress-level=9 --progress --timeout=60 ${EXCLUDES[*]}"

# 如果需要密码，取消注释以下行并修改密码
# SSH_PASS="your_password_here"
# SSH_CMD="sshpass -p ${SSH_PASS}"

# 如果不需要密码（使用SSH密钥），使用这个
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== 快速更新远程服务器 (${TIMESTAMP}) ======"
echo "本地目录: ${LOCAL_DIR}"
echo "远程服务器: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"

# 仅创建最小备份
echo "===== 在远程服务器创建最小备份 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && mkdir -p backups/quick_${TIMESTAMP} && cp app.py backups/quick_${TIMESTAMP}/"

# 快速上传核心文件
echo "===== 快速上传app.py ====="
rsync ${RSYNC_OPTS} app.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

echo "===== 快速上传templates目录 ====="
rsync ${RSYNC_OPTS} templates/ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/templates/

echo "===== 快速上传static目录 ====="
rsync ${RSYNC_OPTS} static/ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/static/

# 正确重启Gunicorn服务
echo "===== 正确重启Gunicorn服务 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && pkill -f 'gunicorn -c gunicorn_config.py' && sleep 2 && ${REMOTE_DIR}/venv/bin/gunicorn -c gunicorn_config.py app:app -D"

# 重启Nginx以确保静态文件正确加载
echo "===== 重启Nginx服务 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "systemctl restart nginx"

# 检查服务器状态
echo "===== 检查服务状态 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "ps aux | grep -i gunicorn | grep -v grep"

echo "====== 快速更新完成 (${TIMESTAMP}) ======"
echo "服务器已更新完成，请刷新浏览器测试" 