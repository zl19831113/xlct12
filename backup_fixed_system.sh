#!/bin/bash

# 备份修复后的系统，包括数据库和关键配置文件
# 创建于: 2025-03-31

# 设置备份目录和名称
BACKUP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/system_backup_$(date +"%Y%m%d_%H%M%S")"
DB_SOURCE="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/instance/xlct12.db"
APP_PY="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/app.py"

# 创建备份目录
echo "创建备份目录: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/instance"
mkdir -p "$BACKUP_DIR/scripts"

# 备份数据库
echo "备份数据库: xlct12.db"
cp "$DB_SOURCE" "$BACKUP_DIR/instance/"

# 备份app.py
echo "备份配置文件: app.py"
cp "$APP_PY" "$BACKUP_DIR/"

# 备份修复脚本
echo "备份修复脚本"
cp "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/fix_file_association.py" "$BACKUP_DIR/scripts/"
cp "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/force_rename_files.py" "$BACKUP_DIR/scripts/" 2>/dev/null
cp "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/check_db_filenames.py" "$BACKUP_DIR/scripts/" 2>/dev/null

# 创建备份文档
echo "创建备份文档"
cat > "$BACKUP_DIR/README.md" << EOF
# 系统备份文档

备份日期: $(date +"%Y-%m-%d %H:%M:%S")

## 备份内容

1. 数据库: xlct12.db - 已修复文件路径关联
2. 应用配置: app.py - 已配置使用xlct12.db
3. 修复脚本:
   - fix_file_association.py - 用于修复数据库记录与文件系统的关联
   - force_rename_files.py - 用于重命名文件（如有）
   - check_db_filenames.py - 用于检查数据库记录中的文件名格式

## 系统状态

- 已解决数据库与文件系统的关联问题
- 修复了下载功能，可以正确找到文件
- 数据库记录已更新，指向正确的文件路径
- 应用程序配置已统一使用xlct12.db

## 恢复说明

如需恢复备份，请执行以下步骤:

1. 停止应用程序
2. 复制 \`instance/xlct12.db\` 到应用程序的 \`instance\` 目录
3. 复制 \`app.py\` 到应用程序根目录
4. 重启应用程序
EOF

# 创建恢复脚本
echo "创建恢复脚本"
cat > "$BACKUP_DIR/restore.sh" << EOF
#!/bin/bash

# 恢复备份脚本
# 创建于: $(date +"%Y-%m-%d %H:%M:%S")

APP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
BACKUP_DIR="\$(pwd)"

echo "准备从 \$BACKUP_DIR 恢复备份到 \$APP_DIR"
echo "警告: 此操作将覆盖目标目录中的文件"
read -p "是否继续? (y/n): " response

if [[ "\$response" != "y" ]]; then
    echo "已取消恢复操作"
    exit 0
fi

# 停止正在运行的应用程序
echo "停止应用程序..."
pkill -f "python3 \$APP_DIR/app.py" || true

# 恢复数据库
echo "恢复数据库..."
cp "\$BACKUP_DIR/instance/xlct12.db" "\$APP_DIR/instance/"

# 恢复配置文件
echo "恢复配置文件..."
cp "\$BACKUP_DIR/app.py" "\$APP_DIR/"

echo "恢复完成!"
echo "请重启应用程序以应用更改"
EOF

chmod +x "$BACKUP_DIR/restore.sh"

# 统计备份大小
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo ""
echo "备份完成!"
echo "备份保存在: $BACKUP_DIR"
echo "备份大小: $BACKUP_SIZE"
echo ""
echo "如需恢复备份，请进入备份目录并运行 ./restore.sh"
