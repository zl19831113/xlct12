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
