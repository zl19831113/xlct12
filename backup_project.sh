#!/bin/bash

# 创建一个完整备份项目的脚本

# 设置变量
BACKUP_ROOT="/Volumes/小鹿出题/小鹿备份"
PROJECT_DIR=$(pwd)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/zujuanwang_backup_${TIMESTAMP}"

# 检查备份目录是否存在，如果不存在则创建
if [ ! -d "$BACKUP_ROOT" ]; then
    echo "备份根目录 $BACKUP_ROOT 不存在，请确认磁盘已挂载"
    exit 1
fi

# 创建新的备份目录
echo "===== 开始备份项目 ====="
echo "项目目录: $PROJECT_DIR"
echo "备份目录: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# 使用rsync进行备份，排除不必要的目录
echo "步骤1: 复制文件到备份目录..."
rsync -av --progress \
    --exclude=".git" \
    --exclude="venv" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="temp_update_*" \
    --exclude="node_modules" \
    --exclude=".DS_Store" \
    "$PROJECT_DIR/" "$BACKUP_DIR/"

# 备份完成后的状态
if [ $? -eq 0 ]; then
    # 计算备份大小
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    TOTAL_FILES=$(find "$BACKUP_DIR" -type f | wc -l)
    
    echo "===== 备份完成 ====="
    echo "备份位置: $BACKUP_DIR"
    echo "备份大小: $BACKUP_SIZE"
    echo "文件总数: $TOTAL_FILES"
    echo "备份时间: $(date)"
    
    # 创建备份信息文件
    echo "项目备份信息" > "$BACKUP_DIR/backup_info.txt"
    echo "备份时间: $(date)" >> "$BACKUP_DIR/backup_info.txt"
    echo "备份大小: $BACKUP_SIZE" >> "$BACKUP_DIR/backup_info.txt"
    echo "文件总数: $TOTAL_FILES" >> "$BACKUP_DIR/backup_info.txt"
    echo "源目录: $PROJECT_DIR" >> "$BACKUP_DIR/backup_info.txt"
    
    echo "备份信息已保存到 $BACKUP_DIR/backup_info.txt"
    echo "备份过程成功完成"
else
    echo "备份过程中出现错误!"
    exit 1
fi 