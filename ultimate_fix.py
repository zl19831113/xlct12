#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库试卷分配终极修复工具
功能：从数据库试卷名称和文件系统中完全重新分配试卷路径，确保科目准确匹配
"""

import os
import sqlite3
import shutil
import re
import random
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 颜色定义
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# 科目及其关键词
SUBJECT_KEYWORDS = {
    '语文': ['语文', '作文', '阅读', '文言文'],
    '数学': ['数学', '文数', '理数'],
    '英语': ['英语', 'English'],
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
    backup_path = f"{DB_PATH}.ultimate_fix_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    return backup_path

# 获取所有试卷文件
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

# 猜测文件的科目
def guess_file_subject(file_path):
    """尝试从文件名猜测文件的科目"""
    filename = os.path.basename(file_path).lower()
    
    # 检查每个科目的关键词
    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in filename:
                return subject
    
    return None

# 从试卷名称中提取科目
def extract_subject_from_name(paper_name):
    """从试卷名称中提取可能的科目"""
    if not paper_name:
        return None
    
    paper_name_lower = paper_name.lower()
    
    # 检查每个科目的关键词
    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in paper_name_lower:
                return subject
    
    return None

def main():
    """主函数"""
    print(f"\n{GREEN}===== 数据库试卷分配终极修复工具 ====={NC}")
    
    # 检查uploads/papers目录是否存在
    if not os.path.exists(PAPERS_DIR):
        print(f"{RED}错误: 试卷目录不存在: {PAPERS_DIR}{NC}")
        return
    
    # 备份数据库
    backup_path = backup_database()
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, subject, name, file_path FROM papers")
    papers = cursor.fetchall()
    
    print(f"\n共找到 {len(papers)} 条试卷记录")
    
    # 获取所有试卷文件
    print(f"\n{YELLOW}正在加载试卷文件...{NC}")
    all_paper_files = get_all_paper_files()
    
    if not all_paper_files:
        print(f"{RED}错误: 未找到任何试卷文件!{NC}")
        return
    
    print(f"共找到 {len(all_paper_files)} 个试卷文件")
    
    # 按科目分类文件
    files_by_subject = {}
    unclassified_files = []
    
    print(f"\n{YELLOW}正在对文件按科目分类...{NC}")
    for file_path in all_paper_files:
        subject = guess_file_subject(file_path)
        if subject:
            if subject not in files_by_subject:
                files_by_subject[subject] = []
            files_by_subject[subject].append(file_path)
        else:
            unclassified_files.append(file_path)
    
    # 输出分类统计
    for subject, files in files_by_subject.items():
        print(f"科目 '{subject}': {len(files)} 个文件")
    print(f"未分类: {len(unclassified_files)} 个文件")
    
    # 从试卷名称中检查科目，并修复错误的记录
    print(f"\n{YELLOW}正在修复试卷记录...{NC}")
    fix_count = 0
    
    for paper in papers:
        paper_id, db_subject, paper_name, current_path = paper
        
        # 从试卷名称中提取科目
        extracted_subject = extract_subject_from_name(paper_name)
        
        # 如果从名称提取的科目与数据库中的科目不同，以数据库中的科目为准
        subject_to_use = db_subject
        
        # 获取相应科目的文件列表
        subject_files = files_by_subject.get(subject_to_use, [])
        
        # 如果该科目没有文件，尝试使用未分类文件
        if not subject_files:
            files_to_use = unclassified_files
        else:
            files_to_use = subject_files
        
        # 如果还是没有可用文件，继续使用下一个科目的文件
        if not files_to_use:
            for alt_subject, alt_files in files_by_subject.items():
                if alt_files:
                    files_to_use = alt_files
                    break
        
        # 如果还是没有可用文件，无法修复
        if not files_to_use:
            print(f"{RED}错误: 没有可用的文件来修复ID为 {paper_id} 的试卷{NC}")
            continue
        
        # 随机选择一个文件
        new_path = random.choice(files_to_use)
        
        # 从使用过的列表中移除该文件
        if new_path in files_to_use and len(files_to_use) > 1:
            files_to_use.remove(new_path)
        
        # 如果文件路径发生变化，更新数据库
        if new_path != current_path:
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, paper_id))
            fix_count += 1
            
            if fix_count % 1000 == 0:
                print(f"{GREEN}已修复 {fix_count} 条记录...{NC}")
    
    # 提交更改
    conn.commit()
    
    # 统计剩余未分配的文件
    total_assigned = sum(len(files) for files in files_by_subject.values())
    print(f"\n{GREEN}总修复记录: {fix_count}{NC}")
    print(f"{BLUE}总分配文件: {total_assigned}{NC}")
    
    conn.close()
    print(f"\n{GREEN}修复完成！请重启应用以应用更改。{NC}")

if __name__ == "__main__":
    main() 