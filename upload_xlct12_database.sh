#!/bin/bash

# 上传xlct12.db数据库到服务器并配置应用使用它
LOCAL_DB_PATH="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/instance/xlct12.db"
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
APP_DIR="/var/www/question_bank"

# 新数据库信息
NEW_DB_NAME="xlct12.db"
NEW_DB_DIR="${APP_DIR}/instance"  # 保持在instance目录，但使用新名称

# 当前数据库备份信息
CURRENT_DB_PATH="${APP_DIR}/instance/questions.db"
BACKUP_DB_PATH="${APP_DIR}/instance/questions_backup_$(date +"%Y%m%d_%H%M%S").db"

echo "准备上传新数据库 ${NEW_DB_NAME} 到服务器..."

# 1. 首先在服务器上进行配置和备份
echo "先在服务器上备份原数据库并更新配置..."
sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}" "
  echo '开始在服务器上更新数据库配置...'

  # 备份当前数据库
  if [ -f ${CURRENT_DB_PATH} ]; then
    echo '备份当前数据库...'
    cp ${CURRENT_DB_PATH} ${BACKUP_DB_PATH}
    echo '数据库已备份到: ${BACKUP_DB_PATH}'
  else
    echo '警告: 当前数据库文件不存在!'
  fi

  # 更新应用配置以使用新的数据库
  echo '修改应用程序配置以使用新数据库...'
  if [ -f ${APP_DIR}/app.py ]; then
    # 创建app.py的备份
    cp ${APP_DIR}/app.py ${APP_DIR}/app.py.bak_$(date +"%Y%m%d_%H%M%S")
    
    # 更新数据库配置 - 使用sed替换数据库路径
    sed -i 's|db_path = os.path.join(instance_path, \"questions.db\")|db_path = os.path.join(instance_path, \"${NEW_DB_NAME}\")|g' ${APP_DIR}/app.py
    
    echo '配置已更新，应用将使用新数据库: ${NEW_DB_DIR}/${NEW_DB_NAME}'
  else
    echo '错误: 应用程序文件不存在!'
    exit 1
  fi
"

# 2. 上传新数据库到服务器
echo "开始上传数据库文件到服务器 ${REMOTE_HOST}:${NEW_DB_DIR}/${NEW_DB_NAME}..."
sshpass -p "${SSH_PASS}" scp "${LOCAL_DB_PATH}" "${REMOTE_USER}@${REMOTE_HOST}:${NEW_DB_DIR}/${NEW_DB_NAME}"
echo "数据库上传完成。"

# 3. 重启应用
echo "重启服务器应用..."
sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}" "
  cd ${APP_DIR} && 
  echo '查找运行中的Python进程...' && 
  pgrep -f 'python.*app\\.py' && 
  echo '关闭现有的Python进程...' && 
  pkill -f 'python.*app\\.py' && 
  echo '等待进程关闭...' && 
  sleep 2 && 
  echo '启动应用程序...' && 
  cd ${APP_DIR} && 
  nohup python app.py > app.log 2>&1 & 
  echo '应用已在后台重新启动' || 
  echo '没有找到运行中的应用，正在启动新实例...' && 
  cd ${APP_DIR} && 
  nohup python app.py > app.log 2>&1 & 
  echo '应用已在后台启动'
"

echo "整个过程已完成！"
echo "1. 原数据库已备份"
echo "2. xlct12.db 数据库已上传到服务器"
echo "3. 应用配置已更新以使用新数据库"
echo "4. 应用已重启"
echo "请等待几秒钟，然后访问网站检查是否一切正常"
