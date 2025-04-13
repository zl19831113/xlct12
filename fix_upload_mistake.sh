#!/bin/bash

# 恢复网站文件（不包括uploads目录）
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
SSH_PASS="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

echo "正在连接到服务器修复错误..."

# 尝试从之前的备份恢复网站文件（除uploads目录外）
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "
  cd $REMOTE_DIR && 
  echo '查找最近的网站备份...' &&
  if [ -d '/var/www/backups/zujuanwang76' ]; then
    echo '找到备份，正在恢复网站文件（除uploads目录外）...' &&
    LATEST_BACKUP=\$(ls -td /var/www/backups/zujuanwang76/* | head -1) &&
    echo '使用备份: '\$LATEST_BACKUP &&
    # 复制所有文件，除了uploads目录
    find \$LATEST_BACKUP -type f -not -path '*/uploads/*' | while read file; do
      REL_PATH=\${file#\$LATEST_BACKUP/} &&
      mkdir -p \$(dirname $REMOTE_DIR/\$REL_PATH) &&
      cp \$file $REMOTE_DIR/\$REL_PATH
    done &&
    echo '网站文件已恢复'
  else
    echo '未找到备份，无法自动恢复' 
  fi
"

echo "修复操作已尝试执行。接下来修正uploads目录的上传脚本。"
