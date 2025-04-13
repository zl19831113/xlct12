#!/usr/bin/env python3
import sqlite3
import os
import re

# 连接数据库
conn = sqlite3.connect('xlct12.db')
cursor = conn.cursor()

# 获取所有文件路径中包含 zujuanwang47 的记录
cursor.execute("SELECT id, name, file_path, subject FROM papers WHERE file_path LIKE '%zujuanwang47%'")
zujuanwang47_files = cursor.fetchall()

missing_files = []
found_files = []

for file_id, name, file_path, subject in zujuanwang47_files:
    # 提取原始文件名
    original_filename = os.path.basename(file_path)
    
    # 在 zujuanwang81 中的可能路径
    possible_path_81 = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads"
    
    # 检查文件是否存在于 zujuanwang81 目录
    found = False
    for root, dirs, files in os.walk(possible_path_81):
        if original_filename in files:
            found = True
            found_path = os.path.join(root, original_filename)
            found_files.append((file_id, name, file_path, found_path, subject))
            break
    
    if not found:
        missing_files.append((file_id, name, file_path, subject))

print(f"总共找到 {len(zujuanwang47_files)} 个在zujuanwang47的文件记录")
print(f"在zujuanwang81中找到: {len(found_files)} 个文件")
print(f"在zujuanwang81中缺失: {len(missing_files)} 个文件")

# 按科目统计缺失文件
subject_counts = {}
for _, _, _, subject in missing_files:
    subject_counts[subject] = subject_counts.get(subject, 0) + 1

print("\n== 按科目统计缺失文件 ==")
for subject, count in sorted(subject_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{subject}: {count}个文件")

# 只打印前20个缺失文件作为示例
print("\n== 缺失文件示例(前20个) ==")
for idx, (file_id, name, file_path, subject) in enumerate(missing_files[:20], 1):
    print(f"{idx}. ID: {file_id}, 科目: {subject}, 名称: {name}")
    print(f"   原路径: {file_path}")
    print("-" * 80)

# 关闭数据库连接
conn.close()
