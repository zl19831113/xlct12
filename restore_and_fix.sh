#!/bin/bash
# 恢复到原始版本并修复app.py中的case()函数语法

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始恢复和修复 ====="

# 1. 停止服务
echo "停止服务..."
systemctl stop question_bank

# 2. 恢复SQLAlchemy和Flask-SQLAlchemy到系统版本
echo "恢复到系统版本..."
pip uninstall -y sqlalchemy flask-sqlalchemy --break-system-packages
apt-get update
apt-get install -y python3-sqlalchemy python3-flask-sqlalchemy

# 3. 检查版本
echo "安装后的版本:"
pip show sqlalchemy | grep Version || echo "SQLAlchemy not found via pip"
pip show flask-sqlalchemy | grep Version || echo "Flask-SQLAlchemy not found via pip"
echo "系统包版本:"
apt-cache show python3-sqlalchemy | grep Version
apt-cache show python3-flask-sqlalchemy | grep Version

# 4. 备份app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_PATH="${APP_PATH}.bak_$(date +%Y%m%d%H%M%S)"
cp $APP_PATH $BACKUP_PATH
echo "已创建app.py备份: $BACKUP_PATH"

# 5. 修改app.py中的case()函数语法
echo "修改app.py中的case()函数语法..."

# 创建一个临时文件来存储修改后的filter_papers函数
TMP_FILE="/tmp/filter_papers_fixed.py"

# 提取filter_papers函数的开始行号
START_LINE=$(grep -n "def filter_papers" $APP_PATH | head -1 | cut -d':' -f1)
if [ -z "$START_LINE" ]; then
    echo "找不到filter_papers函数，退出"
    exit 1
fi

# 查找下一个函数的开始行号
NEXT_FUNC=$(grep -n "@app.route" $APP_PATH | awk -v start=$START_LINE '$1 > start {print $1; exit}' | cut -d':' -f1)
if [ -z "$NEXT_FUNC" ]; then
    # 如果找不到下一个函数，使用文件末尾
    NEXT_FUNC=$(wc -l < $APP_PATH)
fi
END_LINE=$((NEXT_FUNC - 1))

# 提取函数内容
sed -n "${START_LINE},${END_LINE}p" $APP_PATH > /tmp/filter_papers_original.py

# 修改case()函数调用
sed -i 's/db\.case(\[\(.*\)\], else_=\(.*\))/case((\1), else_=\2)/g' /tmp/filter_papers_original.py
sed -i 's/db\.case(\[/case((/g' /tmp/filter_papers_original.py
sed -i 's/\], else_=\(.*\))/), else_=\1)/g' /tmp/filter_papers_original.py

# 确保导入case函数
if ! grep -q "from sqlalchemy import case" $APP_PATH; then
    sed -i '1s/^/from sqlalchemy import case\n/' $APP_PATH
    echo "已添加case函数导入"
fi

# 替换原始函数
sed -i "${START_LINE},${END_LINE}d" $APP_PATH
sed -i "${START_LINE}r /tmp/filter_papers_original.py" $APP_PATH

# 6. 启动服务
echo "启动服务..."
systemctl start question_bank

# 7. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 8. 等待服务启动
echo "等待服务启动..."
sleep 3

# 9. 测试筛选功能
echo "测试筛选功能..."
curl -s -X POST http://localhost:5001/filter_papers \
  -H "Content-Type: application/json" \
  -d '{"region":"湖北","page":1,"per_page":5}' | head -20

echo "===== 恢复和修复完成 ====="
EOF
