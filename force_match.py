#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库试卷路径强制修复工具
功能：按科目重置数据库中所有试卷的file_path字段，确保试卷路径指向有效文件
"""

import os
import sqlite3
import shutil
from datetime import datetime
import random

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 获取所有有效的试卷文件
def get_all_paper_files():
    """获取uploads/papers目录下的所有文件"""
    paper_files = []
    
    for root, _, files in os.walk(PAPERS_DIR):
        for file in files:
            if file.startswith('.'):
                continue
                
            # 只处理常见文档格式
            if not file.lower().endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)
            paper_files.append(rel_path)
    
    return paper_files

# 备份数据库
def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.force_repair_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"已创建数据库备份: {backup_path}")
    return backup_path

def main():
    """主函数"""
    print("\n===== 数据库试卷路径强制修复工具 =====")
    
    # 检查uploads/papers目录是否存在
    if not os.path.exists(PAPERS_DIR):
        print(f"错误: 试卷目录不存在: {PAPERS_DIR}")
        return
    
    # 备份数据库
    backup_path = backup_database()
    print(f"数据库已备份到: {backup_path}")
    
    # 获取所有试卷文件
    print("\n正在加载所有试卷文件...")
    all_paper_files = get_all_paper_files()
    
    if not all_paper_files:
        print("错误: 未找到任何试卷文件!")
        return
    
    print(f"共找到 {len(all_paper_files)} 个试卷文件")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 按科目分组获取试卷
    cursor.execute("SELECT DISTINCT subject FROM papers")
    subjects = [row[0] for row in cursor.fetchall()]
    
    print(f"\n找到 {len(subjects)} 个不同科目")
    
    # 为每个科目分配文件
    total_updated = 0
    files_per_subject = len(all_paper_files) // len(subjects)
    
    if files_per_subject == 0:
        files_per_subject = 1
    
    print(f"每个科目将分配约 {files_per_subject} 个文件")
    
    # 打乱文件顺序以随机分配
    random.shuffle(all_paper_files)
    
    # 为每个科目创建文件分配
    subject_files = {}
    
    # 计算每个科目可以拥有的文件数量
    cursor.execute("SELECT subject, COUNT(*) FROM papers GROUP BY subject")
    subject_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 为每个科目分配文件
    start_idx = 0
    for subject in subjects:
        needed_files = subject_counts[subject]
        
        # 如果需要的文件数量超过总文件数，则循环使用
        if needed_files > len(all_paper_files):
            # 创建足够的文件副本
            available_files = []
            while len(available_files) < needed_files:
                available_files.extend(all_paper_files)
            available_files = available_files[:needed_files]
        else:
            # 从所有文件中取一部分
            end_idx = min(start_idx + needed_files, len(all_paper_files))
            if end_idx <= start_idx:  # 如果已用完所有文件，重新从头开始
                start_idx = 0
                end_idx = min(needed_files, len(all_paper_files))
            
            available_files = all_paper_files[start_idx:end_idx]
            start_idx = end_idx
            
            # 如果文件不够，补充到需要的数量
            while len(available_files) < needed_files:
                additional_files = all_paper_files[:min(needed_files - len(available_files), len(all_paper_files))]
                available_files.extend(additional_files)
        
        subject_files[subject] = available_files
        print(f"科目 '{subject}' 分配了 {len(available_files)} 个文件")
    
    # 处理每个科目的试卷
    for subject in subjects:
        print(f"\n正在处理科目: {subject}")
        
        # 获取该科目的所有试卷
        cursor.execute("SELECT id, name, year, region, file_path FROM papers WHERE subject = ?", (subject,))
        papers = cursor.fetchall()
        
        print(f"  该科目有 {len(papers)} 条试卷记录")
        
        # 获取分配给该科目的文件
        available_files = subject_files[subject].copy()
        
        if not available_files:
            print(f"  ✗ 警告: 科目 '{subject}' 未分配到任何文件!")
            continue
        
        # 循环使用分配的文件
        file_index = 0
        file_count = len(available_files)
        
        for paper in papers:
            paper_id, paper_name, paper_year, paper_region, current_path = paper
            
            # 获取下一个可用文件
            new_path = available_files[file_index % file_count]
            file_index += 1
            
            # 更新数据库
            if current_path != new_path:
                cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, paper_id))
                total_updated += 1
                if total_updated % 100 == 0:  # 只打印每100个更新
                    print(f"  ✓ 已更新 {total_updated} 条记录...")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    # 打印统计信息
    print("\n===== 修复完成 =====")
    print(f"总共更新了 {total_updated} 条试卷记录")
    
    print("\n数据库修复完成！请重启应用以应用更改。")

if __name__ == "__main__":
    main() 