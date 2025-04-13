#!/bin/bash
# 直接修复filter_papers函数

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始直接修复filter_papers函数 ====="

# 1. 备份app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_PATH="${APP_PATH}.bak_$(date +%Y%m%d%H%M%S)"
cp $APP_PATH $BACKUP_PATH
echo "已创建备份: $BACKUP_PATH"

# 2. 直接修改app.py文件
echo "修改app.py文件中的case()函数调用..."

# 确保导入case函数
if ! grep -q "from sqlalchemy import case" $APP_PATH; then
    sed -i '1s/^/from sqlalchemy import case\n/' $APP_PATH
    echo "已添加case函数导入"
fi

# 使用sed直接替换case函数调用
# 替换 db.case([(condition, value)], else_=x) 为 case((condition, value), else_=x)
sed -i 's/db\.case(\[\(Paper\.region == "湖北", 1\)\], else_=0)/case((Paper.region == "湖北", 1), else_=0)/g' $APP_PATH

# 3. 重启服务
echo "重启服务..."
systemctl restart question_bank

# 4. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 5. 等待服务启动
echo "等待服务启动..."
sleep 3

# 6. 测试筛选功能
echo "测试筛选功能..."
curl -s -X POST http://localhost:5001/filter_papers \
  -H "Content-Type: application/json" \
  -d '{"region":"湖北","page":1,"per_page":5}' | head -20

echo "===== 直接修复完成 ====="
EOF
