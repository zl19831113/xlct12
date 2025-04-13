#!/bin/bash

# 脚本说明: 快速备份到外接硬盘"小鹿出题"
# 创建日期: 2025-04-01

# 设置备份目录
EXTERNAL_DRIVE="/Volumes/小鹿出题"
PROJECT_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_NAME="zujuanwang76_backup_${TIMESTAMP}"
BACKUP_PATH="${EXTERNAL_DRIVE}/${BACKUP_NAME}"

# 检查外接硬盘是否已挂载
if [ ! -d "$EXTERNAL_DRIVE" ]; then
  echo "错误: 外接硬盘'小鹿出题'未挂载，请连接后重试"
  exit 1
fi

# 检查硬盘空间
SOURCE_SIZE=$(du -sm "$PROJECT_DIR" | cut -f1)
AVAILABLE_SPACE=$(df -m "$EXTERNAL_DRIVE" | tail -1 | awk '{print $4}')

if [ "$AVAILABLE_SPACE" -lt "$SOURCE_SIZE" ]; then
  echo "错误: 外接硬盘空间不足"
  echo "需要: ${SOURCE_SIZE}MB"
  echo "可用: ${AVAILABLE_SPACE}MB"
  exit 1
fi

# 显示开始备份信息
echo "==== 开始备份 - 优化速度模式 ===="
echo "源目录: $PROJECT_DIR"
echo "目标目录: $BACKUP_PATH"
echo "时间戳: $TIMESTAMP"

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 复制项目文件 - 使用速度优化选项
echo "正在快速复制核心文件..."
rsync -av \
  --exclude ".git" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.pyo" \
  --exclude "*.tmp" \
  --exclude ".DS_Store" \
  "$PROJECT_DIR/" "$BACKUP_PATH/"

# 特别处理数据库文件
echo "正在备份数据库文件..."
DB_PATH="$PROJECT_DIR/instance"
DB_BACKUP_PATH="$BACKUP_PATH/instance"

# 确保数据库备份目录存在
mkdir -p "$DB_BACKUP_PATH"

# 使用SQLite的.backup命令进行安全备份
if [ -f "$DB_PATH/xlct12.db" ]; then
  echo "备份SQLite数据库..."
  sqlite3 "$DB_PATH/xlct12.db" ".backup '$DB_BACKUP_PATH/xlct12.db'"
  echo "数据库备份完成"
elif [ -f "$DB_PATH/questions.db" ]; then
  echo "备份SQLite数据库..."
  sqlite3 "$DB_PATH/questions.db" ".backup '$DB_BACKUP_PATH/questions.db'"
  echo "数据库备份完成"
else
  echo "警告: 主数据库文件不存在"
  # 尝试直接复制所有数据库文件
  cp -R "$DB_PATH"/*.db "$DB_BACKUP_PATH/" 2>/dev/null
  echo "尝试直接复制数据库文件"
fi

# 创建备份信息文件
INFO_FILE="$BACKUP_PATH/backup_info.txt"
echo "备份名称: $BACKUP_NAME" > "$INFO_FILE"
echo "备份时间: $(date)" >> "$INFO_FILE"
echo "备份内容: zujuanwang76项目（含数据库）" >> "$INFO_FILE"
echo "备份类型: 快速备份到外接硬盘" >> "$INFO_FILE"
echo "试卷数量: $(sqlite3 "$PROJECT_DIR/instance/xlct12.db" "SELECT count(*) FROM papers;" 2>/dev/null || echo "无法获取")" >> "$INFO_FILE"

# 创建latest链接
LATEST_LINK="${EXTERNAL_DRIVE}/zujuanwang76_latest"
rm -f "$LATEST_LINK" 2>/dev/null
ln -s "$BACKUP_PATH" "$LATEST_LINK"
echo "已更新最新备份链接: $LATEST_LINK -> $BACKUP_PATH"

# 保留最近3个备份 (减少占用空间)
echo "清理旧备份..."
ls -dt "${EXTERNAL_DRIVE}/zujuanwang76_backup_"* | tail -n +4 | xargs rm -rf 2>/dev/null

# 计算备份大小
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

# 显示备份完成信息
echo "==== 备份完成 ===="
echo "备份位置: $BACKUP_PATH"
echo "备份大小: $BACKUP_SIZE"
echo "最新备份链接: $LATEST_LINK"
echo "保留备份数: 3"
echo "备份时间: $(date)"
