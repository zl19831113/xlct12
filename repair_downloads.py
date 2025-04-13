#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复名校试卷下载功能
根据uploads目录中的文件，恢复下载功能
"""

import os
import sqlite3
import sys
import shutil
from datetime import datetime

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'  # 无颜色

# 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'uploads')
DB_PATH = os.path.join(PROJECT_DIR, 'instance', 'questions.db')

def print_color(message, color=None):
    """打印彩色文本"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)

def backup_file(filepath):
    """备份文件"""
    if os.path.exists(filepath):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = f"{filepath}.bak.{timestamp}"
        shutil.copy2(filepath, backup_path)
        print_color(f"已创建备份: {backup_path}", BLUE)
        return True
    return False

def get_file_stats():
    """获取文件统计信息"""
    if not os.path.exists(UPLOADS_DIR):
        print_color(f"错误: uploads目录不存在: {UPLOADS_DIR}", RED)
        return None

    file_exts = {}
    file_count = 0
    
    for root, _, files in os.walk(UPLOADS_DIR):
        for file in files:
            file_count += 1
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext in file_exts:
                file_exts[ext] += 1
            else:
                file_exts[ext] = 1
    
    return {
        'total_count': file_count,
        'by_extension': file_exts
    }

def update_database():
    """更新数据库中的文件路径"""
    if not os.path.exists(DB_PATH):
        print_color(f"错误: 数据库文件不存在: {DB_PATH}", RED)
        return False
    
    # 备份数据库
    backup_file(DB_PATH)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取uploads目录中的所有文件名
    upload_files = []
    for root, _, files in os.walk(UPLOADS_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), PROJECT_DIR)
            upload_files.append((file, rel_path))
    
    # 创建文件名到相对路径的映射
    file_map = {filename: path for filename, path in upload_files}
    
    print_color(f"在uploads目录中找到 {len(file_map)} 个文件", BLUE)
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, name, file_path FROM papers")
    papers = cursor.fetchall()
    print_color(f"数据库中有 {len(papers)} 条试卷记录", BLUE)
    
    # 更新文件路径
    updated_count = 0
    not_found_count = 0
    
    for paper_id, paper_name, file_path in papers:
        # 从原始路径中提取文件名
        if file_path:
            original_filename = os.path.basename(file_path)
            
            # 查找匹配的文件
            if original_filename in file_map:
                # 直接匹配
                new_path = file_map[original_filename]
                cursor.execute(
                    "UPDATE papers SET file_path = ? WHERE id = ?", 
                    (new_path, paper_id)
                )
                updated_count += 1
            else:
                # 尝试查找类似的文件（例如，忽略时间戳等）
                found = False
                
                # 1. 尝试匹配扩展名和部分名称
                base_name = os.path.splitext(original_filename)[0]
                name_parts = base_name.split('_')
                if len(name_parts) > 2:
                    # 可能有前缀编号或时间戳，取后面部分
                    search_term = '_'.join(name_parts[2:])
                    
                    for filename, path in upload_files:
                        if search_term in filename:
                            new_path = path
                            cursor.execute(
                                "UPDATE papers SET file_path = ? WHERE id = ?", 
                                (new_path, paper_id)
                            )
                            updated_count += 1
                            found = True
                            break
                
                if not found:
                    not_found_count += 1
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print_color(f"更新了 {updated_count} 条记录的文件路径", GREEN)
    print_color(f"有 {not_found_count} 条记录的文件未找到匹配", YELLOW)
    
    return True

