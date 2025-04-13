#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库试卷路径修复工具
功能：重置数据库中所有试卷的file_path字段，确保与实际文件正确对应
"""

import os
import re
import sqlite3
import glob
import shutil
from datetime import datetime
import hashlib
import tempfile
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 备份数据库
def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.repair_backup_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"已创建数据库备份: {backup_path}")
    return backup_path

# 获取文件内容的哈希值，用于文件比较
def get_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 尝试提取文件内容信息
def extract_file_info(file_path):
    """尝试从文件中提取信息，如标题和科目"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        # 使用临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
            # 尝试提取前10行内容
            if file_ext == '.pdf':
                # 使用pdftotext（需要安装）或其他PDF提取工具
                try:
                    subprocess.run(['pdftotext', '-f', '1', '-l', '2', file_path, temp.name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    # 如果pdftotext不可用，使用其他方法
                    return None
            elif file_ext in ('.doc', '.docx'):
                # 需要其他工具处理Word文档
                return None
            else:
                # 无法处理的格式
                return None
                
            # 读取提取的文本
            with open(temp.name, 'r', errors='ignore') as f:
                content = f.read(2000)  # 读取前2000个字符
                
            # 分析内容，寻找科目信息
            subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
            found_subjects = []
            for subject in subjects:
                if subject in content:
                    found_subjects.append(subject)
                    
            if found_subjects:
                return {'subjects': found_subjects, 'content_sample': content[:200]}
    except Exception as e:
        print(f"提取文件信息时出错: {e}")
    
    return None

def get_file_details(file_path):
    """获取文件详细信息"""
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    modification_time = os.path.getmtime(file_path)
    
    # 从文件名中提取信息
    year_match = re.search(r'20\d{2}', filename)
    year = year_match.group(0) if year_match else None
    
    # 从文件名中查找科目关键词
    subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    found_subjects = []
    for subject in subjects:
        if subject in filename:
            found_subjects.append(subject)
    
    # 提取文件内容信息（可选）
    content_info = extract_file_info(file_path) if file_ext in ('.pdf', '.doc', '.docx') else None
    
    return {
        'path': file_path,
        'name': filename,
        'size': file_size,
        'ext': file_ext,
        'year': year,
        'subjects_in_name': found_subjects,
        'content_info': content_info,
        'mod_time': modification_time
    }

def main():
    """主函数"""
    print("\n===== 数据库试卷路径修复工具 =====")
    
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
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, name, subject, year, region, file_path FROM papers ORDER BY id")
    papers = cursor.fetchall()
    
    total_papers = len(papers)
    print(f"\n共找到 {total_papers} 条试卷记录")
    
    # 加载所有试卷文件
    print("\n正在加载试卷文件...")
    all_files = []
    for root, _, files in os.walk(PAPERS_DIR):
        for file in files:
            if file.endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')) and not file.startswith('.'):
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    
    print(f"共找到 {len(all_files)} 个试卷文件")
    
    # 为每个文件创建索引
    print("\n正在对文件进行索引...")
    file_index = []
    for file_path in all_files:
        rel_path = os.path.relpath(file_path, PROJECT_ROOT)
        file_details = get_file_details(file_path)
        file_index.append(file_details)
    
    # 一对一匹配 - 通过文件名精确匹配
    print("\n第1阶段: 通过文件名精确匹配...")
    matched_papers = []
    unmatched_papers = []
    
    for paper in papers:
        paper_id, paper_name, paper_subject, paper_year, paper_region, current_path = paper
        matched = False
        
        # 检查当前路径是否有效
        if current_path and os.path.exists(os.path.join(PROJECT_ROOT, current_path)):
            # 当前路径有效，检查是否是正确的文件
            file_details = get_file_details(os.path.join(PROJECT_ROOT, current_path))
            
            # 判断是否包含正确的科目
            if paper_subject in file_details.get('subjects_in_name', []) or paper_subject == '':
                matched_papers.append((paper, current_path))
                matched = True
                print(f"  ✓ 文件ID {paper_id} ({paper_subject}) 保持原路径: {current_path}")
                continue
        
        # 尝试通过文件名找到精确匹配
        for file_details in file_index:
            rel_path = os.path.relpath(file_details['path'], PROJECT_ROOT)
            
            # 如果文件名中包含试卷ID，很可能是精确匹配
            if str(paper_id) in file_details['name']:
                if paper_subject in file_details.get('subjects_in_name', []) or not file_details.get('subjects_in_name'):
                    matched_papers.append((paper, rel_path))
                    matched = True
                    print(f"  ✓ 文件ID {paper_id} ({paper_subject}) 通过ID匹配: {rel_path}")
                    break
        
        if not matched:
            unmatched_papers.append(paper)
    
    # 第2阶段：科目+年份匹配
    print(f"\n第2阶段: 通过科目+年份匹配 ({len(unmatched_papers)} 个未匹配的试卷)...")
    still_unmatched = []
    
    for paper in unmatched_papers:
        paper_id, paper_name, paper_subject, paper_year, paper_region, _ = paper
        matched = False
        best_matches = []
        
        for file_details in file_index:
            rel_path = os.path.relpath(file_details['path'], PROJECT_ROOT)
            
            # 如果已经有文件匹配了该路径，跳过
            if any(rel_path == matched_path for _, matched_path in matched_papers):
                continue
            
            # 检查科目匹配
            if paper_subject in file_details.get('subjects_in_name', []):
                # 检查年份匹配
                if file_details.get('year') and str(paper_year) == file_details.get('year'):
                    score = 80  # 科目+年份匹配，高分
                    best_matches.append((rel_path, score))
                else:
                    score = 60  # 只有科目匹配，中等分数
                    best_matches.append((rel_path, score))
        
        # 按匹配分数排序
        if best_matches:
            best_matches.sort(key=lambda x: x[1], reverse=True)
            best_match, score = best_matches[0]
            matched_papers.append((paper, best_match))
            matched = True
            print(f"  ✓ 文件ID {paper_id} ({paper_subject}) 通过科目匹配: {best_match}")
        
        if not matched:
            still_unmatched.append(paper)
    
    # 第3阶段: 未匹配试卷的处理
    print(f"\n第3阶段: 处理剩余的未匹配试卷 ({len(still_unmatched)} 个)...")
    
    # 找出尚未分配的文件
    assigned_paths = [path for _, path in matched_papers]
    unassigned_files = []
    
    for file_details in file_index:
        rel_path = os.path.relpath(file_details['path'], PROJECT_ROOT)
        if rel_path not in assigned_paths:
            unassigned_files.append(file_details)
    
    print(f"  剩余未分配的文件: {len(unassigned_files)} 个")
    
    # 为剩余未匹配的试卷随机分配未分配的文件
    for i, paper in enumerate(still_unmatched):
        if i < len(unassigned_files):
            paper_id, paper_name, paper_subject, paper_year, paper_region, _ = paper
            file_details = unassigned_files[i]
            rel_path = os.path.relpath(file_details['path'], PROJECT_ROOT)
            matched_papers.append((paper, rel_path))
            print(f"  ✓ 文件ID {paper_id} ({paper_subject}) 随机分配: {rel_path}")
        else:
            print(f"  ✗ 文件ID {paper_id} ({paper_subject}) 无法分配文件，文件数量不足")
    
    # 更新数据库
    print("\n正在更新数据库...")
    updated_count = 0
    
    for paper, new_path in matched_papers:
        paper_id = paper[0]
        old_path = paper[5]
        
        if old_path != new_path:
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, paper_id))
            updated_count += 1
    
    # 提交更改
    conn.commit()
    conn.close()
    
    # 打印统计信息
    print("\n===== 修复完成 =====")
    print(f"总试卷数: {total_papers}")
    print(f"已更新: {updated_count}")
    print(f"未更新: {total_papers - updated_count}")
    
    print("\n数据库修复完成！请重启应用以应用更改。")

if __name__ == "__main__":
    main() 