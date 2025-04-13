#!/usr/bin/env python3
import os
import sqlite3
import time
from pathlib import Path

# 设置路径
DB_PATH = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/xlct12.db"
FILES_DIR = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 确保目录存在
if not os.path.exists(DB_PATH):
    print(f"错误: 数据库 {DB_PATH} 不存在")
    exit(1)
if not os.path.exists(FILES_DIR):
    print(f"错误: 目录 {FILES_DIR} 不存在")
    exit(1)

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"开始分析数据库和文件系统的一致性...")

# 获取所有papers表记录
cursor.execute("SELECT id, name, file_path, subject FROM papers")
db_records = cursor.fetchall()

print(f"数据库中找到 {len(db_records)} 条记录")

# 获取81目录中的所有文件
files_81 = set()
for root, dirs, files in os.walk(FILES_DIR):
    for file in files:
        if file.startswith('.'):
            continue
        file_path = os.path.join(root, file)
        files_81.add(file_path)

print(f"81目录中找到 {len(files_81)} 个文件")

# 分析数据库记录
records_with_valid_path = 0
records_with_invalid_path = 0
records_with_47_path = 0
records_with_81_path = 0
records_with_other_path = 0
invalid_records = []

# 更新文件路径模式以统一比较
path_81_prefix = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

for rec_id, name, file_path, subject in db_records:
    # 检查路径是否包含zujuanwang47
    if 'zujuanwang47' in file_path:
        records_with_47_path += 1
        
        # 尝试创建一个可能的81路径版本
        if '/papers/papers/' in file_path:
            file_name = os.path.basename(file_path)
            possible_81_path = os.path.join(path_81_prefix, file_name)
            
            # 检查这个文件是否在81目录中存在
            if os.path.exists(possible_81_path):
                records_with_valid_path += 1
            else:
                records_with_invalid_path += 1
                invalid_records.append((rec_id, name, file_path, subject, "zujuanwang47路径，文件在81中不存在"))
        else:
            records_with_invalid_path += 1
            invalid_records.append((rec_id, name, file_path, subject, "zujuanwang47路径，格式不符合期望"))
    
    # 检查路径是否包含zujuanwang81
    elif 'zujuanwang81' in file_path:
        records_with_81_path += 1
        
        # 检查文件是否实际存在
        if os.path.exists(file_path):
            records_with_valid_path += 1
        else:
            records_with_invalid_path += 1
            invalid_records.append((rec_id, name, file_path, subject, "zujuanwang81路径，但文件不存在"))
    
    # 其他路径
    else:
        records_with_other_path += 1
        
        # 尝试检查文件名是否在81目录中存在
        file_name = os.path.basename(file_path)
        possible_81_path = os.path.join(path_81_prefix, file_name)
        
        if os.path.exists(possible_81_path):
            records_with_valid_path += 1
        else:
            records_with_invalid_path += 1
            invalid_records.append((rec_id, name, file_path, subject, "非标准路径，文件在81中不存在"))

# 查找81目录中存在但数据库中没有记录的文件
db_file_paths = set()
for _, _, file_path, _ in db_records:
    # 标准化路径，只保留文件名
    file_name = os.path.basename(file_path)
    db_file_paths.add(file_name)

files_without_db_record = set()
for file_path in files_81:
    file_name = os.path.basename(file_path)
    if file_name not in db_file_paths:
        files_without_db_record.add(file_path)

# 输出分析结果
print("\n== 数据库记录分析 ==")
print(f"总记录数: {len(db_records)}")
print(f"有效路径记录数: {records_with_valid_path} ({records_with_valid_path/len(db_records)*100:.1f}%)")
print(f"无效路径记录数: {records_with_invalid_path} ({records_with_invalid_path/len(db_records)*100:.1f}%)")
print(f"zujuanwang47路径记录数: {records_with_47_path} ({records_with_47_path/len(db_records)*100:.1f}%)")
print(f"zujuanwang81路径记录数: {records_with_81_path} ({records_with_81_path/len(db_records)*100:.1f}%)")
print(f"其他路径记录数: {records_with_other_path} ({records_with_other_path/len(db_records)*100:.1f}%)")

print(f"\n在81目录中找到但数据库中无记录的文件数: {len(files_without_db_record)} ({len(files_without_db_record)/len(files_81)*100:.1f}%)")

# 创建报告文件
output_file = f"db_files_consistency_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_file, "w") as f:
    f.write(f"数据库和文件系统一致性报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("== 数据库记录分析 ==\n")
    f.write(f"总记录数: {len(db_records)}\n")
    f.write(f"有效路径记录数: {records_with_valid_path} ({records_with_valid_path/len(db_records)*100:.1f}%)\n")
    f.write(f"无效路径记录数: {records_with_invalid_path} ({records_with_invalid_path/len(db_records)*100:.1f}%)\n")
    f.write(f"zujuanwang47路径记录数: {records_with_47_path} ({records_with_47_path/len(db_records)*100:.1f}%)\n")
    f.write(f"zujuanwang81路径记录数: {records_with_81_path} ({records_with_81_path/len(db_records)*100:.1f}%)\n")
    f.write(f"其他路径记录数: {records_with_other_path} ({records_with_other_path/len(db_records)*100:.1f}%)\n\n")
    
    f.write(f"在81目录中找到但数据库中无记录的文件数: {len(files_without_db_record)} ({len(files_without_db_record)/len(files_81)*100:.1f}%)\n\n")
    
    # 按科目统计无效路径记录
    subjects_count = {}
    for _, _, _, subject, _ in invalid_records:
        if subject not in subjects_count:
            subjects_count[subject] = 0
        subjects_count[subject] += 1
    
    f.write("== 按科目统计无效路径记录 ==\n")
    for subject, count in sorted(subjects_count.items(), key=lambda x: x[1], reverse=True):
        f.write(f"{subject}: {count} 条记录\n")
    
    f.write("\n== 无效路径记录详情(前100条) ==\n\n")
    for idx, (rec_id, name, file_path, subject, reason) in enumerate(invalid_records[:100], 1):
        f.write(f"{idx}. ID: {rec_id}, 科目: {subject}\n")
        f.write(f"   名称: {name}\n")
        f.write(f"   路径: {file_path}\n")
        f.write(f"   原因: {reason}\n")
        f.write("-" * 80 + "\n")
    
    if len(invalid_records) > 100:
        f.write(f"\n... 以及其他 {len(invalid_records) - 100} 条记录\n\n")
    
    f.write("\n== 无数据库记录的文件详情(前50条) ==\n\n")
    for idx, file_path in enumerate(sorted(list(files_without_db_record))[:50], 1):
        f.write(f"{idx}. {file_path}\n")
    
    if len(files_without_db_record) > 50:
        f.write(f"\n... 以及其他 {len(files_without_db_record) - 50} 个文件\n")

# 关闭数据库连接
conn.close()

print(f"\n详细报告已保存到: {output_file}")
