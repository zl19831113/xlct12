#!/bin/bash

# 全面调试并重启应用脚本
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank"

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       全面调试并重启应用                        ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "目标服务器: ${REMOTE_SERVER}"
echo -e "应用目录: ${REMOTE_DIR}"
echo -e "调试时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 连接到服务器并执行详细的调试
ssh ${REMOTE_USER}@${REMOTE_SERVER} << 'ENDSSH'
# 1. 彻底停止所有进程
echo "彻底停止所有进程..."
systemctl stop zujuanwang.service || true
systemctl stop nginx || true
pkill -f gunicorn || true
pkill -f python || true

# 睡眠几秒确保所有进程都已停止
sleep 5

# 2. 检查是否有残留进程
echo "检查残留进程..."
ps aux | grep -E 'gunicorn|python' | grep -v grep

# 3. 检查app.py文件权限及完整性
echo "检查应用文件..."
cd /var/www/question_bank
ls -la app.py
head -n 10 app.py

# 4. 确保日志目录存在且可写
echo "准备日志目录..."
mkdir -p /var/www/question_bank/logs
chmod 777 /var/www/question_bank/logs
touch /var/www/question_bank/logs/error.log
touch /var/www/question_bank/logs/access.log
chmod 666 /var/www/question_bank/logs/*.log

# 5. 尝试手动运行应用检查错误
echo "尝试手动启动应用检查错误..."
cd /var/www/question_bank
source venv/bin/activate
python -c "import app; print('应用可以成功导入')"

# 6. 检查并更新gunicorn配置
echo "更新gunicorn配置..."
cat > /var/www/question_bank/gunicorn_config.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
timeout = 300
accesslog = "/var/www/question_bank/logs/access.log"
errorlog = "/var/www/question_bank/logs/error.log"
capture_output = True
loglevel = "debug"
EOF

# 7. 清理pyc文件
echo "清理pyc文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -rf {} +

# 8. 手动启动gunicorn并检查
echo "手动启动gunicorn..."
cd /var/www/question_bank
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app --daemon

# 睡眠几秒让应用启动
sleep 5

# 9. 检查gunicorn是否启动成功
echo "检查gunicorn进程..."
ps aux | grep gunicorn | grep -v grep
netstat -tulpn | grep 8000

# 10. 检查错误日志
echo "检查错误日志..."
tail -n 50 /var/www/question_bank/logs/error.log

# 11. 重启nginx
echo "重启nginx..."
systemctl restart nginx

# 12. 测试网站连接
echo "测试网站连接..."
curl -I http://localhost

# 13. 查看系统服务状态
echo "系统服务状态..."
systemctl status nginx
systemctl status zujuanwang.service

echo "调试和重启过程完成"
ENDSSH

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           调试和重启过程完成!                   ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "完成时间: $(date)"
echo -e "${YELLOW}请再次访问服务器网站验证问题是否解决${NC}"
echo -e "${YELLOW}网站地址: https://xlct12.com/papers${NC}"
