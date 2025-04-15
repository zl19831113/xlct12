#!/bin/bash

# 设置变量
REMOTE_USER="root"
REMOTE_HOST="120.26.12.100"
REMOTE_DIR="/var/www/question_bank"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
BACKUP_DIR="/root/backups/question_bank_${TIMESTAMP}"
LOG_FILE="deploy_${TIMESTAMP}.log"

# SSH命令
SSH_CMD="ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10"

echo "====== 安全部署脚本 (${TIMESTAMP}) ======" | tee -a $LOG_FILE
echo "服务器: ${REMOTE_HOST}" | tee -a $LOG_FILE
echo "目录: ${REMOTE_DIR}" | tee -a $LOG_FILE
echo "开始时间: $(date)" | tee -a $LOG_FILE

# 1. 检查本地Git状态
echo "===== 检查本地Git状态 =====" | tee -a $LOG_FILE
if [ -d ".git" ]; then
    git status | tee -a $LOG_FILE
else
    echo "错误: 当前目录不是Git仓库" | tee -a $LOG_FILE
    exit 1
fi

# 提示用户确认
read -p "是否继续部署? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "部署已取消" | tee -a $LOG_FILE
    exit 0
fi

# 2. 创建服务器备份
echo "===== 在服务器上创建备份 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
mkdir -p ${BACKUP_DIR}
if [ -d ${REMOTE_DIR} ]; then
    # 备份整个项目目录
    cp -r ${REMOTE_DIR}/* ${BACKUP_DIR}/
    # 特别备份关键配置文件
    cp ${REMOTE_DIR}/gunicorn_config.py ${BACKUP_DIR}/gunicorn_config.py.bak 2>/dev/null || true
    cp -r /etc/nginx/sites-enabled ${BACKUP_DIR}/nginx_sites_enabled 2>/dev/null || true
    echo '✅ 服务器备份完成'
else
    echo '❌ 远程目录不存在'
    exit 1
fi
" | tee -a $LOG_FILE

# 3. 检查远程Git状态
echo "===== 检查远程Git状态 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
cd ${REMOTE_DIR}
git status 2>&1
# 检查是否有未提交的更改
if git status | grep -q 'Changes not staged'; then
    echo '⚠️ 远程服务器有未提交的更改，创建临时保存'
    git stash save 'Auto-stashed before deployment ${TIMESTAMP}'
    echo '✅ 临时保存了远程更改'
fi
" | tee -a $LOG_FILE

# 4. 推送本地更改
echo "===== 推送本地Git更改 =====" | tee -a $LOG_FILE

# 询问用户当前的分支名
current_branch=$(git branch --show-current)
echo "当前分支: $current_branch" | tee -a $LOG_FILE

# 提交本地更改
git add . 
git commit -m "部署更新 ${TIMESTAMP}" || echo "没有新的更改需要提交" | tee -a $LOG_FILE

# 推送到远程
echo "推送到远程..." | tee -a $LOG_FILE
git push origin $current_branch || {
    echo "❌ 推送失败。尝试使用SFTP直接传输..." | tee -a $LOG_FILE
    
    # 创建临时归档文件
    echo "创建临时归档文件..." | tee -a $LOG_FILE
    git archive -o /tmp/deploy_${TIMESTAMP}.tar.gz HEAD
    
    # 使用scp传输文件
    echo "使用SCP传输文件..." | tee -a $LOG_FILE
    scp /tmp/deploy_${TIMESTAMP}.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/tmp/
    
    # 在远程服务器上解压
    ${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
    cd ${REMOTE_DIR}
    tar -xzf /tmp/deploy_${TIMESTAMP}.tar.gz -C /tmp/extract_${TIMESTAMP} --strip-components=0
    cp -r /tmp/extract_${TIMESTAMP}/* ${REMOTE_DIR}/
    rm -rf /tmp/extract_${TIMESTAMP} /tmp/deploy_${TIMESTAMP}.tar.gz
    echo '✅ 文件传输完成'
    " | tee -a $LOG_FILE
    
    # 删除本地临时文件
    rm -f /tmp/deploy_${TIMESTAMP}.tar.gz
}

# 5. 在服务器上更新代码
echo "===== 在服务器上更新代码 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
cd ${REMOTE_DIR}

# 检查是否为Git仓库
if [ -d '.git' ]; then
    # 拉取最新代码
    git fetch
    git checkout $current_branch
    git pull origin $current_branch
    echo '✅ Git拉取完成'
else
    echo '⚠️ 远程目录不是Git仓库，跳过Git拉取'
fi

# 确保权限正确
chmod -R 755 ${REMOTE_DIR}
find ${REMOTE_DIR} -type f -name '*.py' -exec chmod 644 {} \;
find ${REMOTE_DIR} -type d -exec chmod 755 {} \;
echo '✅ 权限已设置'
" | tee -a $LOG_FILE

# 6. 安全重启服务 - 使用零停机策略
echo "===== 安全重启服务 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
cd ${REMOTE_DIR}

# 保存当前配置
cp gunicorn_config.py gunicorn_config.py.bak 2>/dev/null || true

# 首先，启动新的Gunicorn进程
echo '启动新的Gunicorn进程...'
source venv/bin/activate 2>/dev/null || true
 
# 检查是否存在gunicorn_config.py
if [ -f 'gunicorn_config.py' ]; then
    # 先杀掉老的进程
    pkill -f gunicorn 2>/dev/null || true
    sleep 2
    
    # 启动新进程
    mkdir -p logs
    nohup venv/bin/gunicorn -c gunicorn_config.py app:app -D
    
    # 检查新进程
    sleep 2
    if pgrep -f gunicorn > /dev/null; then
        echo '✅ Gunicorn重启成功'
    else
        echo '❌ Gunicorn重启失败，尝试恢复...'
        # 尝试使用备份的配置
        if [ -f 'gunicorn_config.py.bak' ]; then
            cp gunicorn_config.py.bak gunicorn_config.py
            nohup venv/bin/gunicorn -c gunicorn_config.py app:app -D
            sleep 2
            if pgrep -f gunicorn > /dev/null; then
                echo '✅ Gunicorn使用备份配置重启成功'
            else
                echo '❌ Gunicorn无法启动，需要手动检查'
            fi
        fi
    fi
else
    echo '⚠️ 找不到gunicorn_config.py，尝试直接启动...'
    nohup venv/bin/gunicorn app:app -b 0.0.0.0:8080 -D
    sleep 2
    if pgrep -f gunicorn > /dev/null; then
        echo '✅ Gunicorn使用默认配置启动成功'
    else
        echo '❌ Gunicorn无法启动，需要手动检查'
    fi
fi

# 检查Nginx配置并重载
echo '检查Nginx配置...'
nginx -t 2>&1
if [ \$? -eq 0 ]; then
    systemctl reload nginx
    echo '✅ Nginx重载成功'
else
    echo '❌ Nginx配置有误，跳过重载'
fi
" | tee -a $LOG_FILE

# 7. 验证部署
echo "===== 验证部署 =====" | tee -a $LOG_FILE
${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} "
# 检查Gunicorn进程
echo '检查Gunicorn进程:'
ps aux | grep gunicorn | grep -v grep

# 检查Nginx状态
echo '检查Nginx状态:'
systemctl status nginx | grep 'active'

# 测试应用响应
echo '测试应用响应:'
curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/ || echo 'HTTP请求失败'
" | tee -a $LOG_FILE

# 8. 提供回滚指令
echo "===== 部署完成 =====" | tee -a $LOG_FILE
echo "服务器备份位置: ${BACKUP_DIR}" | tee -a $LOG_FILE
echo "如需回滚，请执行:" | tee -a $LOG_FILE
echo "${SSH_CMD} ${REMOTE_USER}@${REMOTE_HOST} \"cp -r ${BACKUP_DIR}/* ${REMOTE_DIR}/; systemctl restart nginx; cd ${REMOTE_DIR}; pkill -f gunicorn; sleep 2; source venv/bin/activate; nohup venv/bin/gunicorn -c gunicorn_config.py app:app -D\"" | tee -a $LOG_FILE

echo "====== 部署完成 ($(date)) ======" | tee -a $LOG_FILE
echo "部署日志已保存到 $LOG_FILE" 