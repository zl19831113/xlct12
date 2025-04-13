#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import shutil
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'file_association_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# 配置
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'xlct12.db')
PAPERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'papers')
BACKUP_DB_PATH = f'{DB_PATH}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
DRY_RUN = False  # 执行实际修复操作

# 创建数据库备份
def backup_database():
    logging.info(f"正在创建数据库备份: {BACKUP_DB_PATH}")
    shutil.copy2(DB_PATH, BACKUP_DB_PATH)
    logging.info(f"数据库备份完成")

# 获取数据库中的所有记录
def get_db_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_path FROM papers")
    records = cursor.fetchall()
    conn.close()
    return records

# 获取文件系统中的所有文件
def get_filesystem_files():
    files = []
    for root, _, filenames in os.walk(PAPERS_DIR):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, os.path.dirname(os.path.abspath(__file__)))
            files.append((filename, full_path, rel_path))
    return files

# 从文件名中提取一个"规范化"版本用于匹配
def normalize_filename(filename):
    # 去除扩展名
    base_name = os.path.splitext(filename)[0]
    
    # 去除所有非字母数字字符
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', base_name)
    
    # 如果是日期格式文件名，提取日期部分
    date_match = re.search(r'(\d{8}|\d{4}\d{2}\d{2})', clean_name)
    if date_match:
        date_part = date_match.group(1)
        # 保留日期部分及之后的内容
        idx = clean_name.find(date_part)
        if idx >= 0:
            clean_name = clean_name[idx:]
    
    return clean_name.lower()

# 智能匹配数据库记录和文件系统文件
def find_matches(db_records, fs_files):
    # 创建文件系统文件的查找映射
    fs_file_map = {}
    for filename, full_path, rel_path in fs_files:
        norm_name = normalize_filename(filename)
        if norm_name not in fs_file_map:
            fs_file_map[norm_name] = []
        fs_file_map[norm_name].append((filename, full_path, rel_path))
    
    matches = []
    no_matches = []
    
    logging.info(f"开始匹配 {len(db_records)} 条数据库记录...")
    
    for record_id, name, file_path in db_records:
        db_filename = os.path.basename(file_path)
        norm_db_name = normalize_filename(db_filename)
        
        # 尝试直接匹配规范化名称
        found = False
        if norm_db_name in fs_file_map:
            for filename, full_path, rel_path in fs_file_map[norm_db_name]:
                matches.append((record_id, name, file_path, filename, full_path, rel_path))
                found = True
                break
        
        # 如果没有找到，尝试更宽松的匹配
        if not found:
            # 提取日期部分（假设格式相似）
            date_match = re.search(r'(\d{8}|\d{4}\d{2}\d{2})', norm_db_name)
            
            if date_match:
                date_part = date_match.group(1)
                
                for norm_fs_name, files in fs_file_map.items():
                    if date_part in norm_fs_name:
                        filename, full_path, rel_path = files[0]
                        matches.append((record_id, name, file_path, filename, full_path, rel_path))
                        found = True
                        break
        
        if not found:
            no_matches.append((record_id, name, file_path))
    
    return matches, no_matches

# 更新数据库记录
def update_database_records(matches):
    if DRY_RUN:
        logging.info("模拟模式：以下是将要执行的数据库更新")
        for record_id, _, db_path, _, _, new_rel_path in matches[:10]:
            logging.info(f"ID {record_id}: {db_path} -> {new_rel_path}")
        if len(matches) > 10:
            logging.info(f"... 以及 {len(matches)-10} 条更多记录")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    for record_id, _, _, _, _, new_rel_path in matches:
        cursor.execute(
            "UPDATE papers SET file_path = ? WHERE id = ?", 
            (new_rel_path, record_id)
        )
        updated += 1
        
        # 定期提交以避免锁定问题
        if updated % 1000 == 0:
            conn.commit()
            logging.info(f"已更新 {updated} 条记录...")
    
    conn.commit()
    conn.close()
    logging.info(f"数据库更新完成，共更新 {updated} 条记录")

# 主函数
def main():
    logging.info("开始修复文件关联...")
    logging.info(f"数据库路径：{DB_PATH}")
    logging.info(f"文件目录：{PAPERS_DIR}")
    logging.info(f"模拟运行：{DRY_RUN}")
    
    # 备份数据库
    backup_database()
    
    # 获取数据
    db_records = get_db_records()
    logging.info(f"共加载 {len(db_records)} 条数据库记录")
    
    fs_files = get_filesystem_files()
    logging.info(f"共发现 {len(fs_files)} 个文件系统文件")
    
    # 匹配文件
    matches, no_matches = find_matches(db_records, fs_files)
    logging.info(f"找到 {len(matches)} 条匹配记录")
    logging.info(f"有 {len(no_matches)} 条记录无法匹配")
    
    # 显示前几个无法匹配的记录
    if no_matches:
        logging.info("无法匹配的记录示例:")
        for record_id, name, file_path in no_matches[:5]:
            logging.info(f"ID {record_id}: {name} - {file_path}")
    
    # 更新数据库
    if matches:
        if DRY_RUN:
            logging.info("这是一次模拟运行，未执行实际更改")
            logging.info("若要执行实际更改，请将脚本中的 DRY_RUN 设置为 False")
        else:
            update_database_records(matches)
    
    logging.info("处理完成！")

if __name__ == "__main__":
    main()
