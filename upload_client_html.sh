#!/bin/bash

# 脚本用于上传修改后的client.html文件到服务器
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank/templates"
LOCAL_FILE="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/templates/client.html"

# 显示上传信息
echo "准备上传client.html文件到服务器..."
echo "本地文件: $LOCAL_FILE"
echo "目标服务器: $SERVER"
echo "目标目录: $REMOTE_DIR"

# 创建服务器上的备份
echo "在服务器上创建备份..."
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_COMMAND="cp $REMOTE_DIR/client.html $REMOTE_DIR/client.html.bak_$TIMESTAMP"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "$BACKUP_COMMAND"

if [ $? -eq 0 ]; then
    echo "服务器备份创建成功: client.html.bak_$TIMESTAMP"
else
    echo "警告: 无法在服务器上创建备份，但将继续上传"
fi

# 上传文件
echo "正在上传client.html文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$LOCAL_FILE" "$USER@$SERVER:$REMOTE_DIR/client.html"

if [ $? -eq 0 ]; then
    echo "文件上传成功!"
    
    # 重启服务器应用
    echo "正在重启服务器应用..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"
    
    if [ $? -eq 0 ]; then
        echo "服务器应用重启成功!"
    else
        echo "警告: 服务器应用重启失败，请手动重启"
    fi
else
    echo "错误: 文件上传失败!"
    exit 1
fi

echo "操作完成!"
