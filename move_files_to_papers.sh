#!/bin/bash

# 将uploads目录外面的所有非文件夹文件移动到uploads/papers目录

# 本地源目录和目标目录
SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads"
TARGET_DIR="$SOURCE_DIR/papers"

# 确保目标目录存在
mkdir -p "$TARGET_DIR"

echo "开始将uploads目录外的非文件夹文件移动到uploads/papers目录..."

# 查找uploads目录下的所有非文件夹文件（排除papers子目录中的文件）
find "$SOURCE_DIR" -type f -not -path "$TARGET_DIR/*" -not -path "*/\.*" | while read file; do
  # 获取文件名
  filename=$(basename "$file")
  
  # 如果文件不在papers目录中，则移动它
  if [[ "$file" != "$TARGET_DIR/$filename" ]]; then
    echo "移动文件: $filename"
    mv "$file" "$TARGET_DIR/"
  fi
done

echo "移动完成！所有uploads目录外的非文件夹文件已移动到uploads/papers目录。"
echo "现在准备上传更新后的目录结构到服务器..."

# 连接到远程服务器并执行相同的操作
REMOTE_HOST="120.26.12.100"
REMOTE_USER="root"
REMOTE_DIR="/var/www/question_bank/uploads"
SSH_PASS="85497652Sl."

echo "连接到远程服务器并在服务器端执行相同的操作..."

# 使用SSH执行相同的文件移动操作
sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "
  # 确保目标目录存在
  mkdir -p $REMOTE_DIR/papers
  
  echo '开始在服务器上移动文件...'
  
  # 查找uploads目录下的所有非文件夹文件（排除papers子目录中的文件）
  find $REMOTE_DIR -maxdepth 1 -type f | while read file; do
    # 获取文件名
    filename=\$(basename \"\$file\")
    
    echo \"移动文件: \$filename\"
    mv \"\$file\" \"$REMOTE_DIR/papers/\"
  done
  
  echo '服务器端文件移动完成！'
"

echo "所有操作已完成！"
