#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# SSH 命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== 开始诊断 502 Bad Gateway 错误 (${TIMESTAMP}) ======"

# 1. 检查 gunicorn 配置
echo "===== 检查 gunicorn_config.py ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cat ${REMOTE_DIR}/gunicorn_config.py" > gunicorn_config_backup.txt
echo "gunicorn配置已保存到本地 gunicorn_config_backup.txt"

# 2. 检查 nginx 配置
echo "===== 检查 nginx 配置 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cat /etc/nginx/sites-enabled/default" > nginx_config_backup.txt
echo "nginx配置已保存到本地 nginx_config_backup.txt"

# 3. 检查 gunicorn 状态
echo "===== 检查 gunicorn 状态 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "ps aux | grep -i gunicorn | grep -v grep"

# 4. 检查 gunicorn 日志
echo "===== 检查 gunicorn 日志 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "tail -n 50 ${REMOTE_DIR}/logs/error.log" > gunicorn_error_logs.txt
echo "gunicorn错误日志已保存到本地 gunicorn_error_logs.txt"

# 5. 尝试重新启动 gunicorn (正确的启动方式)
echo "===== 重新启动 gunicorn ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && pkill -f 'gunicorn -c gunicorn_config.py' || true && sleep 2 && ${REMOTE_DIR}/venv/bin/gunicorn -c gunicorn_config.py app:app -D --log-level debug"

# 6. 再次检查 gunicorn 是否启动
echo "===== 再次检查 gunicorn 状态 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "ps aux | grep -i gunicorn | grep -v grep"

# 7. 再次检查日志
echo "===== 重新检查错误日志 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "tail -n 50 ${REMOTE_DIR}/logs/error.log" > gunicorn_new_error_logs.txt
echo "新的gunicorn错误日志已保存到本地 gunicorn_new_error_logs.txt"

# 8. 检查 nginx 错误日志
echo "===== 检查 nginx 错误日志 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "tail -n 50 /var/log/nginx/error.log" > nginx_error_logs.txt
echo "nginx错误日志已保存到本地 nginx_error_logs.txt"

# 9. 尝试直接通过端口测试应用
echo "===== 检查应用是否直接响应 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "curl -s http://localhost:8080 | head -20" > app_response.txt
echo "应用响应已保存到本地 app_response.txt"

# 10. 最简单的尝试：直接运行 Flask 应用以查看错误
echo "===== 尝试直接运行 Flask 应用 ====="
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && FLASK_APP=app.py ${REMOTE_DIR}/venv/bin/flask run --host=0.0.0.0 --port=8081 > flask_debug.log 2>&1 &"
sleep 5
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "curl -s http://localhost:8081" > flask_response.txt
echo "Flask直接运行响应已保存到本地 flask_response.txt"

echo "====== 诊断完成 (${TIMESTAMP}) ======"
echo "所有诊断信息已保存到本地文件，请检查"
echo "如需一键修复，运行 fix_dependencies.sh" 