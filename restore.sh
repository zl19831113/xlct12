#!/bin/bash

# 自动恢复脚本
# 创建于: Thu Mar 27 18:48:23 CST 2025

SOURCE_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75_backup_20250327_184707"
TARGET_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75"

echo "开始恢复备份..."
echo "备份源目录: ${SOURCE_DIR}"
echo "恢复目标目录: ${TARGET_DIR}"

# 确认恢复操作
read -p "确认要恢复备份吗? 这将覆盖目标目录中的文件 [y/N]: " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
    echo "恢复操作已取消"
    exit 0
fi

# 检查目标目录
if [ ! -d "${TARGET_DIR}" ]; then
    echo "目标目录不存在，正在创建..."
    mkdir -p "${TARGET_DIR}"
fi

# 备份当前状态以防万一
CURRENT_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CURRENT_BACKUP="${TARGET_DIR}_before_restore_${CURRENT_TIMESTAMP}"
echo "为安全起见，先备份目标目录到: ${CURRENT_BACKUP}"
cp -R "${TARGET_DIR}" "${CURRENT_BACKUP}"

# 复制备份文件到目标目录
echo "正在恢复文件..."
rsync -av --delete "${SOURCE_DIR}/" "${TARGET_DIR}/"

echo "恢复完成!"
echo "如需回滚，请使用: ${CURRENT_BACKUP}"
