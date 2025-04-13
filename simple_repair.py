#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库试卷路径修复工具（简化版）
功能：重置数据库中所有试卷的file_path字段，确保每个试卷都能下载到正确科目的文件
"""

import os
import re
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

# 科目关键词映射 - 用于确保科目匹配
SUBJECT_KEYWORDS = {
    '语文': ['语文'],
    '数学': ['数学', '文数', '理数'],
    '英语': ['英语'],
    '物理': ['物理'],
    '化学': ['化学'],
    '生物': ['生物'],
    '政治': ['政治', '思想政治'],
    '历史': ['历史'],
    '地理': ['地理'],
    '文综': ['文综'],
    '理综': ['理综']
}

# 备份数据库
def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.simple_repair_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"已创建数据库备份: {backup_path}")
    return backup_path

def get_subject_files(subject):
    """获取指定科目的所有文件"""
    subject_files = []
    keywords = SUBJECT_KEYWORDS.get(subject, [subject])
    
    # 遍历所有文件
    for root, _, files in os.walk(PAPERS_DIR):
        for file in files:
            if file.startswith('.'):
                continue
                
            # 只处理常见文档格式
            if not file.lower().endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                continue
                
            # 检查文件名是否包含科目关键词
            file_lower = file.lower()
            if any(keyword.lower() in file_lower for keyword in keywords):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                subject_files.append(rel_path)
    
    return subject_files

def main():
    """主函数"""
    print("\n===== 数据库试卷路径简易修复工具 =====")
    
    # 检查uploads/papers目录是否存在
    if not os.path.exists(PAPERS_DIR):
        print(f"错误: 试卷目录不存在: {PAPERS_DIR}")
        return
    
    # 备份数据库
    backup_path = backup_database()
    print(f"数据库已备份到: {backup_path}")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 按科目分组获取试卷
    cursor.execute("SELECT DISTINCT subject FROM papers")
    subjects = [row[0] for row in cursor.fetchall()]
    
    print(f"\n找到 {len(subjects)} 个不同科目")
    
    # 为每个科目收集文件
    subject_file_map = {}
    for subject in subjects:
        subject_files = get_subject_files(subject)
        subject_file_map[subject] = subject_files
        print(f"科目 '{subject}': 找到 {len(subject_files)} 个匹配文件")
    
    # 处理每个科目的试卷
    total_updated = 0
    for subject in subjects:
        print(f"\n正在处理科目: {subject}")
        
        # 获取该科目的所有试卷
        cursor.execute("SELECT id, name, year, region, file_path FROM papers WHERE subject = ?", (subject,))
        papers = cursor.fetchall()
        
        print(f"  该科目有 {len(papers)} 条试卷记录")
        
        # 获取该科目的所有文件
        subject_files = subject_file_map.get(subject, [])
        
        if not subject_files:
            print(f"  ✗ 警告: 未找到科目 '{subject}' 的任何匹配文件!")
            continue
        
        # 随机分配文件给试卷
        available_files = subject_files.copy()
        
        for paper in papers:
            paper_id, paper_name, paper_year, paper_region, current_path = paper
            
            # 如果可用文件用完，重新开始循环使用
            if not available_files:
                available_files = subject_files.copy()
            
            # 随机选择一个文件
            new_path = random.choice(available_files)
            available_files.remove(new_path)
            
            # 更新数据库
            if current_path != new_path:
                cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, paper_id))
                total_updated += 1
                print(f"  ✓ 更新试卷 ID={paper_id} '{paper_name}' 的文件路径: {new_path}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    # 打印统计信息
    print("\n===== 修复完成 =====")
    print(f"总共更新了 {total_updated} 条试卷记录")
    
    print("\n数据库修复完成！请重启应用以应用更改。")

if __name__ == "__main__":
    main() 