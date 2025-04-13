#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清除缺失文件的试卷记录
功能：从数据库中删除没有对应文件的试卷记录
"""

import os
import sqlite3
import shutil
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('clean_papers.log')
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
    backup_path = f"{DB_PATH}.clean_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"已创建数据库备份: {backup_path}")
    print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    return backup_path

def clean_missing_papers(dry_run=True):
    """清除缺失文件的试卷记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, name, subject, file_path FROM papers")
    papers = cursor.fetchall()
    
    total_records = len(papers)
    logger.info(f"找到 {total_records} 条试卷记录")
    print(f"\n{GREEN}找到 {total_records} 条试卷记录{NC}")
    
    # 统计变量
    missing_files = 0
    to_delete = []
    
    # 检查每条记录
    for paper_id, name, subject, file_path in papers:
        # 构建完整文件路径
        full_path = os.path.join(PROJECT_ROOT, file_path) if file_path else None
        
        # 检查文件是否存在
        if not full_path or not os.path.exists(full_path):
            missing_files += 1
            to_delete.append((paper_id, name, subject))
            
            # 记录到日志
            logger.info(f"缺失文件: ID={paper_id}, 科目={subject}, 名称={name}, 路径={file_path}")
            
            # 每100条显示一次进度
            if missing_files % 100 == 0:
                print(f"{BLUE}已找到 {missing_files} 条缺失文件记录...{NC}")
    
    print(f"\n{YELLOW}发现 {missing_files} 条缺失文件的记录{NC}")
    logger.info(f"发现 {missing_files} 条缺失文件的记录")
    
    # 如果是演习模式，仅显示而不删除
    if dry_run:
        print(f"{YELLOW}[演习模式] 以下记录将被删除 (实际未删除):{NC}")
        for i, (paper_id, name, subject) in enumerate(to_delete[:10]):
            print(f"{i+1}. ID={paper_id}, 科目={subject}, 名称={name}")
        
        if len(to_delete) > 10:
            print(f"... 以及 {len(to_delete) - 10} 条其他记录")
        
        print(f"\n{GREEN}演习模式已完成，没有实际删除任何记录。{NC}")
        print(f"{YELLOW}要实际删除这些记录，请运行:{NC}")
        print(f"python3 clean_missing_papers.py --confirm")
    else:
        # 实际删除记录
        if missing_files > 0:
            # 创建删除记录的SQL查询
            paper_ids = [paper_id for paper_id, _, _ in to_delete]
            placeholders = ','.join(['?'] * len(paper_ids))
            cursor.execute(f"DELETE FROM papers WHERE id IN ({placeholders})", paper_ids)
            
            # 提交更改
            conn.commit()
            
            print(f"\n{GREEN}成功删除 {missing_files} 条缺失文件的记录{NC}")
            logger.info(f"成功删除 {missing_files} 条缺失文件的记录")
        else:
            print(f"\n{GREEN}没有发现缺失文件的记录，无需清理{NC}")
            logger.info("没有发现缺失文件的记录，无需清理")
    
    conn.close()
    
    return missing_files

def main():
    """主函数"""
    import sys
    
    # 检查是否确认执行
    confirm = len(sys.argv) > 1 and sys.argv[1] == '--confirm'
    
    print(f"\n{GREEN}===== 清除缺失文件的试卷记录 ====={NC}")
    
    if not confirm:
        print(f"{YELLOW}[演习模式] 将只显示要删除的记录，不会实际删除。{NC}")
        print(f"{YELLOW}如需实际删除，请添加 --confirm 参数{NC}\n")
    else:
        print(f"{RED}[执行模式] 将实际删除缺失文件的记录！{NC}\n")
        
        # 备份数据库
        backup_path = backup_database()
        print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    
    # 清除缺失文件的记录
    missing_count = clean_missing_papers(dry_run=not confirm)
    
    if confirm and missing_count > 0:
        print(f"\n{GREEN}清理完成!{NC}")
        print(f"{YELLOW}已备份数据库，请重启应用以应用更改{NC}")
    
    if not confirm and missing_count > 0:
        print(f"\n{YELLOW}要确认删除这些记录，请运行:{NC}")
        print(f"python3 clean_missing_papers.py --confirm")

if __name__ == "__main__":
    main() 