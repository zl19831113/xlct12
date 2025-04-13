#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件路径冲突修复工具
功能：检测并修复数据库中多个试卷记录共享同一个文件路径的问题
"""

import os
import sqlite3
import shutil
from datetime import datetime
import logging
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('path_conflicts.log')
    ]
)
logger = logging.getLogger(__name__)

# 颜色定义 (终端输出)
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.conflicts_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"已创建数据库备份: {backup_path}")
    print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    return backup_path

def find_conflicting_paths():
    """查找数据库中有冲突的文件路径"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询所有试卷记录
    cursor.execute("SELECT id, name, subject, file_path FROM papers")
    papers = cursor.fetchall()
    
    # 按文件路径分组
    path_groups = defaultdict(list)
    for paper_id, name, subject, file_path in papers:
        if file_path:  # 忽略空路径
            path_groups[file_path].append((paper_id, name, subject))
    
    # 筛选出有冲突的路径
    conflicts = {path: papers for path, papers in path_groups.items() if len(papers) > 1}
    
    conn.close()
    return conflicts

def fix_conflicting_paths(dry_run=True):
    """修复冲突的文件路径"""
    conflicts = find_conflicting_paths()
    
    total_conflicts = len(conflicts)
    total_papers = sum(len(papers) for papers in conflicts.values())
    
    print(f"{GREEN}发现 {total_conflicts} 个冲突路径，涉及 {total_papers} 个试卷记录{NC}")
    
    if total_conflicts == 0:
        print(f"{GREEN}没有发现冲突的文件路径，无需修复{NC}")
        return
    
    # 打印冲突信息
    print(f"\n{YELLOW}冲突路径列表:{NC}")
    for i, (path, papers) in enumerate(conflicts.items(), 1):
        print(f"{i}. 路径: {path}")
        print(f"   共享此路径的试卷 ({len(papers)}):")
        for j, (paper_id, name, subject) in enumerate(papers, 1):
            print(f"   {j}) ID: {paper_id}, 科目: {subject}, 名称: {name}")
        print()
    
    if dry_run:
        print(f"{YELLOW}[演习模式] 上述是将被修复的路径冲突。{NC}")
        print(f"{YELLOW}要实际修复这些冲突，请运行:{NC}")
        print(f"python3 fix_conflicting_paths.py --confirm")
        return
    
    # 执行修复
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    fixed_count = 0
    
    for path, papers in conflicts.items():
        print(f"{BLUE}正在修复路径: {path}{NC}")
        
        # 检查文件是否实际存在
        full_path = os.path.join(PROJECT_ROOT, path)
        file_exists = os.path.exists(full_path)
        
        if file_exists:
            # 如果文件存在，保留第一个试卷的路径，为其他试卷创建新路径
            keep_paper = papers[0]
            conflict_papers = papers[1:]
            
            print(f"  保留 ID: {keep_paper[0]} ({keep_paper[2]} - {keep_paper[1]}) 的原始路径")
            
            for paper_id, name, subject in conflict_papers:
                # 检查试卷名称中是否包含年份
                year_match = None
                for year_str in ["2021", "2022", "2023", "2024", "2025"]:
                    if year_str in name:
                        year_match = year_str
                        break
                
                # 获取文件扩展名
                _, ext = os.path.splitext(path)
                
                # 生成新的相对文件路径
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = f"{timestamp}_{paper_id}_{year_match if year_match else ''}{ext}"
                new_path = os.path.join(os.path.dirname(path), new_filename)
                
                # 标记为需要找到合适的文件
                cursor.execute(
                    "UPDATE papers SET file_path = ? WHERE id = ?", 
                    (new_path, paper_id)
                )
                
                print(f"  更新 ID: {paper_id} ({subject} - {name}) 的路径为: {new_path}")
                fixed_count += 1
        else:
            # 如果文件不存在，为每个试卷生成新路径
            print(f"  {RED}警告: 文件不存在: {full_path}{NC}")
            
            for paper_id, name, subject in papers:
                # 检查试卷名称中是否包含年份
                year_match = None
                for year_str in ["2021", "2022", "2023", "2024", "2025"]:
                    if year_str in name:
                        year_match = year_str
                        break
                
                # 获取文件扩展名
                _, ext = os.path.splitext(path)
                
                # 生成新的相对文件路径
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                new_filename = f"{timestamp}_{paper_id}_{year_match if year_match else ''}{ext}"
                new_path = os.path.join(os.path.dirname(path), new_filename)
                
                # 标记为需要找到合适的文件
                cursor.execute(
                    "UPDATE papers SET file_path = ? WHERE id = ?", 
                    (new_path, paper_id)
                )
                
                print(f"  更新 ID: {paper_id} ({subject} - {name}) 的路径为: {new_path}")
                fixed_count += 1
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n{GREEN}修复完成!{NC}")
    print(f"已修复 {fixed_count} 个冲突记录")
    print(f"{YELLOW}注意: 这些试卷记录现在有了新的文件路径，但实际文件尚未创建。{NC}")
    print(f"{YELLOW}请使用管理功能上传实际文件，或运行 fix_paper_matches.py 尝试自动配对文件。{NC}")

def main():
    """主函数"""
    import sys
    
    # 检查是否确认执行
    confirm = len(sys.argv) > 1 and sys.argv[1] == '--confirm'
    
    print(f"\n{GREEN}===== 文件路径冲突修复工具 ====={NC}")
    
    # 查找冲突的文件路径
    conflicts = find_conflicting_paths()
    total_conflicts = len(conflicts)
    
    if total_conflicts == 0:
        print(f"{GREEN}没有发现冲突的文件路径，无需修复{NC}")
        return
    
    if not confirm:
        print(f"{YELLOW}[演习模式] 将只显示要修复的冲突，不会实际操作。{NC}")
        print(f"{YELLOW}如需实际修复，请添加 --confirm 参数{NC}\n")
    else:
        print(f"{RED}[执行模式] 将实际修复冲突的文件路径！{NC}\n")
        
        # 备份数据库
        backup_path = backup_database()
        print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    
    # 修复冲突的路径
    fix_conflicting_paths(dry_run=not confirm)

if __name__ == "__main__":
    main() 