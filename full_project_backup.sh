#!/bin/bash

# 全面项目备份脚本
# 创建于: 2025-04-01

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
BACKUP_ROOT="/Volumes/小鹿出题"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${BACKUP_ROOT}/zujuanwang76_complete_backup_${TIMESTAMP}"
BACKUP_TAR="${BACKUP_ROOT}/zujuanwang76_backup_${TIMESTAMP}.tar.gz"

# 要排除的文件/目录
EXCLUDE_PATTERNS=(
    "*.git*"
    "*__pycache__*"
    "*.pyc"
    ".venv"
    "venv"
    "*.tar.gz"
    "uploads_backup_*"
    "system_backup_*"
    "*.DS_Store"
)

# 构建排除选项
EXCLUDE_OPTIONS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      创建完整项目备份        ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "项目目录: ${PROJECT_DIR}"
echo -e "备份目录: ${BACKUP_DIR}"
echo -e "备份文件: ${BACKUP_TAR}"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 创建备份目录
echo -e "${YELLOW}创建备份目录...${NC}"
mkdir -p "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}/code"
mkdir -p "${BACKUP_DIR}/database"
mkdir -p "${BACKUP_DIR}/scripts"
mkdir -p "${BACKUP_DIR}/docs"

# 复制核心代码文件
echo -e "${YELLOW}复制核心代码文件...${NC}"
cp "${PROJECT_DIR}/app.py" "${BACKUP_DIR}/code/"

# 复制数据库文件
echo -e "${YELLOW}复制数据库文件...${NC}"
mkdir -p "${BACKUP_DIR}/database/instance"
cp "${PROJECT_DIR}/instance/xlct12.db" "${BACKUP_DIR}/database/instance/" 2>/dev/null
cp "${PROJECT_DIR}/xlct12.db" "${BACKUP_DIR}/database/" 2>/dev/null

# 复制关键脚本
echo -e "${YELLOW}复制关键修复脚本...${NC}"
cp "${PROJECT_DIR}/fix_file_association.py" "${BACKUP_DIR}/scripts/" 2>/dev/null
cp "${PROJECT_DIR}/rename_files_to_match_db.py" "${BACKUP_DIR}/scripts/" 2>/dev/null
cp "${PROJECT_DIR}/repair_downloads.py" "${BACKUP_DIR}/scripts/" 2>/dev/null

# 创建说明文档
echo -e "${YELLOW}创建备份说明文档...${NC}"
cat > "${BACKUP_DIR}/docs/README.md" << EOF
# 完整项目备份

备份日期: $(date +"%Y-%m-%d %H:%M:%S")

## 备份内容

1. 核心代码: app.py - 包含所有应用程序逻辑和下载功能
2. 数据库: xlct12.db - 包含所有试卷记录和文件路径
3. 修复脚本:
   - fix_file_association.py - 用于修复数据库记录与文件系统的关联
   - rename_files_to_match_db.py - 用于重命名文件以匹配数据库记录
   - repair_downloads.py - 用于修复下载功能

## 项目状态

- 已解决数据库与文件系统的关联问题
- 修复了下载功能，可以正确处理下划线与短横线的文件名差异
- 数据库记录已更新，指向正确的文件路径
- 应用程序配置已统一使用xlct12.db

## 完整备份归档

除此文件夹外，还创建了完整的项目归档：
\`${BACKUP_TAR}\`

该归档包含整个项目（排除了临时文件、虚拟环境和其他备份）。
EOF

# 创建完整项目归档
echo -e "${YELLOW}创建完整项目归档...${NC}"
cd "${PROJECT_DIR}/.."
tar -czf "${BACKUP_TAR}" ${EXCLUDE_OPTIONS} "zujuanwang76"

if [ $? -ne 0 ]; then
    echo -e "${RED}创建归档失败。${NC}"
    exit 1
fi

# 将归档信息添加到备份目录
echo -e "${YELLOW}复制完整归档信息...${NC}"
echo "完整归档位置: ${BACKUP_TAR}" > "${BACKUP_DIR}/docs/archive_info.txt"
echo "归档大小: $(du -h ${BACKUP_TAR} | cut -f1)" >> "${BACKUP_DIR}/docs/archive_info.txt"
echo "排除项: ${EXCLUDE_PATTERNS[*]}" >> "${BACKUP_DIR}/docs/archive_info.txt"

# 计算备份大小
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
ARCHIVE_SIZE=$(du -sh "${BACKUP_TAR}" | cut -f1)

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}            备份完成!                 ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "备份目录: ${BACKUP_DIR}"
echo -e "备份大小: ${BACKUP_SIZE}"
echo -e "完整归档: ${BACKUP_TAR}"
echo -e "归档大小: ${ARCHIVE_SIZE}"
echo -e ""
echo -e "备份包含整个项目的核心文件和完整归档。"
echo -e "如需恢复，可以使用完整归档 ${BACKUP_TAR}"
