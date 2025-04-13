#!/usr/bin/env python3
import os
import time
import re
import sqlite3
from pathlib import Path

# 设置路径
UPLOADS_DIR = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads"
PAPERS_DIR = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 连接数据库
try:
    conn = sqlite3.connect('xlct12.db')
    cursor = conn.cursor()
    has_db = True
except:
    print("警告: 无法连接到数据库, 将只执行文件比较")
    has_db = False

# 获取papers目录中的所有文件
papers_files = set()
if os.path.exists(PAPERS_DIR):
    for root, dirs, files in os.walk(PAPERS_DIR):
        for file in files:
            # 跳过隐藏文件
            if not file.startswith('.'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PAPERS_DIR)
                papers_files.add(rel_path)

print(f"uploads/papers 目录中找到 {len(papers_files)} 个文件")

# 搜索uploads目录中不在papers子目录的文件
potential_papers = []
paper_extensions = {'.pdf', '.doc', '.docx', '.zip', '.rar', '.7z', '.xls', '.xlsx', '.ppt', '.pptx'}

for root, dirs, files in os.walk(UPLOADS_DIR):
    # 跳过papers目录
    if root.startswith(PAPERS_DIR):
        continue
        
    for file in files:
        # 跳过隐藏文件
        if file.startswith('.'):
            continue
            
        # 检查文件扩展名
        _, ext = os.path.splitext(file)
        if ext.lower() in paper_extensions:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, UPLOADS_DIR)
            potential_papers.append({
                'filename': file,
                'path': full_path,
                'rel_path': rel_path,
                'size': os.path.getsize(full_path)
            })

# 按大小从大到小排序
potential_papers.sort(key=lambda x: x['size'], reverse=True)

print(f"\n在uploads目录(但不在papers子目录)找到 {len(potential_papers)} 个可能的试卷文件")

# 如果连接到了数据库，尝试匹配数据库记录
if has_db:
    # 获取缺失的论文记录
    cursor.execute("""
    SELECT id, name, file_path, subject FROM papers 
    WHERE file_path LIKE '%zujuanwang47%'
    """)
    missing_papers = cursor.fetchall()
    
    # 提取文件名
    missing_names = [(paper[0], paper[1], os.path.basename(paper[2])) for paper in missing_papers]
    
    print(f"\n找到 {len(missing_names)} 个在数据库中但缺失的论文记录")
    
    # 创建匹配映射
    matches = []
    
    # 通过文件名直接匹配
    for paper_id, paper_name, db_filename in missing_names:
        for potential in potential_papers:
            if potential['filename'] == db_filename:
                matches.append({
                    'id': paper_id,
                    'db_name': paper_name,
                    'db_filename': db_filename,
                    'found_path': potential['path'],
                    'match_type': 'exact_filename'
                })
                break
    
    print(f"\n通过文件名直接匹配找到 {len(matches)} 个匹配项")

# 创建输出文件
output_file = f"papers_outside_papers_dir_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_file, "w") as f:
    f.write(f"uploads目录中不在papers子目录的试卷文件 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    
    # 输出匹配结果
    if has_db and len(matches) > 0:
        f.write("== 与缺失数据库记录匹配的文件 ==\n")
        for idx, match in enumerate(matches, 1):
            f.write(f"{idx}. ID: {match['id']}, 数据库名称: {match['db_name']}\n")
            f.write(f"   数据库文件名: {match['db_filename']}\n")
            f.write(f"   找到位置: {match['found_path']}\n")
            f.write(f"   匹配类型: {match['match_type']}\n")
            f.write("-" * 80 + "\n")
        
        f.write("\n\n")
    
    # 输出所有潜在试卷
    f.write("== 所有不在papers子目录的潜在试卷文件 ==\n")
    for idx, paper in enumerate(potential_papers, 1):
        f.write(f"{idx}. 文件名: {paper['filename']}\n")
        f.write(f"   相对路径: {paper['rel_path']}\n")
        f.write(f"   大小: {paper['size'] / 1024:.2f} KB\n")
        f.write("-" * 80 + "\n")

if has_db:
    conn.close()

print(f"\n分析结果已保存到: {output_file}")
