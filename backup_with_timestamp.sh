#!/bin/bash

# 增强版备份脚本 - 带时间戳和回滚功能
# 创建于: 2025-03-28
# 版本: 1.0

# 设置详细备份时间戳
DATE_STAMP=$(date +"%Y-%m-%d")
TIME_STAMP=$(date +"%H-%M-%S")
FULL_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_VERSION="v${FULL_TIMESTAMP}"

# 设置备份目录结构
BACKUP_ROOT="/Users/sl19831113/Desktop/备份"
BACKUP_NAME="zujuanwang75_backup_${BACKUP_VERSION}"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"
SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75"
RESTORE_SCRIPT="${BACKUP_DIR}/restore.sh"
BACKUP_LOG="${BACKUP_DIR}/backup_log.txt"
VERSION_FILE="${BACKUP_ROOT}/version_history.txt"
LATEST_SYMLINK="${BACKUP_ROOT}/latest_backup"

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

# 创建备份目录结构
mkdir -p "${BACKUP_ROOT}/rollbacks"
mkdir -p "${BACKUP_DIR}"

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "错误: 无法创建备份目录 ${BACKUP_DIR}"
    exit 1
fi

# 显示开始备份信息
echo "=================================================="
echo "开始创建时间戳备份 | ${BACKUP_VERSION}"
echo "--------------------------------------------------"
echo "备份时间: $(date)"
echo "备份源目录: ${SOURCE_DIR}"
echo "备份目标目录: ${BACKUP_DIR}"
echo "--------------------------------------------------"

# 创建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

# 记录备份版本历史
echo "${BACKUP_VERSION},$(date),${BACKUP_NAME}" >> "${VERSION_FILE}"

# 创建到最新备份的符号链接
if [ -L "${LATEST_SYMLINK}" ]; then
    rm "${LATEST_SYMLINK}"
fi
ln -sf "${BACKUP_DIR}" "${LATEST_SYMLINK}"

# 创建实现恢复功能的脚本
cat << EOF > "${RESTORE_SCRIPT}"
#!/bin/bash

# 自动生成的恢复脚本 (备份版本: ${BACKUP_VERSION})
# 生成时间: $(date)
# 源目录: ${SOURCE_DIR}

SOURCE_DIR="\$(dirname "\$(readlink -f "\$0")")"
TARGET_DIR="${SOURCE_DIR}"
BACKUP_VERSION="${BACKUP_VERSION}"
RESTORE_LOG="\${SOURCE_DIR}/restore_\$(date +"%Y%m%d_%H%M%S").log"

echo "=================================================="
echo "开始恢复 | 版本: \${BACKUP_VERSION}"
echo "--------------------------------------------------"
echo "恢复时间: \$(date)"
echo "从: \${SOURCE_DIR}"
echo "到: \${TARGET_DIR}"
echo "日志文件: \${RESTORE_LOG}"
echo "--------------------------------------------------"

# 检查目标目录是否存在
if [ ! -d "\${TARGET_DIR}" ]; then
    echo "目标目录不存在，正在创建..."
    mkdir -p "\${TARGET_DIR}"
fi

# 创建先前备份
BEFORE_RESTORE="\${TARGET_DIR}_before_restore_\$(date +"%Y%m%d_%H%M%S")"
echo "创建恢复前的备份: \${BEFORE_RESTORE}"
rsync -a "\${TARGET_DIR}/" "\${BEFORE_RESTORE}/" >> "\${RESTORE_LOG}" 2>&1

# 使用rsync来重建原始目录
echo "正在恢复文件..."

rsync -av --delete "\${SOURCE_DIR}/" "\${TARGET_DIR}/" >> "\${RESTORE_LOG}" 2>&1

RETURN_CODE=\$?
if [ \$RETURN_CODE -eq 0 ]; then
    echo "✅ 恢复成功完成!"
    echo "目标目录: \${TARGET_DIR}"
    echo "如需回滚，请使用以下目录: \${BEFORE_RESTORE}"
    echo "  回滚命令: rsync -av --delete \"\${BEFORE_RESTORE}/\" \"\${TARGET_DIR}/\""
else
    echo "⚠️ 恢复过程中出现错误. 查看日志: \${RESTORE_LOG}"
    exit 1
fi
EOF

# 设置恢复脚本的可执行权限
chmod +x "${RESTORE_SCRIPT}"

# 运行rsync进行备份
echo "正在运行rsync进行备份..."
rsync -a ${EXCLUDE_OPTIONS} "${SOURCE_DIR}/" "${BACKUP_DIR}/" >> "${BACKUP_LOG}" 2>&1

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "✅ 备份成功完成!"
    echo "备份目录: ${BACKUP_DIR}"
    echo "版本: ${BACKUP_VERSION}"
    echo "
恢复指令:"
    echo "  1. 最新备份: ${RESTORE_SCRIPT}"
    echo "  2. 指定版本: 查看 ${VERSION_FILE} 获取版本列表"
    
    # 创建版本快捷方式
    ROLLBACK_SCRIPT="${BACKUP_ROOT}/rollbacks/rollback_to_${BACKUP_VERSION}.sh"
    ln -sf "${RESTORE_SCRIPT}" "${ROLLBACK_SCRIPT}"
    chmod +x "${ROLLBACK_SCRIPT}"
    echo "  3. 快捷恢复: ${ROLLBACK_SCRIPT}"
else
    echo "⚠️ 备份失败! 查看错误日志: ${BACKUP_LOG}"
    exit 1
fi

echo "=================================================="
echo "备份历史文件: ${VERSION_FILE}"
echo "最新备份链接: ${LATEST_SYMLINK}"
echo "恢复脚本目录: ${BACKUP_ROOT}/rollbacks/"
echo "=================================================="
