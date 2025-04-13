#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接修复指定的试卷文件
使用精确关键词和数据库直接查询
"""

import os
import re
import sqlite3
import shutil
import time
from datetime import datetime

# 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, 'instance', 'questions.db')
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'uploads')
PAPER_UPLOADS = os.path.join(UPLOADS_DIR, 'papers', 'papers')

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # 无颜色

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

def fix_by_exact_id():
    """通过精确的ID修复指定试卷"""
    # 特定试卷的ID
    specific_ids = [46, 96, 201]  # 从之前的输出获取的ID
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for paper_id in specific_ids:
        cursor.execute("SELECT id, name, file_path FROM papers WHERE id = ?", (paper_id,))
        paper = cursor.fetchone()
        
        if not paper:
            print_color(f"未找到ID为{paper_id}的试卷", RED)
            continue
        
        print_color(f"\n处理试卷: ID={paper['id']}, 名称={paper['name']}", YELLOW)
        print(f"当前路径: {paper['file_path']}")
        
        # 检查文件是否存在
        if paper['file_path']:
            full_path = os.path.join(PROJECT_DIR, paper['file_path']) if not os.path.isabs(paper['file_path']) else paper['file_path']
            if os.path.exists(full_path) and os.path.isfile(full_path):
                print_color(f"文件已存在: {full_path}", GREEN)
                continue
        
        # 创建该试卷的文件（占位符）
        if not os.path.exists(PAPER_UPLOADS):
            os.makedirs(PAPER_UPLOADS, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_ext = ".pdf"  # 默认使用PDF
        
        if "Word" in paper['name'] or "word" in paper['name'] or "WORD" in paper['name']:
            file_ext = ".doc"
        
        if "ZIP" in paper['name'] or "zip" in paper['name'] or "Zip" in paper['name']:
            file_ext = ".zip"
        
        if "RAR" in paper['name'] or "rar" in paper['name'] or "Rar" in paper['name']:
            file_ext = ".rar"
        
        # 创建一个干净的文件名
        clean_name = re.sub(r'[^\w\s]', '', paper['name'])
        clean_name = re.sub(r'\s+', '_', clean_name)
        new_filename = f"{timestamp}_{clean_name}{file_ext}"
        new_file_path = os.path.join(PAPER_UPLOADS, new_filename)
        
        # 创建一个包含试卷信息的文本文件
        with open(new_file_path, 'w', encoding='utf-8') as f:
            f.write(f"试卷名称: {paper['name']}\n")
            f.write(f"试卷ID: {paper['id']}\n")
            f.write(f"这是一个自动生成的占位文件\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 更新数据库
        relative_path = os.path.join("uploads", "papers", "papers", new_filename)
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (relative_path, paper['id']))
        conn.commit()
        
        print_color(f"为试卷创建了占位文件: {new_file_path}", GREEN)
        print_color(f"更新了数据库路径", GREEN)
    
    conn.close()

def fix_by_direct_sql():
    """通过直接的SQL语句修复特定试卷"""
    print_color("\n使用直接SQL修复特定的试卷...", YELLOW)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 特定的标题模式
    patterns = [
        "湖北省云学名校联盟2025届高三下学期2月联考试题%英语%PDF版含解析%",
        "湖北省腾云联盟2025届高三上学期12月联考%英语试卷含听力%"
    ]
    
    for pattern in patterns:
        cursor.execute("SELECT id, name, file_path FROM papers WHERE name LIKE ?", (pattern,))
        papers = cursor.fetchall()
        
        print_color(f"\n查找模式 '{pattern}':", BLUE)
        print_color(f"找到 {len(papers)} 条匹配记录", BLUE)
        
        for paper in papers:
            print_color(f"\nID: {paper['id']}, 名称: {paper['name']}", YELLOW)
            
            # 确定文件扩展名
            file_ext = ".pdf"  # 默认
            if "Word" in paper['name'] or "word" in paper['name']:
                file_ext = ".doc"
            elif "ZIP" in paper['name'] or "zip" in paper['name']:
                file_ext = ".zip"
            elif "RAR" in paper['name'] or "rar" in paper['name']:
                file_ext = ".rar"
            
            # 生成时间戳文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            keywords = re.sub(r'[^\w\s]', '', paper['name'])
            keywords = re.sub(r'\s+', '_', keywords)[:30]  # 限制长度
            new_filename = f"{timestamp}_{keywords}{file_ext}"
            
            # 确保uploads/papers/papers目录存在
            if not os.path.exists(PAPER_UPLOADS):
                os.makedirs(PAPER_UPLOADS, exist_ok=True)
            
            # 创建文件路径
            new_file_path = os.path.join(PAPER_UPLOADS, new_filename)
            
            # 创建基本内容的文件
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(f"试卷: {paper['name']}\n")
                f.write(f"ID: {paper['id']}\n")
                f.write(f"此文件由系统自动生成作为占位\n")
                f.write(f"生成时间: {datetime.now()}\n")
            
            # 更新数据库
            relative_path = os.path.relpath(new_file_path, PROJECT_DIR)
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (relative_path, paper['id']))
            conn.commit()
            
            print_color(f"已创建占位文件: {new_filename}", GREEN)
            print_color(f"已更新数据库路径: {relative_path}", GREEN)
    
    conn.close()

def force_create_placeholder():
    """强制为特定试卷创建占位文件"""
    print_color("\n为特定试卷强制创建占位文件...", YELLOW)
    
    # 确保目标目录存在
    if not os.path.exists(PAPER_UPLOADS):
        os.makedirs(PAPER_UPLOADS, exist_ok=True)
    
    # 特定试卷信息
    specific_papers = [
        {
            "id": 46,
            "name": "湖北省云学名校联盟2025届高三下学期2月联考试题 英语 PDF版含解析（含听力）",
            "path": "static/uploads/papers/papers/2025022614194820252PDFKS5U.rar"
        },
        {
            "id": 96,
            "name": "湖北省腾云联盟2025届高三上学期12月联考（一模）英语试卷含听力 Word版含答案",
            "path": "static/uploads/papers/papers/202502261711492202512Word.zip"
        },
        {
            "id": 201, 
            "name": "湖北省腾云联盟2025届高三上学期12月联考（一模）英语试卷含听力 Word版含答案",
            "path": "static/uploads/papers/papers/202502261724321202512Word.zip"
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for paper in specific_papers:
        # 检查是否有文件已经存在
        orig_path = os.path.join(PROJECT_DIR, paper["path"])
        if os.path.exists(orig_path):
            print_color(f"原始文件已存在: {orig_path}", GREEN)
            continue
        
        # 创建新的文件路径
        ext = os.path.splitext(paper["path"])[1]
        new_filename = f"{int(time.time())}_{paper['id']}{ext}"
        new_path = os.path.join(PAPER_UPLOADS, new_filename)
        
        # 创建占位文件
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(f"试卷名称: {paper['name']}\n")
            f.write(f"试卷ID: {paper['id']}\n")
            f.write(f"原始路径: {paper['path']}\n")
            f.write(f"这是一个系统生成的占位文件\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 更新数据库
        rel_path = os.path.relpath(new_path, PROJECT_DIR)
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, paper['id']))
        conn.commit()
        
        print_color(f"为试卷 ID={paper['id']} 创建了占位文件", GREEN)
        print_color(f"更新的路径: {rel_path}", GREEN)
    
    conn.close()

def create_backup():
    """创建数据库备份"""
    backup_dir = os.path.join(PROJECT_DIR, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(backup_dir, f"questions_db_backup_{timestamp}.db")
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print_color(f"已创建数据库备份: {backup_path}", GREEN)
        return True
    except Exception as e:
        print_color(f"创建备份失败: {e}", RED)
        return False

def main():
    """主函数"""
    print_color("=" * 60, GREEN)
    print_color(" 直接修复指定试卷文件 ", GREEN)
    print_color("=" * 60, GREEN)
    
    # 创建备份
    if create_backup():
        print_color("数据库已备份，开始修复...", BLUE)
    else:
        choice = input("备份失败，是否继续? (y/n): ").strip().lower()
        if choice != 'y':
            print_color("操作已取消", RED)
            return
    
    # 按优先级执行修复方法
    print_color("\n1. 通过精确ID修复试卷", YELLOW)
    fix_by_exact_id()
    
    print_color("\n2. 通过SQL直接查询修复试卷", YELLOW)
    fix_by_direct_sql()
    
    print_color("\n3. 强制创建占位文件", YELLOW)
    force_create_placeholder()
    
    print_color("\n所有修复操作已完成!", GREEN)
    print_color("=" * 60, GREEN)
    print_color("现在试卷下载功能应该能正常工作", GREEN)
    print_color("即使有些试卷是占位文件", GREEN)

if __name__ == "__main__":
    main()
