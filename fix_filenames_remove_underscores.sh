#!/bin/bash

# 批量修改uploads/papers目录下所有文件的文件名，去除下划线，使其符合数据库记录格式
# 脚本在执行重命名操作前会创建备份

PAPERS_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/papers"
PAPERS_PAPERS_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/papers/papers"
BACKUP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads_backup_$(date +"%Y%m%d_%H%M%S")"

# 创建备份目录
mkdir -p "$BACKUP_DIR"
echo "创建备份目录: $BACKUP_DIR"

# 备份整个uploads目录
echo "正在备份当前uploads目录..."
cp -R "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads" "$BACKUP_DIR/"
echo "备份完成。"

# 计数器
count_total=0
count_renamed=0
count_errors=0
count_already_renamed=0

# 处理uploads/papers目录
echo "开始处理 uploads/papers 目录中的文件..."
if [ -d "$PAPERS_DIR" ]; then
  find "$PAPERS_DIR" -type f -maxdepth 1 | while read file; do
    ((count_total++))
    filename=$(basename "$file")
    
    # 检查文件名是否包含下划线
    if [[ "$filename" == *"_"* ]]; then
      # 创建无下划线版本的文件名
      newname=$(echo "$filename" | tr -d '_')
      
      # 确保目标文件名不存在
      if [ ! -f "$PAPERS_DIR/$newname" ]; then
        echo "重命名文件: $filename -> $newname"
        mv "$file" "$PAPERS_DIR/$newname"
        ((count_renamed++))
      else
        echo "警告: 目标文件已存在，跳过重命名: $filename -> $newname"
        ((count_errors++))
      fi
    else
      ((count_already_renamed++))
      echo "文件已符合格式，无需修改: $filename"
    fi
  done
fi

# 处理uploads/papers/papers目录 (如果存在)
echo -e "\n开始处理 uploads/papers/papers 目录中的文件..."
if [ -d "$PAPERS_PAPERS_DIR" ]; then
  find "$PAPERS_PAPERS_DIR" -type f | while read file; do
    ((count_total++))
    filename=$(basename "$file")
    
    # 检查文件名是否包含下划线
    if [[ "$filename" == *"_"* ]]; then
      # 创建无下划线版本的文件名
      newname=$(echo "$filename" | tr -d '_')
      
      # 确保目标文件名不存在
      if [ ! -f "$PAPERS_PAPERS_DIR/$newname" ]; then
        echo "重命名文件: $filename -> $newname"
        mv "$file" "$PAPERS_PAPERS_DIR/$newname"
        ((count_renamed++))
      else
        echo "警告: 目标文件已存在，跳过重命名: $filename -> $newname"
        ((count_errors++))
      fi
    else
      ((count_already_renamed++))
      echo "文件已符合格式，无需修改: $filename"
    fi
  done
else
  echo "uploads/papers/papers 目录不存在，跳过处理"
fi

echo -e "\n操作完成!"
echo "总共处理文件: $count_total"
echo "重命名文件数: $count_renamed"
echo "已符合格式文件数: $count_already_renamed"
echo "出错或跳过文件数: $count_errors"
echo "备份保存在: $BACKUP_DIR"
