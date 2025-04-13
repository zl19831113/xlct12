#!/usr/bin/env python3
import os
import sqlite3
import time
import re
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

print(f"开始分析下划线和命名模式不一致问题...")

# 获取所有papers表记录
cursor.execute("SELECT id, name, file_path, subject FROM papers WHERE file_path NOT LIKE '%zujuanwang81%'")
db_records = cursor.fetchall()

print(f"数据库中找到 {len(db_records)} 条需要检查的记录")

# 获取81目录中的所有文件
files_81 = {}
for root, dirs, files in os.walk(FILES_DIR):
    for file in files:
        if file.startswith('.'):
            continue
        file_path = os.path.join(root, file)
        files_81[file] = file_path

print(f"81目录中找到 {len(files_81)} 个文件")

# 分析和解决命名问题
total_records = len(db_records)
matched_records = 0
matched_with_transform = 0
still_unmatched = 0
matches = []
potential_matches = []
unmatched = []

# 定义可能的转换函数
def try_transformations(filename):
    transformations = []
    
    # 1. 移除所有下划线
    no_underscores = filename.replace('_', '')
    transformations.append(('移除下划线', no_underscores))
    
    # 2. 尝试不同位置的下划线
    parts = filename.split('_')
    for i in range(1, len(parts)):
        transformed = '_'.join(parts[:i]) + ''.join(parts[i:])
        transformations.append((f'在第{i}个下划线后合并', transformed))
    
    # 3. 尝试替换或移除特殊字符
    special_chars_removed = re.sub(r'[^\w\.]', '', filename)
    transformations.append(('移除特殊字符', special_chars_removed))
    
    # 4. 尝试处理中文名称转换的问题
    no_spaces = filename.replace(' ', '')
    transformations.append(('移除空格', no_spaces))
    
    return transformations

print(f"开始寻找匹配...")

# 主分析循环
for rec_id, name, file_path, subject in db_records:
    # 获取数据库记录中的文件名
    db_filename = os.path.basename(file_path)
    
    # 检查是否直接匹配
    if db_filename in files_81:
        matched_records += 1
        matches.append((rec_id, name, file_path, files_81[db_filename], "直接匹配"))
        continue
    
    # 尝试各种转换
    found_match = False
    for actual_filename, actual_path in files_81.items():
        # 检查两个文件名是否相似（忽略下划线）
        if db_filename.replace('_', '') == actual_filename.replace('_', ''):
            matched_with_transform += 1
            matches.append((rec_id, name, file_path, actual_path, "忽略下划线匹配"))
            found_match = True
            break
        
        # 比较文件名中的数字部分
        db_numbers = re.findall(r'\d+', db_filename)
        actual_numbers = re.findall(r'\d+', actual_filename)
        if db_numbers and actual_numbers and db_numbers == actual_numbers:
            # 如果数字序列相同，这可能是一个匹配
            potential_matches.append((rec_id, name, file_path, actual_path, "数字序列匹配"))
            found_match = True
            break
    
    if not found_match:
        # 尝试更复杂的转换
        transformations = try_transformations(db_filename)
        for transform_desc, transformed_name in transformations:
            for actual_filename, actual_path in files_81.items():
                if transformed_name == actual_filename or transformed_name == actual_filename.replace('_', ''):
                    matched_with_transform += 1
                    matches.append((rec_id, name, file_path, actual_path, f"通过{transform_desc}匹配"))
                    found_match = True
                    break
            if found_match:
                break
    
    if not found_match:
        still_unmatched += 1
        unmatched.append((rec_id, name, file_path, subject))

print(f"\n分析完成!")
print(f"总记录数: {total_records}")
print(f"直接匹配: {matched_records} ({matched_records/total_records*100:.1f}%)")
print(f"通过转换匹配: {matched_with_transform} ({matched_with_transform/total_records*100:.1f}%)")
print(f"总匹配率: {(matched_records+matched_with_transform)/total_records*100:.1f}%")
print(f"仍未匹配: {still_unmatched} ({still_unmatched/total_records*100:.1f}%)")

# 创建SQL更新脚本
sql_file = f"update_paths_{time.strftime('%Y%m%d_%H%M%S')}.sql"
with open(sql_file, "w") as f:
    f.write("-- 数据库路径更新SQL脚本\n")
    f.write(f"-- 创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("-- 执行此脚本前请务必备份数据库!\n\n")
    
    f.write("BEGIN TRANSACTION;\n\n")
    
    for rec_id, _, old_path, new_path, match_type in matches:
        f.write(f"-- {match_type}\n")
        f.write(f"UPDATE papers SET file_path = '{new_path}' WHERE id = {rec_id};\n\n")
    
    f.write("COMMIT;\n")

# 创建完整报告
report_file = f"path_mismatch_report_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(report_file, "w") as f:
    f.write(f"文件名不一致分析报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("== 总体分析 ==\n")
    f.write(f"总记录数: {total_records}\n")
    f.write(f"直接匹配: {matched_records} ({matched_records/total_records*100:.1f}%)\n")
    f.write(f"通过转换匹配: {matched_with_transform} ({matched_with_transform/total_records*100:.1f}%)\n")
    f.write(f"总匹配率: {(matched_records+matched_with_transform)/total_records*100:.1f}%\n")
    f.write(f"仍未匹配: {still_unmatched} ({still_unmatched/total_records*100:.1f}%)\n\n")
    
    f.write(f"已生成SQL更新脚本: {sql_file}\n\n")
    
    # 记录不同类型的匹配模式
    match_types = {}
    for _, _, _, _, match_type in matches:
        if match_type not in match_types:
            match_types[match_type] = 0
        match_types[match_type] += 1
    
    f.write("== 匹配模式统计 ==\n")
    for match_type, count in sorted(match_types.items(), key=lambda x: x[1], reverse=True):
        f.write(f"{match_type}: {count} 条记录\n")
    
    f.write("\n== 匹配示例(前50条) ==\n\n")
    for idx, (rec_id, name, old_path, new_path, match_type) in enumerate(matches[:50], 1):
        f.write(f"{idx}. ID: {rec_id}, 名称: {name}\n")
        f.write(f"   匹配方式: {match_type}\n")
        f.write(f"   原路径: {old_path}\n")
        f.write(f"   新路径: {new_path}\n")
        f.write(f"   原文件名: {os.path.basename(old_path)}\n")
        f.write(f"   新文件名: {os.path.basename(new_path)}\n")
        f.write("-" * 80 + "\n")
    
    f.write("\n== 未匹配记录示例(前50条) ==\n\n")
    for idx, (rec_id, name, file_path, subject) in enumerate(unmatched[:50], 1):
        f.write(f"{idx}. ID: {rec_id}, 科目: {subject}\n")
        f.write(f"   名称: {name}\n")
        f.write(f"   路径: {file_path}\n")
        f.write(f"   文件名: {os.path.basename(file_path)}\n")
        f.write("-" * 80 + "\n")

# 关闭数据库连接
conn.close()

print(f"\n详细报告已保存到: {report_file}")
print(f"SQL更新脚本已保存到: {sql_file}")
print("\n执行SQL脚本前，务必备份数据库！")
