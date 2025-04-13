#!/bin/bash

# 完整备份脚本（含时间戳）
# 更新日期: 2025-03-27

# 设置备份时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75_full_backup_${TIMESTAMP}"
SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75"
DB_BACKUP="${BACKUP_DIR}/database_backup"
RESTORE_SCRIPT="${BACKUP_DIR}/restore.sh"

# 显示开始备份信息
echo "============================================="
echo "开始创建完整备份..."
echo "备份时间: $(date)"
echo "备份源目录: ${SOURCE_DIR}"
echo "备份目标目录: ${BACKUP_DIR}"
echo "============================================="

# 创建备份目录
mkdir -p "${BACKUP_DIR}"
mkdir -p "${DB_BACKUP}"

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "错误: 无法创建备份目录 ${BACKUP_DIR}"
    exit 1
fi

# 复制所有文件到备份目录
echo "正在复制项目文件..."
rsync -av --exclude="__pycache__/" --exclude="*.pyc" --exclude=".DS_Store" "${SOURCE_DIR}/" "${BACKUP_DIR}/project/"

# 特别备份数据库文件
echo "正在备份数据库文件..."
if [ -f "${SOURCE_DIR}/instance/questions.db" ]; then
    cp "${SOURCE_DIR}/instance/questions.db" "${DB_BACKUP}/questions_${TIMESTAMP}.db"
    echo "数据库备份成功: ${DB_BACKUP}/questions_${TIMESTAMP}.db"
else
    echo "警告: 数据库文件不存在，跳过数据库备份"
fi

# 创建备份信息文件
cat > "${BACKUP_DIR}/backup_info.txt" << EOF2
备份创建时间: $(date)
备份源目录: ${SOURCE_DIR}
备份类型: 完整项目备份（含数据库）
备份ID: ${TIMESTAMP}

此备份包含:
1. 完整项目代码
2. 数据库文件
3. 静态资源和模板
4. 配置文件

最近更新内容:
1. 修复了搜索页面的500内部服务器错误
2. 使搜索结果显示完整题目内容
3. 修复了名校试卷下载页面的筛选按钮
4. 优化了移动端header按钮间距
5. 统一使用"解析"按钮样式（蓝色文字）
6. 优化了移动端页面布局，防止横向滚动
7. 改进了客户端页面的购物车图标样式
EOF2

# 创建恢复脚本
cat > "${RESTORE_SCRIPT}" << EOF3
#!/bin/bash

# 自动恢复脚本
# 创建于: $(date)
# 备份ID: ${TIMESTAMP}

SOURCE_DIR="${BACKUP_DIR}/project"
TARGET_DIR="${SOURCE_DIR}"
DB_SOURCE="${DB_BACKUP}/questions_${TIMESTAMP}.db"
DB_TARGET="${TARGET_DIR}/instance/questions.db"

echo "============================================="
echo "开始恢复备份..."
echo "备份源目录: \${SOURCE_DIR}"
echo "恢复目标目录: \${TARGET_DIR}"
echo "数据库文件: \${DB_SOURCE}"
echo "============================================="

# 确认恢复操作
read -p "确认要恢复备份吗? 这将覆盖目标目录中的文件 [y/N]: " confirm
if [[ "\${confirm}" != "y" && "\${confirm}" != "Y" ]]; then
    echo "恢复操作已取消"
    exit 0
fi

# 检查目标目录
if [ ! -d "\${TARGET_DIR}" ]; then
    echo "目标目录不存在，正在创建..."
    mkdir -p "\${TARGET_DIR}"
fi

# 备份当前状态以防万一
CURRENT_TIMESTAMP=\$(date +"%Y%m%d_%H%M%S")
CURRENT_BACKUP="\${TARGET_DIR}_before_restore_\${CURRENT_TIMESTAMP}"
echo "为安全起见，先备份目标目录到: \${CURRENT_BACKUP}"
cp -R "\${TARGET_DIR}" "\${CURRENT_BACKUP}"

# 复制备份文件到目标目录
echo "正在恢复项目文件..."
rsync -av --delete "\${SOURCE_DIR}/" "\${TARGET_DIR}/"

# 恢复数据库
if [ -f "\${DB_SOURCE}" ]; then
    echo "正在恢复数据库..."
    mkdir -p "\${TARGET_DIR}/instance"
    cp "\${DB_SOURCE}" "\${DB_TARGET}"
    echo "数据库恢复成功"
else
    echo "警告: 未找到数据库备份文件，跳过数据库恢复"
fi

echo "============================================="
echo "恢复完成!"
echo "如需回滚，请使用备份: \${CURRENT_BACKUP}"
echo "============================================="
EOF3

# 设置恢复脚本为可执行
chmod +x "${RESTORE_SCRIPT}"

# 创建文件清单
echo "正在创建文件清单..."
find "${BACKUP_DIR}" -type f | grep -v "__pycache__" | sort > "${BACKUP_DIR}/file_list.txt"

# 计算文件总数和大小
FILE_COUNT=$(find "${BACKUP_DIR}" -type f | grep -v "__pycache__" | wc -l)
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)

echo "============================================="
echo "备份完成!"
echo "备份ID: ${TIMESTAMP}"
echo "备份包含 ${FILE_COUNT} 个文件"
echo "备份总大小: ${BACKUP_SIZE}"
echo "备份路径: ${BACKUP_DIR}"
echo "要恢复此备份，请运行: ${RESTORE_SCRIPT}"
echo "============================================="
