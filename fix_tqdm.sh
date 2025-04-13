#!/bin/bash

# 修复tqdm模块缺失问题
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
echo -e "${YELLOW}     修复tqdm模块缺失并重启应用                  ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "目标服务器: ${REMOTE_SERVER}"
echo -e "应用目录: ${REMOTE_DIR}"
echo -e "修复时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 检查本地requirements.txt，确保包含tqdm
echo -e "${YELLOW}检查并更新本地requirements.txt...${NC}"
if ! grep -q "tqdm" requirements.txt; then
    echo "tqdm" >> requirements.txt
    echo -e "${GREEN}已在本地requirements.txt中添加tqdm${NC}"
else
    echo -e "${GREEN}本地requirements.txt已包含tqdm${NC}"
fi

# 上传更新后的requirements.txt到服务器
echo -e "${YELLOW}上传更新后的requirements.txt到服务器...${NC}"
scp requirements.txt ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/

# 在服务器上安装tqdm并重启服务
ssh ${REMOTE_USER}@${REMOTE_SERVER} << 'ENDSSH'
cd /var/www/question_bank

# 安装tqdm模块
echo "安装tqdm模块..."
source venv/bin/activate
pip install tqdm

# 确认tqdm已安装
echo "确认tqdm模块已安装..."
python -c "import tqdm; print('tqdm模块已成功安装, 版本:', tqdm.__version__)" || echo "tqdm安装失败!"

# 重启服务
echo "重启服务..."
systemctl restart zujuanwang.service
systemctl restart nginx

# 验证服务状态
echo "验证服务状态..."
systemctl status zujuanwang.service
ps aux | grep -E 'gunicorn|python' | grep -v grep
netstat -tulpn | grep -E '8000|80'

echo "修复过程完成"
ENDSSH

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}           问题修复尝试完成!                     ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "完成时间: $(date)"
echo -e "${YELLOW}请再次访问服务器网站验证问题是否解决${NC}"
echo -e "${YELLOW}网站地址: https://xlct12.com/papers${NC}"