def fix_app_code():
    """修复app.py中的潜在问题"""
    app_path = os.path.join(PROJECT_DIR, 'app.py')
    
    if not os.path.exists(app_path):
        print_color(f"错误: app.py不存在: {app_path}", RED)
        return False
    
    # 备份app.py
    backup_file(app_path)
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 检查代码逻辑错误(代码写在return后)
    fixed_content = []
    original_lines = content.split('\n')
    in_download_func = False
    after_return = False
    accumulated_lines = []
    
    for line in original_lines:
        if 'def download_paper(' in line:
            in_download_func = True
            fixed_content.append(line)
        elif in_download_func and ('return send_file(' in line or 'return send_from_directory(' in line):
            after_return = True
            fixed_content.append(line)
        elif in_download_func and after_return and line.strip() and not (line.strip().startswith('#') or line.strip() == ''):
            if line.startswith('        '):  # 这是函数内代码，但在return后
                accumulated_lines.append(line)
            else:  # 这可能是新函数或其他内容
                after_return = False
                in_download_func = False
                fixed_content.append(line)
        else:
            fixed_content.append(line)
    
    if accumulated_lines:
        print_color("检测到app.py中有代码写在return语句之后，这部分代码永远不会执行", RED)
        print_color("已移除这部分代码", BLUE)
    
    # 修复2: 确保文件路径搜索逻辑正确
    fixed_content_str = '\n'.join(fixed_content)
    
    if 'potential_paths' in fixed_content_str and 'os.path.join(upload_folder, file_name)' in fixed_content_str:
        # 确保有正确的文件搜索路径
        if 'uploads' not in fixed_content_str or 'os.path.join(project_root, \'uploads\', file_name)' not in fixed_content_str:
            # 需要添加直接指向uploads目录的路径
            insertion_point = fixed_content_str.find('potential_paths = [')
            if insertion_point != -1:
                # 找到插入点的行号
                line_num = fixed_content_str[:insertion_point].count('\n')
                
                # 在potential_paths列表中添加新路径
                new_path = "\n            # 新增: 直接从uploads目录查找\n            os.path.join(project_root, 'uploads', file_name),"
                
                # 重建fixed_content数组
                fixed_content = fixed_content_str.split('\n')
                
                # 在适当位置插入新路径
                indentation = '            '  # 假设缩进是4个空格
                for i in range(line_num + 1, len(fixed_content)):
                    if indentation + ']' in fixed_content[i]:
                        # 找到列表结束，在之前插入
                        fixed_content.insert(i, indentation + "# 新增: 直接从uploads目录查找")
                        fixed_content.insert(i + 1, indentation + "os.path.join(project_root, 'uploads', file_name),")
                        break
    
    # 写回修改后的内容
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_content))
    
    print_color("app.py修复完成", GREEN)
    return True

def check_directory_structure():
    """检查并创建必要的目录结构"""
    directories = [
        UPLOADS_DIR,
        os.path.join(PROJECT_DIR, 'static', 'uploads'),
        os.path.join(PROJECT_DIR, 'instance')
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print_color(f"创建目录: {directory}", BLUE)

def main():
    """主函数"""
    print_color("=" * 80, GREEN)
    print_color("名校试卷下载功能修复工具", BOLD + GREEN)
    print_color("=" * 80, GREEN)
    print_color(f"项目目录: {PROJECT_DIR}")
    print_color(f"上传目录: {UPLOADS_DIR}")
    print_color(f"数据库路径: {DB_PATH}")
    print_color("=" * 80, GREEN)
    
    # 检查目录结构
    check_directory_structure()
    
    # 获取文件统计信息
    stats = get_file_stats()
    if stats:
        print_color(f"uploads目录中共有 {stats['total_count']} 个文件", BLUE)
        print_color("文件类型统计:", BLUE)
        for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True):
            print_color(f"  {ext}: {count} 个文件", BLUE)
    
    # 修复app.py代码
    if fix_app_code():
        print_color("app.py代码已修复", GREEN)
    
    # 更新数据库
    if update_database():
        print_color("数据库已更新", GREEN)
    
    print_color("=" * 80, GREEN)
    print_color("修复完成! 现在您应该可以正常下载名校试卷了。", BOLD + GREEN)
    print_color("请重启应用程序以使更改生效。", YELLOW)
    print_color("=" * 80, GREEN)

if __name__ == "__main__":
    main()
