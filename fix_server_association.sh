#!/bin/bash

# 修复服务器上的数据库和文件路径关联
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
APP_DIR="/var/www/question_bank"
DB_PATH="${APP_DIR}/instance/xlct12.db"
PAPERS_DIR="${APP_DIR}/uploads/papers"

echo "开始修复服务器上的数据库和文件关联..."

# 连接到服务器并执行关联修复
sshpass -p "${SSH_PASS}" ssh -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}" "
  echo '准备修复数据库和文件路径关联...'
  cd ${APP_DIR}
  
  # 确保uploads/papers目录存在且权限正确
  if [ ! -d ${PAPERS_DIR} ]; then
    echo '创建papers目录...'
    mkdir -p ${PAPERS_DIR}
  fi
  echo '设置papers目录权限...'
  chmod -R 755 ${APP_DIR}/uploads
  chown -R www-data:www-data ${APP_DIR}/uploads 2>/dev/null || echo '未能修改所有者，但这可能不影响功能'
  
  # 确保新数据库权限正确
  echo '设置数据库文件权限...'
  chmod 664 ${DB_PATH}
  chown www-data:www-data ${DB_PATH} 2>/dev/null || echo '未能修改数据库所有者，但这可能不影响功能'
  
  # 检查并更新app.py中的文件路径配置
  echo '检查并更新app.py中的上传路径配置...'
  if grep -q \"UPLOAD_FOLDER\" app.py; then
    # 确保UPLOAD_FOLDER配置正确
    UPLOAD_DIR_CONFIG=\"app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'papers')\"
    sed -i \"s|app.config\\['UPLOAD_FOLDER'\\].*|${UPLOAD_DIR_CONFIG}|g\" app.py
    echo '上传路径配置已更新'
  else
    echo '警告: 未找到UPLOAD_FOLDER配置'
  fi
  
  # 修复数据库中的文件路径
  echo '修复数据库中的文件路径...'
  if [ -f ${DB_PATH} ]; then
    sqlite3 ${DB_PATH} << EOF
-- 更新文件路径，确保指向正确的位置
UPDATE papers SET file_path = REPLACE(file_path, 'uploads/', 'uploads/papers/') 
WHERE file_path LIKE 'uploads/%' AND file_path NOT LIKE 'uploads/papers/%';

-- 查询检查papers表中的路径数据
SELECT COUNT(*) AS total_papers FROM papers;
SELECT COUNT(*) AS papers_with_correct_path FROM papers WHERE file_path LIKE 'uploads/papers/%';
EOF
    echo '数据库路径已更新'
  else
    echo '错误: 数据库文件不存在!'
  fi
  
  # 重启应用
  echo '重启应用以应用更改...'
  pkill -f 'python.*app\\.py' || echo '没有找到正在运行的应用'
  sleep 2
  nohup python app.py > app.log 2>&1 &
  echo '应用已在后台重新启动'
  
  echo '文件和数据库关联修复完成!'
"

echo "服务器关联修复完成！"
echo "现在服务器应该正确地关联新数据库 xlct12.db 和 uploads/papers 目录。"
echo "请访问网站检查是否一切正常。"
