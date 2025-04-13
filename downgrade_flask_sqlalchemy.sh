#!/bin/bash
# 同时降级Flask-SQLAlchemy和SQLAlchemy到兼容版本

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始降级Flask-SQLAlchemy和SQLAlchemy ====="

# 1. 检查当前版本
echo "当前SQLAlchemy版本:"
pip show sqlalchemy | grep Version
echo "当前Flask-SQLAlchemy版本:"
pip show flask-sqlalchemy | grep Version

# 2. 备份app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_PATH="${APP_PATH}.bak_$(date +%Y%m%d%H%M%S)"
cp $APP_PATH $BACKUP_PATH
echo "已创建app.py备份: $BACKUP_PATH"

# 3. 停止服务
echo "停止服务..."
systemctl stop question_bank

# 4. 强制卸载当前版本并安装兼容版本
echo "强制卸载当前版本并安装兼容版本..."
pip uninstall -y flask-sqlalchemy sqlalchemy --break-system-packages
pip install flask-sqlalchemy==2.5.1 sqlalchemy==1.4.46 --break-system-packages

# 5. 确认安装的版本
echo "安装后的SQLAlchemy版本:"
pip show sqlalchemy | grep Version
echo "安装后的Flask-SQLAlchemy版本:"
pip show flask-sqlalchemy | grep Version

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

echo "===== Flask-SQLAlchemy和SQLAlchemy降级完成 ====="
EOF
