#!/bin/bash

# 修复client.html，移除解析内容中的题目序号
# 作用于本地和服务器端

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 移除解析内容中的题目序号 ====="

# 1. 修改本地文件
echo "1. 修改本地文件..."
sed -i '' 's/let lines = \[`第${idx + 1}题：`\];/let lines = [];/' "${LOCAL_DIR}/templates/client.html"

# 2. 检查是否修改成功
echo "2. 验证本地修改..."
grep -A 2 "let lines =" "${LOCAL_DIR}/templates/client.html"

# 3. 上传修改后的文件到服务器
echo "3. 上传修改后的文件到服务器..."
sshpass -p "${REMOTE_PASSWORD}" scp "${LOCAL_DIR}/templates/client.html" "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/templates/client.html"

# 4. 在服务器上执行相同的修改(以防上传失败)
echo "4. 在服务器上执行相同的修改..."
eval "${SSH_CMD} \"sed -i 's/let lines = \\\[\\`第\${idx + 1}题：\\`\\\];/let lines = [];/' ${REMOTE_DIR}/templates/client.html\""

# 5. 检查服务器上的修改
echo "5. 验证服务器上的修改..."
eval "${SSH_CMD} \"grep -A 2 'let lines =' ${REMOTE_DIR}/templates/client.html\""

# 6. 重启服务器应用程序(可选)
echo "6. 重启应用程序..."
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && systemctl restart nginx\""

echo "===== 修改完成 ====="
echo "现在解析内容中不会显示题目序号"
