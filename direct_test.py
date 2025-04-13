#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试脚本
功能：直接从数据库获取试卷记录并验证文件是否存在和是否匹配
"""

import os
import sqlite3
import re
import random
import shutil
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 颜色定义
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# 科目关键词映射
SUBJECT_KEYWORDS = {
    '语文': ['语文'],
    '数学': ['数学', '文数', '理数'],
    '英语': ['英语'],
    '物理': ['物理'],
    '化学': ['化学'],
    '生物': ['生物'],
    '政治': ['政治', '思想政治'],
    '历史': ['历史'],
    '地理': ['地理'],
    '文综': ['文综'],
    '理综': ['理综']
}

def main():
    """主函数"""
    print(f"\n{GREEN}===== 直接测试脚本 ====={NC}")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, subject, name, file_path FROM papers LIMIT 10")
    papers = cursor.fetchall()
    
    print(f"\n{YELLOW}获取到 {len(papers)} 条试卷记录{NC}")
    
    for paper in papers:
        paper_id, subject, name, file_path = paper
        
        print(f"\n{BLUE}试卷ID: {paper_id}{NC}")
        print(f"名称: {name}")
        print(f"科目: {subject}")
        print(f"文件路径: {file_path}")
        
        # 构建完整文件路径
        full_path = os.path.join(PROJECT_ROOT, file_path) if file_path else None
        
        # 检查文件是否存在
        if full_path and os.path.exists(full_path):
            print(f"{GREEN}✓ 文件存在{NC}")
            
            # 检查文件名是否包含科目关键词
            filename = os.path.basename(full_path)
            keywords = SUBJECT_KEYWORDS.get(subject, [subject])
            
            matched = False
            for keyword in keywords:
                if keyword in filename or keyword in name:
                    matched = True
                    print(f"{GREEN}✓ 文件名包含科目关键词: {keyword}{NC}")
                    break
            
            if not matched:
                print(f"{RED}✗ 文件名不包含科目关键词{NC}")
                
                # 检查是否包含其他科目的关键词
                for other_subject, other_keywords in SUBJECT_KEYWORDS.items():
                    if other_subject == subject:
                        continue
                    
                    for keyword in other_keywords:
                        if keyword in filename:
                            print(f"{RED}✗ 文件名包含其他科目关键词: {keyword} (科目: {other_subject}){NC}")
                            break
        else:
            print(f"{RED}✗ 文件不存在: {full_path}{NC}")
    
    # 查看实际下载路径处理流程
    print(f"\n{YELLOW}===== 检查下载逻辑 ====={NC}")
    
    # 查找app.py中download_paper函数的实际实现
    app_py_path = os.path.join(PROJECT_ROOT, 'app.py')
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 查找下载函数的定义
            download_func_match = re.search(r'@app\.route\(\'/download_paper/<int:paper_id>\'\)\s*def\s+download_paper\(paper_id\):(.*?)(?=@app\.route|\Z)', content, re.DOTALL)
            if download_func_match:
                download_func = download_func_match.group(1).strip()
                print(f"{GREEN}找到下载函数定义:{NC}")
                print(download_func[:200] + "..." if len(download_func) > 200 else download_func)
                
                # 检查是否有硬编码路径或特殊处理
                if 'find_actual_file_location' in download_func:
                    print(f"{RED}注意: 下载函数使用了find_actual_file_location函数，这可能会覆盖数据库中的路径{NC}")
                
                if 'special_handling' in download_func:
                    print(f"{RED}注意: 下载函数包含special_handling特殊处理逻辑{NC}")
                
                if 'file_path != rel_path' in download_func:
                    print(f"{RED}注意: 下载函数动态修改了数据库中的file_path{NC}")
            else:
                print(f"{RED}未找到download_paper函数定义{NC}")
                
            # 查找是否有其他可能干扰下载的代码
            find_file_match = re.search(r'def\s+find_actual_file_location\(.*?\):(.*?)(?=def|\Z)', content, re.DOTALL)
            if find_file_match:
                find_file_func = find_file_match.group(1).strip()
                print(f"\n{YELLOW}发现find_actual_file_location函数:{NC}")
                print(find_file_func[:200] + "..." if len(find_file_func) > 200 else find_file_func)
    else:
        print(f"{RED}未找到app.py文件{NC}")
    
    # 检查是否有多个进程或服务
    print(f"\n{YELLOW}===== 检查运行中的进程 ====={NC}")
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux', '|', 'grep', 'python'], shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
    except Exception as e:
        print(f"{RED}检查进程时出错: {str(e)}{NC}")
    
    # 关闭数据库连接
    conn.close()
    print(f"\n{GREEN}测试完成！{NC}")

if __name__ == "__main__":
    main() 