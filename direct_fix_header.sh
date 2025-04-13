#!/bin/bash
# 直接修复header.html文件

ssh root@120.26.12.100 << 'EOF'
# 检查header.html内容
echo "检查header.html文件内容..."
HEADER_PATH="/var/www/question_bank/templates/header.html"

# 显示当前的问题行
echo "当前问题行:"
grep -n "upload_page" $HEADER_PATH

# 备份header.html
BACKUP_PATH="${HEADER_PATH}.bak_$(date +%Y%m%d%H%M%S)"
cp $HEADER_PATH $BACKUP_PATH
echo "已创建备份: $BACKUP_PATH"

# 直接编辑文件，将所有的upload_page替换为upload_paper
echo "修改header.html文件..."
sed -i 's/upload_page/upload_paper/g' $HEADER_PATH

# 确认修改
echo "修改后的内容:"
grep -n "upload_paper" $HEADER_PATH

# 重启服务
echo "重启服务..."
systemctl restart question_bank

# 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20
EOF
