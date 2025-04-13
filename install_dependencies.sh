#!/bin/bash

# 安装所有缺失的依赖项
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
echo -e "${YELLOW}     安装所有缺失的依赖项并重启应用             ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "目标服务器: ${REMOTE_SERVER}"
echo -e "应用目录: ${REMOTE_DIR}"
echo -e "时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 更新本地requirements.txt，确保包含所有必要的依赖
echo -e "${YELLOW}更新本地requirements.txt...${NC}"
DEPS_TO_ADD=("tqdm" "numpy" "pandas" "scipy" "matplotlib")

for dep in "${DEPS_TO_ADD[@]}"; do
    if ! grep -q "^${dep}$\|^${dep}==" requirements.txt; then
        echo "${dep}" >> requirements.txt
        echo -e "${GREEN}已在requirements.txt中添加${dep}${NC}"
    else
        echo -e "${GREEN}requirements.txt已包含${dep}${NC}"
    fi
done

# 上传更新后的requirements.txt到服务器
echo -e "${YELLOW}上传更新后的requirements.txt到服务器...${NC}"
scp requirements.txt ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/

# 在服务器上安装所有依赖并重启服务
ssh ${REMOTE_USER}@${REMOTE_SERVER} << 'ENDSSH'
cd /var/www/question_bank

# 停止所有现有进程
echo "停止所有进程..."
pkill -f gunicorn || true
systemctl stop zujuanwang.service || true

# 安装所有依赖
echo "安装所有依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 确认依赖已安装
echo "确认关键依赖已安装..."
pip list | grep -E 'tqdm|numpy|pandas|scipy|matplotlib'

# 手动启动应用
echo "手动启动应用..."
mkdir -p logs
touch logs/error.log logs/access.log
chmod 666 logs/*.log

cd /var/www/question_bank
source venv/bin/activate
gunicorn -c gunicorn_config.py app:app --daemon -w 4

# 睡眠几秒让应用启动
sleep 5

# 检查进程是否启动成功
echo "检查进程状态..."
ps aux | grep gunicorn | grep -v grep
netstat -tulpn | grep 8000

# 重启nginx
echo "重启nginx..."
systemctl restart nginx

echo "服务启动完成"
ENDSSH

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           依赖安装并重启完成!                   ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "完成时间: $(date)"
echo -e "${YELLOW}请再次访问服务器网站验证问题是否解决${NC}"
echo -e "${YELLOW}网站地址: https://xlct12.com/papers${NC}"
