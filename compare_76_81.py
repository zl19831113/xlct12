#!/usr/bin/env python3
import os
import time
import hashlib
from pathlib import Path

# 设置路径
DIR_76 = "/Volumes/小鹿出题/小鹿备份/4月1日76/uploads/papers/papers"
DIR_81 = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 检查目录是否存在
if not os.path.exists(DIR_76):
    print(f"错误: 目录 {DIR_76} 不存在")
    exit(1)
if not os.path.exists(DIR_81):
    print(f"错误: 目录 {DIR_81} 不存在")
    exit(1)

print(f"开始比较目录...")
print(f"76版本: {DIR_76}")
print(f"81版本: {DIR_81}")

# 获取76目录中的所有文件
files_76 = []
for root, dirs, files in os.walk(DIR_76):
    for file in files:
        if file.startswith('.'):
            continue
        file_path = os.path.join(root, file)
        rel_path = os.path.relpath(file_path, DIR_76)
        file_size = os.path.getsize(file_path)
        files_76.append({
            'name': file,
            'path': file_path,
            'rel_path': rel_path,
            'size': file_size
        })

print(f"76版本中找到 {len(files_76)} 个文件")

# 统计计数器
found_count = 0
missing_count = 0
missing_files = []

# 进度指示器
total_files = len(files_76)
milestone = max(1, total_files // 10)
print(f"开始查找文件是否存在于81版本...")

# 检查每个文件是否在81目录中存在
for idx, file_info in enumerate(files_76, 1):
    if idx % milestone == 0:
        print(f"已处理 {idx}/{total_files} 个文件 ({idx/total_files*100:.1f}%)...")
    
    # 直接检查相同文件名是否存在
    file_path_81 = os.path.join(DIR_81, file_info['name'])
    if os.path.exists(file_path_81):
        found_count += 1
    else:
        # 如果按名称找不到，尝试在整个81目录中搜索
        found = False
        for root, dirs, files in os.walk(DIR_81):
            if file_info['name'] in files:
                found = True
                found_count += 1
                break
        
        if not found:
            missing_count += 1
            missing_files.append(file_info)

print(f"\n比较完成!")
print(f"76版本中的文件总数: {total_files}")
print(f"在81版本中找到: {found_count} ({found_count/total_files*100:.1f}%)")
print(f"在81版本中缺失: {missing_count} ({missing_count/total_files*100:.1f}%)")

# 创建报告文件
output_file = f"comparison_76_81_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_file, "w") as f:
    f.write(f"76版本与81版本文件比较报告 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"76版本目录: {DIR_76}\n")
    f.write(f"81版本目录: {DIR_81}\n\n")
    f.write(f"76版本中的文件总数: {total_files}\n")
    f.write(f"在81版本中找到: {found_count} ({found_count/total_files*100:.1f}%)\n")
    f.write(f"在81版本中缺失: {missing_count} ({missing_count/total_files*100:.1f}%)\n\n")
    
    # 按大小排序缺失的文件
    missing_files.sort(key=lambda x: x['size'], reverse=True)
    
    f.write("== 在81版本中缺失的文件 ==\n\n")
    for idx, file_info in enumerate(missing_files, 1):
        f.write(f"{idx}. {file_info['name']}\n")
        f.write(f"   大小: {file_info['size'] / 1024 / 1024:.2f} MB\n")
        f.write(f"   76版本中的路径: {file_info['path']}\n")
        f.write("-" * 80 + "\n")
    
    # 统计缺失文件的扩展名
    extensions = {}
    for file_info in missing_files:
        _, ext = os.path.splitext(file_info['name'])
        ext = ext.lower()
        if ext not in extensions:
            extensions[ext] = 0
        extensions[ext] += 1
    
    f.write("\n== 缺失文件的扩展名统计 ==\n\n")
    for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
        f.write(f"{ext}: {count} 个文件\n")

print(f"详细报告已保存到: {output_file}")
