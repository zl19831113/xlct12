#!/bin/bash
# 修复数据库路径问题

ssh root@120.26.12.100 << 'EOF'
# 1. 检查数据库文件位置
echo "检查数据库文件位置..."
find /var/www/question_bank -name "*.db" -type f

# 2. 修改app.py中的数据库路径
echo "修改app.py中的数据库路径..."
APP_PATH="/var/www/question_bank/app.py"

# 备份app.py
BACKUP_TIME=$(date +%Y%m%d%H%M%S)
APP_BACKUP="${APP_PATH}.bak_${BACKUP_TIME}"
cp $APP_PATH $APP_BACKUP
echo "已创建app.py备份: $APP_BACKUP"

# 修改数据库URI
sed -i "s|app.config\['SQLALCHEMY_DATABASE_URI'\] = 'sqlite:///instance/xlct12.db'|app.config\['SQLALCHEMY_DATABASE_URI'\] = 'sqlite:////var/www/question_bank/instance/xlct12.db'|g" $APP_PATH

# 3. 确保instance目录存在
echo "确保instance目录存在..."
mkdir -p /var/www/question_bank/instance
chown -R www-data:www-data /var/www/question_bank/instance

# 4. 检查xlct12.db是否存在，如果不存在，则从备份恢复
echo "检查数据库文件..."
if [ ! -f "/var/www/question_bank/instance/xlct12.db" ]; then
    echo "xlct12.db不存在，查找可用的数据库文件..."
    DB_FILES=$(find /var/www/question_bank -name "*.db" -type f)
    
    if [ -n "$DB_FILES" ]; then
        FIRST_DB=$(echo "$DB_FILES" | head -1)
        echo "找到数据库文件: $FIRST_DB，复制到instance目录..."
        cp "$FIRST_DB" /var/www/question_bank/instance/xlct12.db
        chown www-data:www-data /var/www/question_bank/instance/xlct12.db
        echo "数据库文件已复制"
    else
        echo "未找到数据库文件，创建空数据库..."
        touch /var/www/question_bank/instance/xlct12.db
        chown www-data:www-data /var/www/question_bank/instance/xlct12.db
    fi
else
    echo "xlct12.db已存在"
fi

# 5. 检查数据库权限
echo "检查数据库权限..."
chmod 664 /var/www/question_bank/instance/xlct12.db
chown www-data:www-data /var/www/question_bank/instance/xlct12.db

# 6. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 7. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 8. 检查日志
echo "检查应用日志..."
sleep 2
journalctl -u question_bank -n 20 --no-pager
EOF
