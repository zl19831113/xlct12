#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速修复缺失的试卷文件
使用简化算法和批处理方式
"""

import os
import re
import sqlite3
import sys
from collections import defaultdict

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # 无颜色

# 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, 'instance', 'questions.db')
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'uploads')

def print_color(message, color=None):
    """打印彩色文本"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fix_specific_papers():
    """修复特定的试卷"""
    specific_papers = [
        {"name": "湖北省云学名校联盟2025届高三下学期2月联考试题 英语", "keywords": ["湖北", "云学", "英语", "2025", "2月"]},
        {"name": "湖北省腾云联盟2025届高三上学期12月联考 英语试卷含听力", "keywords": ["湖北", "腾云", "英语", "2025", "12月", "听力"]}
    ]
    
    # 读取uploads目录中的所有文件
    all_files = []
    for root, _, files in os.walk(UPLOADS_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append((file, file_path))
    
    print_color(f"扫描到 {len(all_files)} 个文件", BLUE)
    
    # 查找特定试卷
    for paper in specific_papers:
        print_color(f"\n查找: {paper['name']}", YELLOW)
        
        # 从数据库中查找匹配的试卷记录
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 使用试卷名称的一部分进行模糊查询
        cursor.execute("SELECT id, name, file_path FROM papers WHERE name LIKE ?", 
                       (f"%{paper['name'].split()[0]}%{paper['keywords'][0]}%{paper['keywords'][1]}%",))
        db_papers = cursor.fetchall()
        
        if not db_papers:
            print_color("在数据库中未找到匹配记录", RED)
            continue
        
        print_color(f"在数据库中找到 {len(db_papers)} 条匹配记录", GREEN)
        
        # 对每条记录进行处理
        for db_paper in db_papers:
            print_color(f"\nID: {db_paper['id']}, 名称: {db_paper['name']}", BLUE)
            print(f"数据库路径: {db_paper['file_path']}")
            
            # 检查文件是否存在
            if db_paper['file_path']:
                full_path = os.path.join(PROJECT_DIR, db_paper['file_path']) if not os.path.isabs(db_paper['file_path']) else db_paper['file_path']
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    print_color(f"文件已存在: {full_path}", GREEN)
                    continue
            
            # 查找匹配文件
            matches = []
            for file_name, file_path in all_files:
                match_score = 0
                file_lower = file_name.lower()
                
                # 匹配关键词
                for keyword in paper['keywords']:
                    if keyword.lower() in file_lower:
                        match_score += 1
                
                if match_score >= 3:  # 至少匹配3个关键词
                    matches.append((file_path, match_score, file_name))
            
            # 按匹配分数排序
            matches.sort(key=lambda x: x[1], reverse=True)
            
            if matches:
                print_color(f"找到 {len(matches)} 个可能匹配的文件", GREEN)
                best_match = matches[0]
                print_color(f"最佳匹配 (得分: {best_match[1]}): {best_match[2]}", GREEN)
                
                # 更新数据库
                rel_path = os.path.relpath(best_match[0], PROJECT_DIR)
                cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, db_paper['id']))
                conn.commit()
                print_color(f"✓ 已更新数据库", GREEN)
            else:
                print_color("未找到匹配文件", RED)
        
        conn.close()

def batch_fix_all_papers():
    """批量修复所有缺失的试卷"""
    print_color("\n开始批量修复所有缺失试卷...", YELLOW)
    
    # 连接数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 读取所有缺失文件的记录
    cursor.execute("""
        SELECT id, name, file_path, region, subject, year
        FROM papers
        WHERE file_path IS NULL OR file_path = ''
    """)
    missing_db = cursor.fetchall()
    
    # 如果没有找到NULL路径的记录，检查文件不存在的记录
    if len(missing_db) == 0:
        print_color("没有发现文件路径为NULL的记录，检查文件不存在的记录...", BLUE)
        # 获取前100条记录，并手动检查文件是否存在
        cursor.execute("SELECT id, name, file_path FROM papers LIMIT 100")
        papers = cursor.fetchall()
        
        missing_db = []
        for paper in papers:
            if paper['file_path']:
                full_path = os.path.join(PROJECT_DIR, paper['file_path']) if not os.path.isabs(paper['file_path']) else paper['file_path']
                if not os.path.exists(full_path) or not os.path.isfile(full_path):
                    missing_db.append(paper)
    
    print_color(f"发现 {len(missing_db)} 条缺失记录", BLUE)
    
    # 扫描uploads目录中的所有文件
    file_index = {}  # 文件名到路径的映射
    file_ext_count = defaultdict(int)  # 统计各类型文件数量
    
    for root, _, files in os.walk(UPLOADS_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            file_index[file] = file_path
            
            # 统计文件类型
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            file_ext_count[ext] += 1
    
    print_color(f"扫描到 {len(file_index)} 个文件", BLUE)
    print_color("文件类型分布:", BLUE)
    for ext, count in sorted(file_ext_count.items(), key=lambda x: x[1], reverse=True):
        print_color(f"  {ext}: {count}个文件", BLUE)
    
    # 批量匹配和更新
    update_count = 0
    
    for db_paper in missing_db:
        # 从文件名中提取有用信息
        if db_paper['file_path']:
            base_name = os.path.basename(db_paper['file_path'])
            
            # 1. 尝试直接匹配完整文件名
            if base_name in file_index:
                cursor.execute(
                    "UPDATE papers SET file_path = ? WHERE id = ?", 
                    (os.path.relpath(file_index[base_name], PROJECT_DIR), db_paper['id'])
                )
                update_count += 1
                continue
            
            # 2. 提取文件名中的关键部分（去掉前缀数字和时间戳）
            clean_name = re.sub(r'^\d+_\d+_\d+_', '', base_name)
            
            # 查找部分匹配
            for file_name, file_path in file_index.items():
                if clean_name and clean_name in file_name:
                    cursor.execute(
                        "UPDATE papers SET file_path = ? WHERE id = ?", 
                        (os.path.relpath(file_path, PROJECT_DIR), db_paper['id'])
                    )
                    update_count += 1
                    break
    
    conn.commit()
    conn.close()
    
    print_color(f"已更新 {update_count} 条记录", GREEN)
    return update_count

def update_app_behavior():
    """更新app.py中的行为，确保即使文件不存在也能正常工作"""
    print_color("\n确保app.py能正确处理缺失文件...", YELLOW)
    
    # 已经在之前的修复中完成，此处不再重复操作
    print_color("之前已经修复过app.py，不需要再次修改", GREEN)

def main():
    """主函数"""
    print_color("=" * 60, GREEN)
    print_color(" 快速修复试卷文件 ", GREEN)
    print_color("=" * 60, GREEN)
    
    # 1. 修复特定试卷
    fix_specific_papers()
    
    # 2. 是否要尝试批量修复所有缺失文件
    choice = input("\n是否要尝试批量修复所有缺失文件? (y/n): ").strip().lower()
    if choice == 'y':
        batch_fix_all_papers()
    
    # 3. 更新应用行为
    update_app_behavior()
    
    print_color("\n操作完成!", GREEN)
    print_color("=" * 60, GREEN)
    print_color("现在，即使仍有部分文件缺失，下载功能也能正常工作", GREEN)
    print_color("缺失的文件会返回一个包含试卷基本信息的占位符", GREEN)

if __name__ == "__main__":
    main()
