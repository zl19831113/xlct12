#!/bin/bash

# 恢复试卷文件的脚本
# 创建于: 2025-03-29

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 配置
PROJECT_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"
SOURCE_DIR="${PROJECT_DIR}/uploads"
TARGET_DIR1="${PROJECT_DIR}/uploads/papers"
TARGET_DIR2="${PROJECT_DIR}/uploads/papers/papers"
TARGET_DIR3="${PROJECT_DIR}/static/uploads/papers"
TARGET_DIR4="${PROJECT_DIR}/static/uploads/papers/papers"

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}       恢复试卷文件                               ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "项目目录: ${PROJECT_DIR}"
echo -e "源目录: ${SOURCE_DIR}"
echo -e "目标目录1: ${TARGET_DIR1}"
echo -e "目标目录2: ${TARGET_DIR2}"
echo -e "目标目录3: ${TARGET_DIR3}"
echo -e "目标目录4: ${TARGET_DIR4}"
echo -e "恢复时间: $(date)"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# 确保目标目录存在
echo -e "${BLUE}确保目标目录存在...${NC}"
mkdir -p "${TARGET_DIR1}"
mkdir -p "${TARGET_DIR2}"
mkdir -p "${TARGET_DIR3}"
mkdir -p "${TARGET_DIR4}"

# 统计源文件数量
FILE_COUNT=$(find "${SOURCE_DIR}" -maxdepth 1 -type f | wc -l)
echo -e "${BLUE}在uploads目录中找到了 ${FILE_COUNT} 个文件${NC}"

# 复制文件到所有可能的目标位置
echo -e "${BLUE}复制文件到所有目标位置...${NC}"

# 复制到目标1: uploads/papers/
echo -e "${BLUE}复制到 uploads/papers/ ...${NC}"
find "${SOURCE_DIR}" -maxdepth 1 -type f -exec cp {} "${TARGET_DIR1}/" \;

# 复制到目标2: uploads/papers/papers/
echo -e "${BLUE}复制到 uploads/papers/papers/ ...${NC}"
find "${SOURCE_DIR}" -maxdepth 1 -type f -exec cp {} "${TARGET_DIR2}/" \;

# 复制到目标3: static/uploads/papers/
echo -e "${BLUE}复制到 static/uploads/papers/ ...${NC}"
find "${SOURCE_DIR}" -maxdepth 1 -type f -exec cp {} "${TARGET_DIR3}/" \;

# 复制到目标4: static/uploads/papers/papers/
echo -e "${BLUE}复制到 static/uploads/papers/papers/ ...${NC}"
find "${SOURCE_DIR}" -maxdepth 1 -type f -exec cp {} "${TARGET_DIR4}/" \;

# 统计文件数量
DIR1_COUNT=$(find "${TARGET_DIR1}" -type f | wc -l)
DIR2_COUNT=$(find "${TARGET_DIR2}" -type f | wc -l)
DIR3_COUNT=$(find "${TARGET_DIR3}" -type f | wc -l)
DIR4_COUNT=$(find "${TARGET_DIR4}" -type f | wc -l)

echo -e "${GREEN}复制完成!${NC}"
echo -e "目标目录1文件数量: ${DIR1_COUNT}"
echo -e "目标目录2文件数量: ${DIR2_COUNT}"
echo -e "目标目录3文件数量: ${DIR3_COUNT}"
echo -e "目标目录4文件数量: ${DIR4_COUNT}"

# 现在更新数据库中的文件路径
echo -e "${YELLOW}修复数据库中的文件路径...${NC}"
echo -e "${BLUE}这需要通过运行Python脚本来完成...${NC}"

# 生成Python脚本来修复数据库
cat > "${PROJECT_DIR}/restore_papers_db.py" << 'EOF'
import os
import sqlite3
import re

# 获取项目根目录
project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, 'instance', 'questions.db')
print(f"数据库路径: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找uploads目录中所有文件
uploads_dir = os.path.join(project_dir, 'uploads')
upload_files = os.listdir(uploads_dir)
file_names = [f for f in upload_files if os.path.isfile(os.path.join(uploads_dir, f))]
print(f"在uploads目录中找到 {len(file_names)} 个文件")

# 检查数据库中的试卷记录
cursor.execute("SELECT id, name, file_path FROM papers")
papers = cursor.fetchall()
print(f"找到 {len(papers)} 条试卷记录")

# 更新文件路径
updated_count = 0
for paper_id, paper_name, file_path in papers:
    if file_path:
        # 从原始路径中提取文件名
        file_name = os.path.basename(file_path)
        
        # 尝试用文件名匹配uploads目录中的文件
        exact_match = None
        pattern_matches = []
        
        for upload_file in file_names:
            # 精确匹配
            if upload_file == file_name:
                exact_match = upload_file
                break
            
            # 模式匹配 - 尝试匹配文件名的一部分（不包括日期时间戳等）
            # 例如，如果数据库中有 "20250227_123456_高中数学试卷.docx"，
            # 但uploads里有 "高中数学试卷.docx" 或 "20250228_高中数学试卷.docx"
            base_name_parts = re.sub(r'^\d+_\d+_\d+_', '', file_name)  # 移除前缀日期/编号
            if base_name_parts in upload_file or base_name_parts.split('.')[0] in upload_file:
                pattern_matches.append(upload_file)
        
        # 确定最佳匹配
        best_match = exact_match or (pattern_matches[0] if pattern_matches else None)
        
        if best_match:
            # 构建新路径 - 使用多个可能的路径位置
            new_paths = [
                f"uploads/papers/{best_match}",         # 路径1
                f"uploads/papers/papers/{best_match}",  # 路径2
                f"static/uploads/papers/{best_match}",  # 路径3
                f"static/uploads/papers/papers/{best_match}"  # 路径4
            ]
            
            # 使用第一个路径更新数据库
            new_path = new_paths[0]
            
            # 更新数据库
            cursor.execute(
                "UPDATE papers SET file_path = ? WHERE id = ?", 
                (new_path, paper_id)
            )
            updated_count += 1
            
            match_type = "精确匹配" if exact_match else "模式匹配"
            print(f"✓ 更新试卷 #{paper_id}: {paper_name} - {match_type}")
            print(f"  原路径: {file_path}")
            print(f"  新路径: {new_path}")

# 提交更改
conn.commit()
print(f"更新了 {updated_count} 条记录")

# 关闭连接
conn.close()
EOF

# 运行Python脚本
echo -e "${BLUE}运行Python脚本修复数据库...${NC}"
cd "${PROJECT_DIR}" && python3 restore_papers_db.py

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       试卷文件恢复完成!                         ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "恢复时间: $(date)"
echo -e "${YELLOW}请重启应用并尝试下载试卷验证问题是否解决${NC}"
