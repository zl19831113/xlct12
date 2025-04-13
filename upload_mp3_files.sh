#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."
REMOTE_PATH="/var/www/question_bank"

echo "上传MP3文件到服务器..."
echo "目标服务器: ${SERVER}"

# 需要上传的目录
AUDIO_DIRS=(
  "static/audio"
  "static/uploads/audio"
  "uploads/papers/audio"
)

# 遍历所有音频目录并上传
for dir in "${AUDIO_DIRS[@]}"; do
  echo "上传目录: $dir"
  
  # 确保目录存在
  if [ ! -d "$dir" ]; then
    echo "警告: 本地目录 $dir 不存在，跳过..."
    continue
  fi
  
  # 检查目录中是否有文件
  if [ -z "$(ls -A $dir 2>/dev/null)" ]; then
    echo "警告: 目录 $dir 为空，跳过..."
    continue
  fi
  
  # 确保远程目录存在
  echo "创建远程目录: ${REMOTE_PATH}/$dir"
  sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "mkdir -p ${REMOTE_PATH}/$dir"
  
  # 上传目录内容
  echo "上传 $dir 中的文件..."
  sshpass -p "${PASS}" scp -r -o StrictHostKeyChecking=no "$dir"/* "${USER}@${SERVER}:${REMOTE_PATH}/$dir/"
  
  if [ $? -eq 0 ]; then
    echo "目录 $dir 上传成功"
  else
    echo "目录 $dir 上传失败"
  fi
done

# 设置适当的权限
echo "设置权限..."
sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "
  chown -R www-data:www-data ${REMOTE_PATH}/static
  chown -R www-data:www-data ${REMOTE_PATH}/uploads
  chmod -R 755 ${REMOTE_PATH}/static
  chmod -R 755 ${REMOTE_PATH}/uploads
"

echo "MP3文件上传已完成！"

# 检查音频文件是否可以正常访问
echo "检查服务器上的音频文件..."
sshpass -p "${PASS}" ssh -o StrictHostKeyChecking=no "${USER}@${SERVER}" "
  echo '检查音频文件目录:'
  ls -la ${REMOTE_PATH}/static/audio/ 2>/dev/null || echo '没有静态音频文件目录'
  echo '检查上传的音频文件目录:'
  ls -la ${REMOTE_PATH}/uploads/papers/audio/ | head -5 2>/dev/null || echo '没有上传的音频文件目录'
  echo '上传的音频文件数量:'
  find ${REMOTE_PATH}/uploads/papers/audio -type f -name '*.mp3' | wc -l 2>/dev/null || echo '无法计数音频文件'
" 