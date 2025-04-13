#!/bin/bash
# 修复 SQLAlchemy case() 函数语法问题

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始修复 SQLAlchemy case() 函数语法 ====="

# 1. 备份 app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_TIME=$(date +%Y%m%d%H%M%S)
APP_BACKUP="${APP_PATH}.bak_sqlalchemy_${BACKUP_TIME}"
cp $APP_PATH $APP_BACKUP
echo "已创建 app.py 备份: $APP_BACKUP"

# 2. 修改 case() 函数语法
echo "修改 case() 函数语法..."

# 使用 sed 替换所有的 case() 函数调用
# 注意：这是一个复杂的替换，需要处理多行模式

# 首先，替换简单的单行 case 调用
sed -i 's/db\.case(\[\(.*\)\], else_=\(.*\))/case((\1), else_=\2)/g' $APP_PATH

# 然后，处理多行的 case 调用
# 这需要更复杂的处理，我们先尝试一个简单的方法

# 替换 db.case([ 开头的行
sed -i 's/db\.case(\[/case((/g' $APP_PATH

# 替换 ], else_ 的行
sed -i 's/\], else_=\(.*\))/), else_=\1)/g' $APP_PATH

# 3. 确保导入了正确的 case 函数
echo "确保导入了正确的 case 函数..."
if ! grep -q "from sqlalchemy import case" $APP_PATH; then
    # 在文件开头添加导入语句
    sed -i '1s/^/from sqlalchemy import case\n/' $APP_PATH
    echo "已添加 case 函数导入"
fi

# 4. 检查语法
echo "检查 Python 语法..."
python3 -m py_compile $APP_PATH
if [ $? -ne 0 ]; then
    echo "语法检查失败，恢复备份..."
    cp $APP_BACKUP $APP_PATH
    exit 1
fi
echo "语法检查通过！"

# 5. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 6. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 7. 等待服务启动
echo "等待服务启动..."
sleep 3

# 8. 测试筛选功能
echo "测试筛选功能..."
curl -s -X POST http://localhost:5001/filter_papers \
  -H "Content-Type: application/json" \
  -d '{"region":"湖北","page":1,"per_page":5}' | head -20

echo "===== SQLAlchemy case() 函数语法修复完成 ====="
EOF
