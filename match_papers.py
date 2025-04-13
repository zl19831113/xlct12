#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
匹配数据库记录与实际文件，解决ID更改后的文件对应问题
"""

import os
import sqlite3
import re
from collections import defaultdict
import time

# 配置
DB_PATH = 'instance/questions.db'
PAPERS_DIR = 'uploads/papers'
LOG_FILE = 'paper_matching_results.log'

def get_file_key(filename):
    """
    从文件名提取关键匹配信息，移除ID部分
    格式：[时间戳]_[ID]_[文件描述].扩展名
    返回: ([时间戳], [文件描述], 扩展名)
    """
    # 匹配模式：时间戳_数字_描述.扩展名
    match = re.match(r'(\d+)_(\d+)_(.+)\.([^.]+)$', filename)
    if match:
        timestamp, _, description, extension = match.groups()
        return (timestamp, description, extension)
    return None

def log_message(message, also_print=True):
    """记录消息到日志文件"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    if also_print:
        print(message)

def main():
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有记录
    cursor.execute('SELECT id, file_path, name FROM papers')
    db_records = cursor.fetchall()
    
    log_message(f"数据库中共有 {len(db_records)} 条记录")
    
    # 创建数据库记录索引
    db_files = {}  # file_path -> (id, name)
    for record_id, file_path, name in db_records:
        db_files[file_path] = (record_id, name)
    
    # 获取所有实际文件
    actual_files = []
    for root, _, files in os.walk(PAPERS_DIR):
        for file in files:
            actual_files.append(os.path.join(root, file))
    
    log_message(f"文件系统中共有 {len(actual_files)} 个文件")
    
    # 检查文件是否存在
    missing_files = []
    for file_path in db_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    log_message(f"有 {len(missing_files)} 条记录的文件不存在")
    
    # 索引实际文件
    actual_file_index = defaultdict(list)
    for file_path in actual_files:
        filename = os.path.basename(file_path)
        key = get_file_key(filename)
        if key:
            actual_file_index[key].append(file_path)
    
    # 尝试匹配缺失文件
    potential_matches = 0
    matched_files = 0
    update_queries = []
    
    for missing_path in missing_files:
        filename = os.path.basename(missing_path)
        key = get_file_key(filename)
        
        if not key:
            continue
        
        if key in actual_file_index:
            matches = actual_file_index[key]
            if len(matches) == 1:
                # 唯一匹配
                new_path = matches[0]
                record_id = db_files[missing_path][0]
                update_queries.append((new_path, record_id))
                matched_files += 1
                log_message(f"找到匹配: {missing_path} -> {new_path}", False)
            else:
                # 多个潜在匹配
                potential_matches += 1
                log_message(f"多个潜在匹配 ({len(matches)}) 对于: {missing_path}", False)
    
    log_message(f"找到 {matched_files} 个确定匹配，{potential_matches} 个潜在多匹配")
    
    # 更新数据库
    if update_queries and input("要更新数据库吗? (y/n): ").lower() == 'y':
        # 先备份数据库
        log_message("正在备份数据库...")
        backup_time = time.strftime('%Y%m%d%H%M%S')
        os.system(f"cp {DB_PATH} {DB_PATH}.bak_{backup_time}")
        
        # 执行更新
        for new_path, record_id in update_queries:
            cursor.execute('UPDATE papers SET file_path = ? WHERE id = ?', (new_path, record_id))
        
        conn.commit()
        log_message(f"已更新 {len(update_queries)} 条记录")
    
    conn.close()
    log_message("完成")

if __name__ == "__main__":
    main()
