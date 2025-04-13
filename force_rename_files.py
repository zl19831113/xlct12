#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import shutil
import re
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'force_rename_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# 配置 - 使用绝对路径
DB_PATH = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/instance/xlct12.db"
PAPERS_DIR = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/papers"
BACKUP_DIR = f"/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 创建备份
def create_backup():
    logging.info(f"跳过完整备份，仅重命名文件")
    # 不执行完整备份，分时繁琐
    return

# 获取数据库中的文件记录
def get_db_files():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_path FROM papers")
    result = cursor.fetchall()
    conn.close()
    
    # 提取文件名
    db_files = {}
    for record_id, file_path in result:
        filename = os.path.basename(file_path)
        # 用规范化名称作为键以便于匹配
        norm_name = normalize_for_matching(filename)
        db_files[norm_name] = (record_id, filename)
    
    logging.info(f"从数据库加载了 {len(db_files)} 条记录")
    return db_files

# 规范化文件名以便匹配
def normalize_for_matching(filename):
    # 移除扩展名
    base_name = os.path.splitext(filename)[0]
    # 移除所有非字母数字字符
    return re.sub(r'[^a-zA-Z0-9]', '', base_name).lower()

# 强制重命名文件
def force_rename_files():
    # 获取数据库文件记录
    db_files = get_db_files()
    
    # 获取文件系统中的所有文件
    renamed_count = 0
    skipped_count = 0
    not_found_count = 0
    
    # 两阶段处理:
    # 1. 先构建映射关系
    file_mapping = {}
    
    # 递归处理 PAPERS_DIR 及其子目录中的所有文件
    if os.path.exists(PAPERS_DIR) and os.path.isdir(PAPERS_DIR):
        total_files = 0
        
        # 首先处理根目录中的文件
        root_files = [f for f in os.listdir(PAPERS_DIR) if os.path.isfile(os.path.join(PAPERS_DIR, f))]
        logging.info(f"在 {PAPERS_DIR} 根目录下找到 {len(root_files)} 个文件")
        total_files += len(root_files)
        
        for filename in root_files:
            norm_name = normalize_for_matching(filename)
            full_path = os.path.join(PAPERS_DIR, filename)
            
            if norm_name not in file_mapping:
                file_mapping[norm_name] = []
            file_mapping[norm_name].append((filename, full_path))
        
        # 专门处理 papers/papers 子目录（关键目录）
        papers_subdir = os.path.join(PAPERS_DIR, 'papers')
        if os.path.exists(papers_subdir) and os.path.isdir(papers_subdir):
            subdir_files = [f for f in os.listdir(papers_subdir) if os.path.isfile(os.path.join(papers_subdir, f))]
            logging.info(f"在 {papers_subdir} 子目录下找到 {len(subdir_files)} 个文件")
            total_files += len(subdir_files)
            
            for filename in subdir_files:
                norm_name = normalize_for_matching(filename)
                full_path = os.path.join(papers_subdir, filename)
                
                if norm_name not in file_mapping:
                    file_mapping[norm_name] = []
                file_mapping[norm_name].append((filename, full_path))
        
        logging.info(f"总计找到 {total_files} 个文件")
    
    logging.info(f"文件系统中找到 {sum(len(files) for files in file_mapping.values())} 个文件")
    
    # 2. 根据数据库记录重命名文件
    for norm_db_name, (record_id, db_filename) in db_files.items():
        if norm_db_name in file_mapping:
            for orig_filename, full_path in file_mapping[norm_db_name]:
                # 跳过已经匹配的文件
                if orig_filename == db_filename:
                    logging.info(f"文件已匹配，无需重命名 (ID {record_id}): {orig_filename}")
                    skipped_count += 1
                    continue
                
                # 构建新路径
                new_path = os.path.join(os.path.dirname(full_path), db_filename)
                
                # 如果目标已存在且不是自身，跳过
                if os.path.exists(new_path) and full_path != new_path:
                    logging.warning(f"目标文件已存在，跳过 (ID {record_id}): {orig_filename} → {db_filename}")
                    skipped_count += 1
                    continue
                
                try:
                    # 强制重命名
                    os.rename(full_path, new_path)
                    logging.info(f"已重命名 (ID {record_id}): {orig_filename} → {db_filename}")
                    renamed_count += 1
                except Exception as e:
                    logging.error(f"重命名失败 (ID {record_id}): {e}")
                    skipped_count += 1
        else:
            logging.warning(f"未找到匹配文件 (ID {record_id}): {db_filename}")
            not_found_count += 1
    
    logging.info(f"\n重命名总结:")
    logging.info(f"已重命名: {renamed_count}")
    logging.info(f"已跳过: {skipped_count}")
    logging.info(f"未找到匹配: {not_found_count}")

# 主函数
def main():
    logging.info("开始强制重命名文件...")
    
    # 创建备份
    create_backup()
    
    # 执行重命名
    force_rename_files()
    
    logging.info("处理完成！")

if __name__ == "__main__":
    main()
