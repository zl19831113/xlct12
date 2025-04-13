#!/bin/bash

# 创建详细备份脚本 - 优化版
# 创建于: 2025-03-28
# 上次更新: 2025-03-28 07:38

# 设置详细备份时间戳
DATE_STAMP=$(date +"%Y-%m-%d")
TIME_STAMP=$(date +"%H-%M-%S")
FULL_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DAY_OF_WEEK=$(date +"%A")
MONTH_NAME=$(date +"%B")

# 设置备份目录 - 使用更简洁的路径
BACKUP_ROOT="/Users/sl19831113/Desktop/备份"
BACKUP_NAME="zujuanwang75_backup_${DATE_STAMP}_${TIME_STAMP}"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"
SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75"
RESTORE_SCRIPT="${BACKUP_DIR}/restore.sh"
BACKUP_LOG="${BACKUP_DIR}/backup_log.txt"

# 要排除的文件和目录
EXCLUDE_PATTERNS=(
    "*.git*"
    "*__pycache__*"
    "*backup_2*"
    "*zujuanwang75_backup_*"
    "*instance/questions.db-journal"
    "*.pyc"
    "*/__pycache__/*"
    "*/\.*"
)

# 显示开始备份信息
echo "开始创建备份..."
echo "备份时间: $(date)"
echo "备份源目录: ${SOURCE_DIR}"
echo "备份目标目录: ${BACKUP_DIR}"

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "错误: 无法创建备份目录 ${BACKUP_DIR}"
    exit 1
fi

# 创建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

# 检查磁盘空间
FREE_SPACE=$(df -h "${BACKUP_ROOT}" | awk 'NR==2 {print $4}')
SOURCE_SIZE=$(du -sh "${SOURCE_DIR}" | cut -f1)

echo "源目录大小: ${SOURCE_SIZE}"
echo "可用磁盘空间: ${FREE_SPACE}"
echo "开始备份前检查磁盘空间..."

# 使用rsync而非cp，并排除不需要的文件
echo "正在复制文件...(排除非必要文件)"
eval "rsync -av --progress ${EXCLUDE_OPTIONS} \"${SOURCE_DIR}/\" \"${BACKUP_DIR}/\""

# 创建详细备份日志
echo "===========================================" > "${BACKUP_LOG}"
echo "      详细备份日志 - ${DATE_STAMP}      " >> "${BACKUP_LOG}"
echo "===========================================" >> "${BACKUP_LOG}"
echo "" >> "${BACKUP_LOG}"
echo "备份时间信息:" >> "${BACKUP_LOG}"
echo "- 备份日期: ${DATE_STAMP} (${DAY_OF_WEEK})" >> "${BACKUP_LOG}"
echo "- 备份时间: ${TIME_STAMP}" >> "${BACKUP_LOG}"
echo "- 月份: ${MONTH_NAME}" >> "${BACKUP_LOG}"
echo "- 时间戳: ${FULL_TIMESTAMP}" >> "${BACKUP_LOG}"
echo "" >> "${BACKUP_LOG}"
echo "文件统计:" >> "${BACKUP_LOG}"
echo "- 总文件数: $(find "${SOURCE_DIR}" -type f | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "- HTML文件: $(find "${SOURCE_DIR}" -name "*.html" | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "- CSS文件: $(find "${SOURCE_DIR}" -name "*.css" | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "- JS文件: $(find "${SOURCE_DIR}" -name "*.js" | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "- Python文件: $(find "${SOURCE_DIR}" -name "*.py" | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "- 图像文件: $(find "${SOURCE_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.gif" -o -name "*.svg" | wc -l | xargs)" >> "${BACKUP_LOG}"
echo "" >> "${BACKUP_LOG}"
echo "最近修改的文件(7天内):" >> "${BACKUP_LOG}"
find "${SOURCE_DIR}" -type f -mtime -7 | sort >> "${BACKUP_LOG}"

# 创建备份信息文件
cat > "${BACKUP_DIR}/backup_info.txt" << EOF
===========================================
              项目备份信息                
===========================================

备份创建时间: $(date)
备份源目录: ${SOURCE_DIR}
备份内容: 完整项目备份
备份日期: ${DATE_STAMP} (${DAY_OF_WEEK})
备份时间: ${TIME_STAMP}

主要修改内容:
1. 优化了移动端paper.html的下载按钮（更小、更现代、更简约）
2. 更新了client.html的样式，与新下载的保持一致
3. 移除了组卷的方框
4. 将"查看答案"统一改为蓝色文字样式的"解析"
5. 优化了购物车样式为白底蓝色
6. 修复了移动端左右晃动问题
7. 修复了搜索页500错误
8. 解决了"筛选错误: List argument must consist only of tuples or dictionaries"
9. 修复了"'str' object has no attribute 'isoformat'"错误
10. 优化了移动端字体大小和按钮对齐，确保解析和组卷按钮文字样式一致
11. 修复了按钮文本大小不一致的问题
12. 优化了移动端选项和问题间距

系统信息:
- 操作系统: $(uname -s)
- 主机名: $(hostname)
- 用户: $(whoami)
- Python版本: $(python3 --version 2>&1)
EOF

# 创建恢复脚本
cat > "${RESTORE_SCRIPT}" << EOF
#!/bin/bash

# 自动恢复脚本
# 创建于: $(date)

SOURCE_DIR="${BACKUP_DIR}"
TARGET_DIR="${SOURCE_DIR}"

echo "开始恢复备份..."
echo "备份源目录: \${SOURCE_DIR}"
echo "恢复目标目录: \${TARGET_DIR}"

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
echo "正在恢复文件..."
rsync -av --delete "\${SOURCE_DIR}/" "\${TARGET_DIR}/"

echo "恢复完成!"
echo "如需回滚，请使用: \${CURRENT_BACKUP}"
EOF

# 设置恢复脚本为可执行
chmod +x "${RESTORE_SCRIPT}"

# 创建文件清单
echo "正在创建文件清单..."
find "${BACKUP_DIR}" -type f | sort > "${BACKUP_DIR}/file_list.txt"

# 计算文件总数和大小
FILE_COUNT=$(find "${BACKUP_DIR}" -type f | wc -l)
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)

echo "===========================================" 
echo "              备份完成!                 "
echo "===========================================" 
echo "备份日期时间: ${DATE_STAMP} ${TIME_STAMP} (${DAY_OF_WEEK})"
echo "备份包含 ${FILE_COUNT} 个文件"
echo "备份总大小: ${BACKUP_SIZE}"
echo "备份路径: ${BACKUP_DIR}"
echo "备份日志: ${BACKUP_LOG}"
echo "要恢复此备份，请运行: ${RESTORE_SCRIPT}"

# 添加MD5校验和文件
echo "正在计算关键文件MD5校验和..."

# 检查目录是否存在
if [ -d "${BACKUP_DIR}/templates" ]; then
    find "${BACKUP_DIR}/templates" -name "*.html" -exec md5 {} \; > "${BACKUP_DIR}/md5_checksums.txt"
else
    echo "templates目录不存在，跳过HTML文件的MD5计算" > "${BACKUP_DIR}/md5_checksums.txt"
fi

if [ -d "${BACKUP_DIR}/static" ]; then
    find "${BACKUP_DIR}/static" -name "*.css" -exec md5 {} \; >> "${BACKUP_DIR}/md5_checksums.txt"
else
    echo "static目录不存在，跳过CSS文件的MD5计算" >> "${BACKUP_DIR}/md5_checksums.txt"
fi

echo "备份时间: $(date)"
echo "完整备份已存储在: ${BACKUP_DIR}"
