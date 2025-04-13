#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."
REMOTE_PATH="/var/www/question_bank"

# 今天修改的核心文件
MODIFIED_FILES=(
  "app.py"
  "templates/client.html"
  "templates/upload.html"
  "templates/header.html"
  "fix_pagination.js"
)

# 需要上传的目录
DIRECTORIES=(
  "static/css"
  "static/js"
  "static/audio"
)

# 数据库文件
DB_PATH="instance/xlct12.db"
REMOTE_DB_PATH="${REMOTE_PATH}/instance/xlct12.db"

echo "上传今天更新的数据库和核心文件到服务器..."
echo "目标服务器: ${SERVER}"
echo "目标路径: ${REMOTE_PATH}"

# 备份服务器上的数据库
echo "在服务器上备份当前数据库..."
sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "
  if [ -f ${REMOTE_DB_PATH} ]; then
    echo '备份当前数据库...'
    cp ${REMOTE_DB_PATH} ${REMOTE_PATH}/instance/xlct12.db.backup_$(date +"%Y%m%d_%H%M%S")
    echo '数据库已备份'
  else
    echo '警告: 远程数据库文件不存在!'
  fi
"

# 上传数据库文件
echo "上传数据库: ${DB_PATH}"
sshpass -p "${PASS}" scp -o StrictHostKeyChecking=no "${DB_PATH}" "${USER}@${SERVER}:${REMOTE_DB_PATH}"
if [ $? -eq 0 ]; then
  echo "数据库上传成功"
else
  echo "数据库上传失败"
  exit 1
fi

# 上传每个修改的文件
echo "上传核心文件..."
for file in "${MODIFIED_FILES[@]}"; do
  echo "上传: $file"
  sshpass -p "${PASS}" scp -o StrictHostKeyChecking=no "$file" "${USER}@${SERVER}:${REMOTE_PATH}/$file"
  if [ $? -eq 0 ]; then
    echo "成功上传: $file"
  else
    echo "上传失败: $file"
  fi
done

# 上传目录
echo "上传静态资源目录..."
for dir in "${DIRECTORIES[@]}"; do
  echo "上传目录: $dir"
  # 确保远程目录存在
  sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "mkdir -p ${REMOTE_PATH}/$dir"
  # 上传目录内容
  sshpass -p "${PASS}" scp -r -o StrictHostKeyChecking=no "$dir"/* "${USER}@${SERVER}:${REMOTE_PATH}/$dir/"
  if [ $? -eq 0 ]; then
    echo "成功上传目录: $dir"
  else
    echo "上传目录失败: $dir"
  fi
done

# 设置适当的权限
echo "设置权限..."
sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "
  chown -R www-data:www-data ${REMOTE_PATH}
  chmod -R 755 ${REMOTE_PATH}
  chmod -R 644 ${REMOTE_PATH}/instance/xlct12.db
  chmod -R 755 ${REMOTE_PATH}/instance
"

# 重启应用
echo "重启服务器应用..."
sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "
  cd ${REMOTE_PATH} && 
  echo '查找运行中的Python进程...' && 
  pgrep -f 'python.*app\\.py' && 
  echo '关闭现有的Python进程...' && 
  pkill -f 'python.*app\\.py' && 
  echo '等待进程关闭...' && 
  sleep 2 && 
  echo '尝试使用服务管理重启...' && 
  (systemctl restart gunicorn && echo '服务已通过systemctl重启') || 
  echo '使用服务管理重启失败，尝试直接启动...' && 
  cd ${REMOTE_PATH} && 
  (which python3 && nohup python3 app.py > app.log 2>&1 &) || 
  (which python && nohup python app.py > app.log 2>&1 &) || 
  echo '无法找到Python可执行文件，请手动检查服务器配置'
"

echo "上传过程已完成！"
echo "1. 原数据库已在服务器上备份"
echo "2. 更新的数据库和核心文件已上传到服务器"
echo "3. 静态资源目录已更新"
echo "4. 适当的权限已设置"
echo "5. 应用已尝试重启"
echo "请等待几秒钟，然后访问网站检查是否一切正常" 