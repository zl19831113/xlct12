#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
试卷文件匹配修复工具
功能：将数据库中的试卷记录与uploads文件夹中的实际文件进行匹配

问题：下载试卷时下载的是占位符，而不是实际的试卷文件
解决：扫描uploads文件夹，根据文件名与试卷名称的相似度进行匹配，更新数据库中的file_path字段
"""

import os
import re
import sqlite3
import glob
import shutil
from datetime import datetime
from difflib import SequenceMatcher

# 配置
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'papers')
BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup')

# 创建备份文件夹
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# 数据库备份
def backup_database():
    backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_FOLDER, f'question_bank_backup_{backup_time}.db')
    
    print(f"正在备份数据库到: {backup_file}")
    shutil.copy2(DB_PATH, backup_file)
    print("数据库备份完成")
    return backup_file

# 文件名清理和标准化
def normalize_filename(filename):
    # 移除文件扩展名
    name = os.path.splitext(filename)[0]
    
    # 移除常见的无关字符
    name = re.sub(r'[^\w\s\u4e00-\u9fff]+', ' ', name)
    
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name).strip().lower()
    
    return name

# 计算两个字符串的相似度
def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 查找最匹配的文件
def find_best_match(paper_name, paper_subject, paper_year, all_files):
    paper_name_norm = normalize_filename(paper_name)
    best_match = None
    best_score = 0
    
    # 如果年份是整数，转换为字符串进行匹配
    year_str = str(paper_year) if paper_year else ""
    
    for file_path in all_files:
        filename = os.path.basename(file_path)
        file_norm = normalize_filename(filename)
        
        # 基础相似度
        similarity = string_similarity(paper_name_norm, file_norm)
        
        # 增加权重：如果文件名包含学科名称
        if paper_subject and paper_subject.lower() in file_norm:
            similarity += 0.1
            
        # 增加权重：如果文件名包含年份
        if year_str and year_str in file_norm:
            similarity += 0.1
        
        # 如果这个匹配比之前的更好
        if similarity > best_score:
            best_score = similarity
            best_match = file_path
    
    # 匹配度超过阈值才返回
    if best_score >= 0.6:
        return best_match, best_score
    return None, 0

def main():
    # 备份数据库
    backup_file = backup_database()
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("""
        SELECT id, name, subject, year, file_path
        FROM papers
    """)
    papers = cursor.fetchall()
    print(f"获取到 {len(papers)} 份试卷记录")
    
    # 获取uploads文件夹中的所有文件
    all_files = []
    for ext in ['pdf', 'PDF', 'doc', 'DOC', 'docx', 'DOCX', 'zip', 'ZIP']:
        all_files.extend(glob.glob(os.path.join(UPLOAD_FOLDER, f'**/*.{ext}'), recursive=True))
    
    print(f"找到 {len(all_files)} 个试卷文件")
    
    # 匹配并更新数据库
    matched_count = 0
    unmatched_count = 0
    already_matched = 0
    
    for paper_id, paper_name, paper_subject, paper_year, file_path in papers:
        # 检查当前file_path是否有效
        current_full_path = os.path.join(UPLOAD_FOLDER, file_path) if file_path else None
        if current_full_path and os.path.exists(current_full_path):
            already_matched += 1
            continue
        
        # 查找最佳匹配文件
        best_match, score = find_best_match(paper_name, paper_subject, paper_year, all_files)
        
        if best_match:
            # 获取相对路径
            rel_path = os.path.relpath(best_match, UPLOAD_FOLDER)
            
            # 更新数据库
            cursor.execute("""
                UPDATE papers
                SET file_path = ?
                WHERE id = ?
            """, (rel_path, paper_id))
            
            print(f"匹配成功: {paper_name} -> {os.path.basename(best_match)} (匹配度: {score:.2f})")
            matched_count += 1
            
            # 从待匹配文件列表中删除已匹配文件
            all_files.remove(best_match)
        else:
            print(f"未找到匹配: {paper_name}")
            unmatched_count += 1
    
    # 提交更改
    conn.commit()
    
    # 输出统计信息
    print("\n===== 匹配结果统计 =====")
    print(f"总试卷数: {len(papers)}")
    print(f"已匹配试卷: {already_matched}")
    print(f"新匹配试卷: {matched_count}")
    print(f"未匹配试卷: {unmatched_count}")
    print(f"剩余未匹配文件: {len(all_files)}")
    
    if len(all_files) > 0:
        print("\n以下文件未被匹配:")
        for i, file in enumerate(all_files[:10]):
            print(f"  {i+1}. {os.path.basename(file)}")
        
        if len(all_files) > 10:
            print(f"  ... 还有 {len(all_files) - 10} 个文件未显示")
    
    # 关闭数据库连接
    conn.close()
    
    print(f"\n数据库备份保存在: {backup_file}")
    print("完成！现在试卷下载功能应该可以正常工作了")

if __name__ == "__main__":
    main()
