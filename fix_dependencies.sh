#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== 开始修复服务器依赖并启动应用 (${TIMESTAMP}) ======"

# 1. 登录服务器并创建备份
echo "===== 创建 pip 依赖备份 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && mkdir -p backups/pip_${TIMESTAMP} && /var/www/question_bank/venv/bin/pip freeze > backups/pip_${TIMESTAMP}/requirements.txt"

# 2. 修复 Flask 和 flask_sqlalchemy 版本
echo "===== 修复依赖关系 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && /var/www/question_bank/venv/bin/pip uninstall -y flask && /var/www/question_bank/venv/bin/pip install flask==2.0.1 && /var/www/question_bank/venv/bin/pip install flask_sqlalchemy==2.5.1"

# 3. 如果gunicorn正在运行，则停止
echo "===== 停止 gunicorn ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "pkill -f 'gunicorn -c gunicorn_config.py' || true"

# 4. 重启 nginx
echo "===== 重启 nginx ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "systemctl restart nginx"

# 5. 启动 gunicorn
echo "===== 启动 gunicorn ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && /var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app -D"

# 6. 检查服务状态
echo "===== 检查服务状态 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "ps aux | grep -i gunicorn | grep -v grep"

# 7. 测试 API 可用性
echo "===== 测试 API 可用性 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "curl -s http://localhost:8080 | grep -i title"

echo "====== 修复完成 (${TIMESTAMP}) ======"
echo "如果需要回滚，请运行:"
echo "ssh ${REMOTE_USER}@${REMOTE_HOST} \"cd ${REMOTE_DIR} && /var/www/question_bank/venv/bin/pip install -r backups/pip_${TIMESTAMP}/requirements.txt\"" 