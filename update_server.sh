#!/bin/bash

# 创建一个用于服务器更新的简单脚本

# 设置变量
SERVER="120.26.12.100"
USER="root"
REMOTE_PATH="/var/www/zujuanwang"

# 报告开始
echo "===== 开始更新服务器 ====="
echo "服务器地址: $SERVER"
echo "远程路径: $REMOTE_PATH"

# 1. 创建一个临时目录，拷贝需要的文件
echo "步骤1: 创建临时目录并复制文件..."
TEMP_DIR="temp_update_$(date +%Y%m%d%H%M%S)"
mkdir -p $TEMP_DIR/templates
cp templates/client.html templates/smart_paper.html $TEMP_DIR/templates/
cp app.py $TEMP_DIR/
echo "文件已复制到临时目录: $TEMP_DIR"

# 2. 将文件上传到服务器
echo "步骤2: 上传文件到服务器..."
scp -r $TEMP_DIR/* $USER@$SERVER:$REMOTE_PATH/
if [ $? -eq 0 ]; then
    echo "文件上传成功!"
else
    echo "文件上传失败!"
    exit 1
fi

# 3. 备份服务器上的原始文件
echo "步骤3: 在服务器上备份原始文件..."
ssh $USER@$SERVER "cd $REMOTE_PATH && \
    cp -f templates/client.html templates/client.html.bak_$(date +%Y%m%d%H%M%S) && \
    cp -f templates/smart_paper.html templates/smart_paper.html.bak_$(date +%Y%m%d%H%M%S) && \
    cp -f app.py app.py.bak_$(date +%Y%m%d%H%M%S)"

# 4. 重启服务器
echo "步骤4: 重启服务..."
ssh $USER@$SERVER "cd $REMOTE_PATH && \
    systemctl restart zujuanwang.service"

# 5. 清理临时目录
echo "步骤5: 清理临时文件..."
rm -rf $TEMP_DIR

echo "===== 服务器更新完成 ====="
echo "请访问网站验证更新是否成功" 