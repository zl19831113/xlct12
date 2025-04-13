#!/bin/bash

# 脚本用于将分页筛选修复程序上传到服务器并执行
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 上传修复脚本
echo "上传分页筛选修复脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/fix_papers_pagination.py $USER@$SERVER:$REMOTE_DIR/

# 设置执行权限并运行脚本
echo "在服务器上执行修复脚本..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "chmod +x $REMOTE_DIR/fix_papers_pagination.py && python3 $REMOTE_DIR/fix_papers_pagination.py"

# 重启服务
echo "重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

echo "分页筛选修复部署完成！"
