#!/bin/bash

# 将分页修复应用到服务器
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 本地路径
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"

echo "===== 开始应用服务器分页修复 ====="

# 上传修复脚本到服务器
echo "1. 上传修复脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/direct_pagination_fix.py $USER@$SERVER:$REMOTE_DIR/

# 在服务器上执行修复
echo "2. 在服务器上执行修复..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_DIR && python3 direct_pagination_fix.py $REMOTE_DIR/templates/papers.html"

# 重启服务
echo "3. 重启服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

# 检查服务状态
echo "4. 检查服务状态..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl status zujuanwang.service | head -n 20"

echo "===== 修复完成 ====="
echo "请访问网站检查分页和筛选功能是否正常工作。"
