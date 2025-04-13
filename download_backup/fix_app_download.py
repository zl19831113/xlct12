#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
试卷下载功能修复工具
创建时间: 2025-03-29
"""

import os
import sqlite3
import sys
from pprint import pprint
import shutil

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # 无颜色

def print_colored(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{NC}")

def get_project_dir():
    """获取项目目录"""
    return os.path.dirname(os.path.abspath(__file__))

def connect_db():
    """连接数据库"""
    project_dir = get_project_dir()
    db_path = os.path.join(project_dir, 'instance', 'questions.db')
    print_colored(f"数据库路径: {db_path}", BLUE)
    return sqlite3.connect(db_path)

def check_file_path_exists(path):
    """检查文件是否存在"""
    if not path:
        return False, "路径为空"
    
    project_dir = get_project_dir()
    
    # 尝试不同的解析方式
    paths_to_check = []
    
    # 1. 直接检查路径
    paths_to_check.append((path, "原始路径"))
    
    # 2. 如果不是绝对路径，从项目根目录解析
    if not os.path.isabs(path):
        paths_to_check.append((os.path.join(project_dir, path), "项目根目录相对路径"))
    
    # 3. 尝试使用upload_folder作为基础路径
    upload_folder = os.path.join(project_dir, 'uploads', 'papers')
    filename = os.path.basename(path)
    paths_to_check.append((os.path.join(upload_folder, filename), "uploads/papers相对路径"))
    
    # 4. 尝试查找static/uploads路径
    static_upload = os.path.join(project_dir, 'static', 'uploads', 'papers')
    paths_to_check.append((os.path.join(static_upload, filename), "static/uploads/papers相对路径"))
    
    for full_path, path_type in paths_to_check:
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return True, f"✓ 文件存在: {full_path} ({path_type})"
    
    return False, f"✗ 文件不存在: 已尝试 {len(paths_to_check)} 种可能的路径"

def test_paper_download(paper_id=None):
    """测试试卷下载功能"""
    conn = connect_db()
    cursor = conn.cursor()
    
    if paper_id:
        cursor.execute("SELECT id, name, file_path FROM papers WHERE id = ?", (paper_id,))
        papers = cursor.fetchall()
    else:
        cursor.execute("SELECT id, name, file_path FROM papers LIMIT 10")
        papers = cursor.fetchall()
    
    print_colored(f"测试 {len(papers)} 条试卷记录的可下载性", YELLOW)
    print("=" * 80)
    
    for paper_id, paper_name, file_path in papers:
        print(f"试卷 #{paper_id}: {paper_name}")
        print(f"文件路径: {file_path}")
        exists, message = check_file_path_exists(file_path)
        if exists:
            print_colored(message, GREEN)
        else:
            print_colored(message, RED)
        print("-" * 80)
    
    conn.close()

def fix_app_code():
    """修复app.py中的代码问题"""
    project_dir = get_project_dir()
    app_path = os.path.join(project_dir, 'app.py')
    
    print_colored("修复app.py中的代码问题", YELLOW)
    
    # 创建备份
    backup_path = f"{app_path}.backup.{os.getpid()}"
    shutil.copy2(app_path, backup_path)
    print_colored(f"已创建备份: {backup_path}", BLUE)
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查下载函数中的逻辑问题 (代码写在return后面)
    if "# 过滤掉None值" in content and "return send_file(" in content:
        # 检测问题模式: 在return语句后有代码
        lines = content.split('\n')
        fixed_content = []
        in_download_func = False
        seen_return = False
        code_after_return = []
        
        for line in lines:
            if "def download_paper(" in line:
                in_download_func = True
                fixed_content.append(line)
            elif in_download_func and "return send_file(" in line:
                seen_return = True
                fixed_content.append(line)
            elif in_download_func and seen_return and line.strip() and not line.startswith('#'):
                if "# 过滤掉None值" in line or "# 检查每个可能的路径" in line:
                    code_after_return.append(line)
                elif line.startswith('        ') and not line.startswith('            '):
                    # 这是函数内的代码，但在return之后
                    code_after_return.append(line)
                else:
                    # 可能是新函数或其他代码
                    fixed_content.append(line)
                    in_download_func = False
                    seen_return = False
            else:
                fixed_content.append(line)
        
        if code_after_return:
            print_colored("检测到下载函数中有代码写在return语句之后，这些代码永远不会执行:", RED)
            for line in code_after_return:
                print(f"  {line}")
            
            print_colored("是否要修复此问题? (y/n)", YELLOW)
            choice = input().lower()
            
            if choice == 'y':
                # 重新组织代码，将return后的代码移到函数前面适当的位置
                fixed_content = []
                in_download_func = False
                found_potential_paths = False
                
                for line in lines:
                    if "def download_paper(" in line:
                        in_download_func = True
                        fixed_content.append(line)
                    elif in_download_func and "# 检查每个可能的路径" in line:
                        # 已经处理过这段代码了，跳过
                        pass
                    elif in_download_func and "# 确保占位符文件存在" in line:
                        # 确保在创建占位符文件前已过滤掉None值并检查了路径
                        if not found_potential_paths:
                            for fix_line in code_after_return:
                                fixed_content.append(fix_line)
                            found_potential_paths = True
                        fixed_content.append(line)
                    elif in_download_func and "return send_file(" in line and "tmp_file_path" in line:
                        fixed_content.append(line)
                        in_download_func = False
                    elif line.strip() and not in_download_func:
                        fixed_content.append(line)
                    else:
                        fixed_content.append(line)
                
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fixed_content))
                
                print_colored("✓ 已修复app.py中的代码问题", GREEN)
            else:
                print_colored("未修改app.py文件", BLUE)
    else:
        print_colored("未检测到app.py中有明显的代码问题", BLUE)

def check_known_issues():
    """检查已知问题"""
    project_dir = get_project_dir()
    static_path = os.path.join(project_dir, 'static')
    
    print_colored("检查已知问题", YELLOW)
    
    # 检查存放试卷的目录权限
    dirs_to_check = [
        os.path.join(project_dir, 'uploads'),
        os.path.join(project_dir, 'uploads', 'papers'),
        os.path.join(project_dir, 'static', 'uploads'),
        os.path.join(project_dir, 'static', 'uploads', 'papers'),
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            mode = oct(os.stat(dir_path).st_mode)[-3:]
            if mode != '755' and mode != '777':
                print_colored(f"目录权限不是755或777: {dir_path} (当前: {mode})", YELLOW)
                print_colored(f"  建议运行: chmod -R 755 {dir_path}", BLUE)
        else:
            print_colored(f"目录不存在: {dir_path}", RED)
            print_colored(f"  建议运行: mkdir -p {dir_path}", BLUE)
    
    # 检查tmp_file_path是否可写
    tmp_file_path = os.path.join(project_dir, 'static', 'tmp_paper.txt')
    tmp_dir = os.path.dirname(tmp_file_path)
    
    if not os.path.exists(tmp_dir):
        print_colored(f"临时文件目录不存在: {tmp_dir}", RED)
        print_colored(f"  建议运行: mkdir -p {tmp_dir}", BLUE)
    elif not os.access(tmp_dir, os.W_OK):
        print_colored(f"无法写入临时文件目录: {tmp_dir}", RED)
        print_colored(f"  建议运行: chmod 755 {tmp_dir}", BLUE)

def main():
    """主函数"""
    print_colored("=" * 80, GREEN)
    print_colored("试卷下载功能修复工具", GREEN)
    print_colored("=" * 80, GREEN)
    
    print("请选择操作:")
    print("1. 检查试卷文件是否存在")
    print("2. 修复app.py中的代码问题")
    print("3. 检查已知问题")
    print("4. 全部执行")
    print("q. 退出")
    
    choice = input("> ")
    
    if choice == '1':
        paper_id = input("请输入试卷ID (留空则检查前10条记录): ")
        if paper_id.strip():
            test_paper_download(int(paper_id))
        else:
            test_paper_download()
    elif choice == '2':
        fix_app_code()
    elif choice == '3':
        check_known_issues()
    elif choice == '4':
        test_paper_download()
        fix_app_code()
        check_known_issues()
    elif choice.lower() == 'q':
        sys.exit(0)
    else:
        print_colored("无效选择", RED)

if __name__ == "__main__":
    main()
