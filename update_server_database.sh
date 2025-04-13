#!/bin/bash

# 在远程服务器上更改数据库位置和名称
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
APP_DIR="/var/www/question_bank"

# 新数据库信息
NEW_DB_NAME="questions_new.db"  # 您可以修改新数据库的名称
NEW_DB_DIR="${APP_DIR}/db_storage"  # 新数据库存储位置

# 当前数据库备份信息
CURRENT_DB_PATH="${APP_DIR}/instance/questions.db"
BACKUP_DB_PATH="${APP_DIR}/instance/questions_backup_$(date +"%Y%m%d_%H%M%S").db"

echo "正在连接到服务器 ${REMOTE_HOST} 更新数据库配置..."

# 使用sshpass避免手动输入密码
sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}" "
  echo '开始更新服务器数据库配置...'

  # 1. 备份当前数据库
  if [ -f ${CURRENT_DB_PATH} ]; then
    echo '备份当前数据库...'
    cp ${CURRENT_DB_PATH} ${BACKUP_DB_PATH}
    echo '数据库已备份到: ${BACKUP_DB_PATH}'
  else
    echo '警告: 当前数据库文件不存在! ${CURRENT_DB_PATH}'
  fi

  # 2. 创建新的数据库目录
  echo '创建新的数据库目录...'
  mkdir -p ${NEW_DB_DIR}
  chmod 755 ${NEW_DB_DIR}

  # 3. 如果您有新的数据库上传到本地，请先运行这个脚本，然后再上传新数据库

  # 4. 更新应用配置以使用新的数据库
  echo '修改应用程序配置以使用新数据库位置...'
  if [ -f ${APP_DIR}/app.py ]; then
    # 创建app.py的备份
    cp ${APP_DIR}/app.py ${APP_DIR}/app.py.bak

    # 更新数据库配置 - 使用sed替换数据库路径
    sed -i 's|db_path = os.path.join(instance_path, \"questions.db\")|db_path = os.path.join(\"${NEW_DB_DIR}\", \"${NEW_DB_NAME}\")|g' ${APP_DIR}/app.py
    
    echo '配置已更新，应用将使用新数据库: ${NEW_DB_DIR}/${NEW_DB_NAME}'
  else
    echo '错误: 应用程序文件不存在! ${APP_DIR}/app.py'
    exit 1
  fi

  echo '操作完成! 请上传新数据库并重启应用。'
"

echo "服务器数据库配置已更新。"
echo "现在您需要将新数据库上传到服务器的 ${NEW_DB_DIR}/${NEW_DB_NAME} 位置。"
echo "上传新数据库后，您需要重启服务器应用以使更改生效。"

# 创建上传新数据库的脚本
cat > upload_new_database.sh << EOF
#!/bin/bash

# 上传新数据库到服务器
LOCAL_DB_PATH="您的新数据库本地路径"  # 请修改为您的新数据库路径
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
REMOTE_DB_PATH="${NEW_DB_DIR}/${NEW_DB_NAME}"

echo "上传新数据库到服务器..."

# 使用sshpass和scp上传数据库
sshpass -p "\${SSH_PASS}" scp "\${LOCAL_DB_PATH}" "\${REMOTE_USER}@\${REMOTE_HOST}:\${REMOTE_DB_PATH}"

echo "数据库上传完成。正在重启应用..."

# 重启应用
sshpass -p "\${SSH_PASS}" ssh -o StrictHostKeyChecking=no "\${REMOTE_USER}@\${REMOTE_HOST}" "
  cd /var/www/question_bank && 
  echo '查找运行中的Python进程...' && 
  pgrep -f 'python.*app\\.py' && 
  echo '关闭现有的Python进程...' && 
  pkill -f 'python.*app\\.py' && 
  echo '等待进程关闭...' && 
  sleep 2 && 
  echo '启动应用程序...' && 
  nohup python app.py > app.log 2>&1 & 
  echo '应用已在后台重新启动'
"

echo "新数据库已上传，应用已重启。"
EOF

chmod +x upload_new_database.sh

echo "已创建上传新数据库的脚本: upload_new_database.sh"
echo "请修改脚本中的LOCAL_DB_PATH为您新数据库的本地路径，然后运行该脚本上传数据库。"
