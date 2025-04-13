#!/bin/bash

# 恢复备份脚本
# 创建于: 2025-03-31 23:48:38

APP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
BACKUP_DIR="$(pwd)"

echo "准备从 $BACKUP_DIR 恢复备份到 $APP_DIR"
echo "警告: 此操作将覆盖目标目录中的文件"
read -p "是否继续? (y/n): " response

if [[ "$response" != "y" ]]; then
    echo "已取消恢复操作"
    exit 0
fi

# 停止正在运行的应用程序
echo "停止应用程序..."
pkill -f "python3 $APP_DIR/app.py" || true

# 恢复数据库
echo "恢复数据库..."
cp "$BACKUP_DIR/instance/xlct12.db" "$APP_DIR/instance/"

# 恢复配置文件
echo "恢复配置文件..."
cp "$BACKUP_DIR/app.py" "$APP_DIR/"

echo "恢复完成!"
echo "请重启应用程序以应用更改"
