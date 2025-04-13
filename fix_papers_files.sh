#!/bin/bash

# 修复试卷文件问题的脚本
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
PROJECT_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
BACKUP_DIR="${PROJECT_DIR}/backup_20250328230710/static/uploads"
TARGET_DIR="${PROJECT_DIR}/static/uploads/papers"

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       修复名校试卷下载的文件问题               ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "项目目录: ${PROJECT_DIR}"
echo -e "备份目录: ${BACKUP_DIR}"
echo -e "目标目录: ${TARGET_DIR}"
echo -e "修复时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 确保目标目录存在
echo -e "${BLUE}确保目标目录存在...${NC}"
mkdir -p "${TARGET_DIR}"
mkdir -p "${TARGET_DIR}/papers"  # 创建一个papers子目录用于存放试卷

# 复制PDF文件
echo -e "${BLUE}复制PDF文件...${NC}"
find "${BACKUP_DIR}" -name "*.pdf" -type f -exec cp {} "${TARGET_DIR}/papers/" \;

# 复制ZIP文件
echo -e "${BLUE}复制ZIP文件...${NC}"
find "${BACKUP_DIR}" -name "*.zip" -type f -exec cp {} "${TARGET_DIR}/papers/" \;

# 统计文件数量
PDF_COUNT=$(find "${TARGET_DIR}/papers" -name "*.pdf" -type f | wc -l)
ZIP_COUNT=$(find "${TARGET_DIR}/papers" -name "*.zip" -type f | wc -l)
TOTAL_COUNT=$((PDF_COUNT + ZIP_COUNT))

echo -e "${GREEN}复制完成!${NC}"
echo -e "PDF文件数量: ${PDF_COUNT}"
echo -e "ZIP文件数量: ${ZIP_COUNT}"
echo -e "总文件数量: ${TOTAL_COUNT}"

# 现在修复数据库中的文件路径
echo -e "${YELLOW}修复数据库中的文件路径...${NC}"
echo -e "${BLUE}这需要通过运行Python脚本来完成...${NC}"

# 生成Python脚本来修复数据库
cat > "${PROJECT_DIR}/fix_papers_db.py" << 'EOF'
import os
import sqlite3
from flask import Flask

# 获取项目根目录
project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, 'instance', 'questions.db')
print(f"数据库路径: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查数据库中的试卷记录
cursor.execute("SELECT id, name, file_path FROM papers")
papers = cursor.fetchall()
print(f"找到 {len(papers)} 条试卷记录")

# 新的文件路径前缀
new_papers_dir = "static/uploads/papers/papers"

# 更新文件路径
updated_count = 0
for paper_id, paper_name, file_path in papers:
    if file_path:
        # 从原始路径中提取文件名
        file_name = os.path.basename(file_path)
        # 构建新路径
        new_path = f"{new_papers_dir}/{file_name}"
        
        # 检查文件是否存在于新位置
        full_new_path = os.path.join(project_dir, new_papers_dir, file_name)
        exists = os.path.exists(full_new_path)
        
        # 即使文件不存在也更新路径，方便将来添加文件
        cursor.execute(
            "UPDATE papers SET file_path = ? WHERE id = ?", 
            (new_path, paper_id)
        )
        updated_count += 1
        
        status = "✓" if exists else "✗"
        print(f"{status} 更新试卷 #{paper_id}: {paper_name} - 路径: {new_path}")

# 提交更改
conn.commit()
print(f"更新了 {updated_count} 条记录")

# 关闭连接
conn.close()
EOF

# 运行Python脚本
echo -e "${BLUE}运行Python脚本修复数据库...${NC}"
cd "${PROJECT_DIR}" && python3 fix_papers_db.py

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       试卷文件修复完成!                         ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "注意: 如果修复数据库失败，您可能需要手动运行fix_papers_db.py"
echo -e "${YELLOW}请再次尝试下载试卷验证问题是否解决${NC}"
