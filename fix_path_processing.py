#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复试卷文件路径处理问题
创建时间: 2025-03-29
"""

import os
import sqlite3
import sys
from datetime import datetime
import shutil

# 彩色输出
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

# 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, 'instance', 'questions.db')
BACKUP_DIR = os.path.join(PROJECT_DIR, 'backup')

def print_color(message, color=None):
    """打印彩色文本"""
    if color:
        print(f"{color}{message}{END}")
    else:
        print(message)

def backup_database():
    """备份数据库"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"questions_path_backup_{backup_time}.db")
    
    print_color(f"正在备份数据库到: {backup_path}", BLUE)
    shutil.copy2(DB_PATH, backup_path)
    print_color("数据库备份完成", GREEN)
    
    return backup_path

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_file_exists(file_path):
    """检查文件是否存在"""
    # 如果是绝对路径
    if os.path.isabs(file_path):
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    # 如果是相对路径，尝试从项目根目录解析
    full_path = os.path.join(PROJECT_DIR, file_path)
    return os.path.exists(full_path) and os.path.isfile(full_path)

def fix_file_paths():
    """修复文件路径处理问题"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有试卷
    cursor.execute("SELECT id, name, file_path FROM papers")
    papers = cursor.fetchall()
    total = len(papers)
    
    print_color(f"共找到 {total} 条试卷记录", BLUE)
    
    fixed_count = 0
    not_found_count = 0
    already_absolute_count = 0
    
    for i, paper in enumerate(papers):
        if i % 1000 == 0 or i == total - 1:
            print_color(f"处理进度: {i+1}/{total} ({(i+1)*100/total:.1f}%)", YELLOW)
        
        paper_id = paper['id']
        file_path = paper['file_path']
        
        if not file_path:
            not_found_count += 1
            continue
        
        # 如果已经是绝对路径且文件存在
        if os.path.isabs(file_path) and check_file_exists(file_path):
            already_absolute_count += 1
            continue
        
        # 尝试将相对路径转换为绝对路径
        absolute_path = os.path.join(PROJECT_DIR, file_path)
        
        # 检查文件是否存在
        if os.path.exists(absolute_path) and os.path.isfile(absolute_path):
            # 更新为绝对路径
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (absolute_path, paper_id))
            fixed_count += 1
        else:
            # 文件不存在，尝试其他查找方法
            search_dirs = [
                os.path.join(PROJECT_DIR, 'uploads', 'papers'),
                os.path.join(PROJECT_DIR, 'uploads'),
                os.path.join(PROJECT_DIR, 'static', 'uploads'),
                os.path.join(PROJECT_DIR, 'zujuanwang', 'uploads')
            ]
            
            found = False
            filename = os.path.basename(file_path)
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                    
                potential_path = os.path.join(search_dir, filename)
                if os.path.exists(potential_path) and os.path.isfile(potential_path):
                    cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (potential_path, paper_id))
                    fixed_count += 1
                    found = True
                    break
            
            if not found:
                not_found_count += 1
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print_color("\n===== 修复结果 =====", GREEN)
    print_color(f"总试卷数: {total}", BLUE)
    print_color(f"已修复路径: {fixed_count}", GREEN if fixed_count > 0 else YELLOW)
    print_color(f"已是绝对路径: {already_absolute_count}", GREEN if already_absolute_count > 0 else YELLOW)
    print_color(f"未找到文件: {not_found_count}", YELLOW if not_found_count > 0 else GREEN)
    
    if fixed_count > 0:
        print_color("\n✅ 修复完成！路径处理已更新为绝对路径", BOLD + GREEN)
    else:
        print_color("\n⚠️ 未发现需要修复的路径", YELLOW)
    
    return fixed_count

def main():
    """主函数"""
    print_color("=" * 80, GREEN)
    print_color(" 修复试卷文件路径处理 ", BOLD + GREEN)
    print_color("=" * 80, GREEN)
    print_color(f"项目目录: {PROJECT_DIR}")
    print_color(f"数据库路径: {DB_PATH}")
    print_color("=" * 80, GREEN)
    
    # 检查数据库是否存在
    if not os.path.exists(DB_PATH):
        print_color(f"错误: 数据库不存在 ({DB_PATH})", RED)
        return 1
    
    # 备份数据库
    backup_path = backup_database()
    
    # 修复文件路径
    fixed_count = fix_file_paths()
    
    print_color(f"数据库备份保存在: {backup_path}", BLUE)
    print_color("请重启应用程序以应用更改", YELLOW)
    print_color("=" * 80, GREEN)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
