#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re

# 数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'xlct12.db')

# 连接到数据库
print(f"正在连接数据库: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询所有试卷记录
print("查询数据库中的文件路径...")
cursor.execute("SELECT id, name, file_path FROM papers")
records = cursor.fetchall()

print(f"共找到 {len(records)} 条记录\n")

# 统计和分析
with_underscore = 0
without_underscore = 0
unusual_patterns = 0
unique_patterns = set()

# 按ID区间创建样本
samples_with_underscore = []
samples_without_underscore = []

print("正在分析文件名格式...")
for record in records:
    id, name, file_path = record
    
    # 提取文件名
    filename = os.path.basename(file_path)
    
    # 检查文件名是否包含下划线
    if '_' in filename:
        with_underscore += 1
        if len(samples_with_underscore) < 5:
            samples_with_underscore.append((id, filename))
    else:
        without_underscore += 1
        if len(samples_without_underscore) < 5:
            samples_without_underscore.append((id, filename))
    
    # 尝试识别文件名格式模式
    # 例如检测是否符合日期格式，或其他常见模式
    date_pattern = re.search(r'(\d{8}|\d{4}\d{2}\d{2}|\d{4}_\d{2}_\d{2})', filename)
    if date_pattern:
        pattern = "DATE" + ("_WITH_UNDERSCORE" if '_' in date_pattern.group() else "_WITHOUT_UNDERSCORE")
        unique_patterns.add(pattern)
    elif re.search(r'^\d+$', filename.split('.')[0]):
        unique_patterns.add("PURE_NUMBER")
    else:
        unusual_patterns += 1

# 输出统计信息
print(f"\n文件名统计:")
print(f"包含下划线的文件名: {with_underscore} ({with_underscore/len(records)*100:.2f}%)")
print(f"不包含下划线的文件名: {without_underscore} ({without_underscore/len(records)*100:.2f}%)")
print(f"检测到的不常见模式: {unusual_patterns}")
print(f"识别出的文件名模式类型: {len(unique_patterns)}")

# 输出包含下划线的文件名示例
print("\n包含下划线的文件名示例:")
for id, filename in samples_with_underscore:
    print(f"ID {id}: {filename}")

# 输出不包含下划线的文件名示例
print("\n不包含下划线的文件名示例:")
for id, filename in samples_without_underscore:
    print(f"ID {id}: {filename}")

conn.close()
print("\n分析完成。")
