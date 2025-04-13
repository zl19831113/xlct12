#!/usr/bin/env python3
import json
import re
import os
import sqlite3
from collections import defaultdict

# 加载检查结果
with open('paper_consistency_check_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

missing_files = results['missing_files']
print(f"分析 {len(missing_files)} 个缺失文件...")

# 分析文件路径模式
path_patterns = defaultdict(int)
for paper_id, name, subject, file_path in missing_files:
    # 提取路径模式（文件夹结构和命名前缀）
    match = re.match(r'uploads/(.+?)_\d+_', file_path)
    if match:
        pattern = f"uploads/{match.group(1)}_*"
        path_patterns[pattern] += 1
    else:
        path_patterns[file_path] += 1

print("\n文件路径模式统计:")
for pattern, count in sorted(path_patterns.items(), key=lambda x: x[1], reverse=True):
    print(f"{pattern}: {count}个")

# 分析日期模式
date_patterns = defaultdict(int)
for paper_id, name, subject, file_path in missing_files:
    # 提取日期模式（如20250331）
    match = re.search(r'(\d{8})', file_path)
    if match:
        date_pattern = match.group(1)
        date_patterns[date_pattern] += 1

print("\n日期模式统计:")
for pattern, count in sorted(date_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{pattern}: {count}个")

# 分析ID范围
id_ranges = []
last_id = None
range_start = None
for paper_id, name, subject, file_path in sorted(missing_files, key=lambda x: x[0]):
    if range_start is None:
        range_start = paper_id
    elif paper_id > last_id + 1:
        id_ranges.append((range_start, last_id))
        range_start = paper_id
    last_id = paper_id

if range_start is not None and last_id is not None:
    id_ranges.append((range_start, last_id))

print("\nID范围分析:")
for start, end in id_ranges[:5]:
    print(f"ID范围: {start}-{end} (共 {end-start+1} 个)")
if len(id_ranges) > 5:
    print(f"...共 {len(id_ranges)} 个ID范围")

# 连接数据库检查实际文件存在性
print("\n检查文件系统中的实际文件...")
found_files = 0
total_files = len(missing_files)

# 随机选取几个文件进行检查
import random
sample_size = min(10, total_files)
sample_missing_files = random.sample(missing_files, sample_size)

print(f"\n随机抽样 {sample_size} 个缺失文件进行检查:")
for paper_id, name, subject, file_path in sample_missing_files:
    # 检查文件是否存在于uploads/papers目录下的其他位置
    base_filename = os.path.basename(file_path)
    possible_files = []
    
    # 构建可能的文件名模式
    id_part = re.search(r'_(\d+)_', base_filename)
    if id_part:
        id_num = id_part.group(1)
        for root, dirs, files in os.walk('uploads/papers'):
            for file in files:
                if id_num in file:
                    possible_files.append(os.path.join(root, file))
    
    if possible_files:
        print(f"ID {paper_id} 的文件可能存在于: {', '.join(possible_files[:3])}" + 
              (f" 等 {len(possible_files)} 个位置" if len(possible_files) > 3 else ""))
    else:
        print(f"ID {paper_id} 的文件 {file_path} 在系统中未找到任何可能的匹配")

# 生成解决方案建议
print("\n解决方案建议:")
print("""
1. 数据库清理:
   - 可以从数据库中删除所有缺失文件的记录，特别是那些时间戳为20250331125700的记录。
   - SQL: DELETE FROM papers WHERE file_path LIKE 'uploads/papers/20250331125700%';

2. 文件重新上传:
   - 如果这些文件是必需的，需要重新上传缺失的文件。
   - 可以按照科目优先级(如语文、数学、英语等核心科目)分批进行上传。

3. 路径修正:
   - 如果文件实际存在但路径记录不正确，可以编写脚本扫描现有文件并尝试匹配数据库记录，更新正确的路径。
   - 可以基于试卷名称、ID或其他元数据进行匹配。

4. 用户界面优化:
   - 在前端显示试卷时，可以添加文件存在性检查，对于缺失文件的条目添加特殊标记或隐藏。
   - 这样可以避免用户尝试下载不存在的文件。
""")

# 创建修复SQL脚本
with open('fix_missing_files.sql', 'w', encoding='utf-8') as sql_file:
    sql_file.write("-- 试卷缺失文件修复SQL脚本\n")
    sql_file.write("-- 生成时间: " + os.popen('date').read().strip() + "\n")
    sql_file.write("-- 总共需要处理的记录数: " + str(len(missing_files)) + "\n\n")
    
    sql_file.write("-- 选项1: 删除所有缺失文件的记录\n")
    sql_file.write("-- BEGIN TRANSACTION;\n\n")
    
    # 按照日期模式分组删除
    for date_pattern, count in sorted(date_patterns.items(), key=lambda x: x[1], reverse=True):
        sql_file.write(f"-- 删除日期模式为 {date_pattern} 的 {count} 条记录\n")
        sql_file.write(f"-- DELETE FROM papers WHERE file_path LIKE 'uploads/papers/{date_pattern}%';\n\n")
    
    sql_file.write("-- 逐条删除特定ID\n")
    sql_file.write("-- DELETE FROM papers WHERE id IN (\n")
    id_list = [str(paper_id) for paper_id, _, _, _ in missing_files]
    # 每行20个ID
    for i in range(0, len(id_list), 20):
        sql_file.write("--    " + ", ".join(id_list[i:i+20]) + ",\n")
    sql_file.write("-- );\n\n")
    
    sql_file.write("-- COMMIT;\n\n")
    
    sql_file.write("-- 选项2: 标记这些记录为缺失状态(如果papers表有status字段)\n")
    sql_file.write("-- BEGIN TRANSACTION;\n")
    sql_file.write("-- 添加status字段(如果不存在)\n")
    sql_file.write("-- ALTER TABLE papers ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';\n\n")
    sql_file.write("-- UPDATE papers SET status = 'missing_file' WHERE id IN (前面的ID列表);\n")
    sql_file.write("-- COMMIT;\n")

print("\n修复SQL脚本已生成: fix_missing_files.sql") 