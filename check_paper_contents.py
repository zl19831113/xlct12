#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
试卷内容检查工具
功能：检查文件内容与数据库记录的科目是否匹配
"""

import os
import sqlite3
import shutil
import re
import sys
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 科目关键词，确保更全面的匹配
SUBJECT_KEYWORDS = {
    '语文': ['语文', '作文', '阅读', '文言文'],
    '数学': ['数学', '文数', '理数', '函数', '方程', '导数', '三角函数'],
    '英语': ['英语', 'English', '单词', '阅读理解', 'reading'],
    '物理': ['物理', '力学', '电学', '热学', '光学'],
    '化学': ['化学', '元素', '分子', '化合物', '反应'],
    '生物': ['生物', '细胞', '遗传', '进化', '生态'],
    '政治': ['政治', '思想政治', '哲学', '经济', '法律', '道德', '思想'],
    '历史': ['历史', '朝代', '战争', '改革', '革命', '文化', '近代史'],
    '地理': ['地理', '气候', '地形', '人口', '资源', '环境', '地图'],
    '文综': ['文综', '政治', '历史', '地理'],
    '理综': ['理综', '物理', '化学', '生物']
}

def check_file_content(file_path, expected_subject):
    """检查文件内容是否与指定科目匹配"""
    if not os.path.exists(file_path):
        return False, "文件不存在"
    
    # 获取文件名
    filename = os.path.basename(file_path)
    
    # 检查文件名中是否包含预期科目的关键词
    keywords = SUBJECT_KEYWORDS.get(expected_subject, [expected_subject])
    for keyword in keywords:
        if keyword in filename:
            return True, f"文件名包含关键词 '{keyword}'"
    
    # 如果文件名不包含预期科目的关键词，检查是否包含其他科目的关键词
    mismatched_subjects = []
    for subject, subject_keywords in SUBJECT_KEYWORDS.items():
        if subject == expected_subject:
            continue
        
        for keyword in subject_keywords:
            if keyword in filename and subject not in mismatched_subjects:
                mismatched_subjects.append(subject)
                break
    
    if mismatched_subjects:
        return False, f"文件名可能与科目 {', '.join(mismatched_subjects)} 匹配"
    
    return False, "文件名不包含相关科目关键词"

def main():
    """主函数"""
    print("\n===== 试卷内容科目检查工具 =====")
    
    # 检查uploads/papers目录是否存在
    if not os.path.exists(PAPERS_DIR):
        print(f"错误: 试卷目录不存在: {PAPERS_DIR}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, subject, name, file_path FROM papers")
    papers = cursor.fetchall()
    
    print(f"共找到 {len(papers)} 条试卷记录")
    
    # 记录匹配和不匹配的试卷
    matching_papers = []
    mismatching_papers = []
    missing_files = []
    
    # 检查每个试卷
    print("\n正在检查试卷文件名与科目是否匹配...")
    for paper in papers:
        paper_id, subject, name, file_path = paper
        
        if not file_path:
            missing_files.append((paper_id, subject, name, "未设置文件路径"))
            continue
        
        # 构建完整文件路径
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if not os.path.exists(full_path):
            missing_files.append((paper_id, subject, name, f"文件不存在: {file_path}"))
            continue
        
        # 检查文件内容
        is_match, reason = check_file_content(full_path, subject)
        
        if is_match:
            matching_papers.append((paper_id, subject, name, file_path, reason))
        else:
            mismatching_papers.append((paper_id, subject, name, file_path, reason))
    
    # 打印结果
    print(f"\n匹配的试卷: {len(matching_papers)} 份")
    print(f"不匹配的试卷: {len(mismatching_papers)} 份")
    print(f"文件丢失: {len(missing_files)} 份")
    
    # 打印不匹配的试卷详情
    if mismatching_papers:
        print("\n=== 不匹配的试卷详情 ===")
        for idx, (paper_id, subject, name, file_path, reason) in enumerate(mismatching_papers[:20], 1):
            print(f"{idx}. ID: {paper_id}, 科目: {subject}, 文件: {os.path.basename(file_path)}")
            print(f"   原因: {reason}")
            print(f"   试卷名称: {name}")
            print()
        
        if len(mismatching_papers) > 20:
            print(f"...还有 {len(mismatching_papers) - 20} 份不匹配的试卷未显示")
    
    # 打印丢失文件的试卷
    if missing_files:
        print("\n=== 文件丢失的试卷 ===")
        for idx, (paper_id, subject, name, reason) in enumerate(missing_files[:20], 1):
            print(f"{idx}. ID: {paper_id}, 科目: {subject}")
            print(f"   原因: {reason}")
            print(f"   试卷名称: {name}")
            print()
        
        if len(missing_files) > 20:
            print(f"...还有 {len(missing_files) - 20} 份文件丢失的试卷未显示")
    
    conn.close()
    print("\n检查完成！")

if __name__ == "__main__":
    main() 