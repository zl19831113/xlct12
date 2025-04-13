#!/bin/bash

# 脚本用于将localStorage修复注入到client.html文件
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank/templates"

# 创建临时文件
TMP_DIR="/tmp/mobile_fix"
mkdir -p $TMP_DIR

# 上传JavaScript修复文件到服务器
echo "上传JavaScript修复文件到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no /Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/simple_mobile_fix.js $USER@$SERVER:/tmp/mobile_fix.js

# 创建服务器端注入脚本
cat > $TMP_DIR/inject_script.sh << 'EOF'
#!/bin/bash

# 目标文件
TARGET_FILE="/var/www/question_bank/templates/client.html"
JS_FILE="/tmp/mobile_fix.js"

# 创建备份
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
cp $TARGET_FILE ${TARGET_FILE}.bak_${TIMESTAMP}
echo "创建备份: ${TARGET_FILE}.bak_${TIMESTAMP}"

# 创建修复后的client.html文件
TMP_FILE=$(mktemp)

# 提取JavaScript代码
JS_CODE=$(cat $JS_FILE)

# 在</body>标签前插入JavaScript代码
awk -v js_code="$JS_CODE" '
{
    if (match($0, "</body>")) {
        print "<script>";
        print js_code;
        print "</script>";
        print $0;
    } else {
        print $0;
    }
}' $TARGET_FILE > $TMP_FILE

# 替换原始文件
mv $TMP_FILE $TARGET_FILE
chmod 644 $TARGET_FILE

echo "修复完成！"
EOF

# 上传注入脚本到服务器
echo "上传注入脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $TMP_DIR/inject_script.sh $USER@$SERVER:/tmp/inject_script.sh

# 执行注入脚本
echo "在服务器上执行注入脚本..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "chmod +x /tmp/inject_script.sh && /tmp/inject_script.sh"

# 重启服务
echo "重启服务器应用..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

# 清理临时文件
rm -rf $TMP_DIR

echo "操作完成！"
