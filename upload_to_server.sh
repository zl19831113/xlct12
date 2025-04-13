#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
LOCAL_DIR="./"

# 排除不需要上传的文件和目录
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

echo "====== 开始上传文件到远程服务器 ======"
echo "本地目录: $LOCAL_DIR"
echo "远程服务器: $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

# 首先，创建关键目录的备份
echo "===== 在远程服务器创建备份 ====="
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && mkdir -p backups/$(date +%Y%m%d_%H%M%S) && cp -r app.py templates static backups/$(date +%Y%m%d_%H%M%S)/"

# 上传更新的核心文件
echo "===== 上传app.py ====="
rsync -avz app.py $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

echo "===== 上传templates目录 ====="
rsync -avz templates/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/templates/

echo "===== 上传static目录 ====="
rsync -avz static/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/static/

# 重启服务
echo "===== 重启服务 ====="
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && systemctl restart zujuanwang.service"

echo "====== 上传完成 ======"
echo "请检查远程服务器网站是否正常运行" 