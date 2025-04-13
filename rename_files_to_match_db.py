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
    filename=f'file_rename_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# 配置 - 使用绝对路径
DB_PATH = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/instance/xlct12.db"
PAPERS_DIR = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/papers"
BACKUP_DIR = f"/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# 确保不同的文件名映射到不同的文件
file_mapping = {}

# 获取数据库中的所有记录
def get_db_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_path FROM papers")
    records = cursor.fetchall()
    conn.close()
    return records

# 创建上传目录备份
def backup_uploads_dir():
    logging.info(f"正在创建uploads目录备份: {BACKUP_DIR}")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copytree(PAPERS_DIR, os.path.join(BACKUP_DIR, 'papers'))
    logging.info(f"uploads目录备份完成")

# 从文件路径中提取文件名，并规范化用于比较
def normalize_filename(filename):
    # 去除扩展名
    base_name, ext = os.path.splitext(filename)
    
    # 去除所有非字母数字字符
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', base_name)
    
    return clean_name.lower(), ext

# 查找文件系统中的所有文件
def get_filesystem_files():
    files = []
    # 检查目录是否存在
    if not os.path.exists(PAPERS_DIR):
        logging.error(f"错误: 目录 {PAPERS_DIR} 不存在!")
        return files
    
    # 先只遍历 PAPERS_DIR 下的文件，不包括子目录
    direct_files = [(f, os.path.join(PAPERS_DIR, f)) for f in os.listdir(PAPERS_DIR) 
                   if os.path.isfile(os.path.join(PAPERS_DIR, f))]
    logging.info(f"在 {PAPERS_DIR} 目录下直接找到 {len(direct_files)} 个文件")
    
    # 再递归遍历所有文件（包括子目录）
    for root, _, filenames in os.walk(PAPERS_DIR):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            files.append((filename, full_path, full_path))
    
    logging.info(f"总共找到 {len(files)} 个文件（包括子目录）")
    return files

# 根据数据库记录重命名文件
def rename_files_to_match_db():
    # 获取数据库记录
    db_records = get_db_records()
    logging.info(f"从数据库加载了 {len(db_records)} 条记录")
    
    # 获取文件系统中的所有文件
    fs_files = get_filesystem_files()
    logging.info(f"文件系统中发现 {len(fs_files)} 个文件")
    
    # 创建规范化文件名到实际文件的映射
    fs_file_map = {}
    for filename, full_path, rel_path in fs_files:
        norm_name, ext = normalize_filename(filename)
        if norm_name not in fs_file_map:
            fs_file_map[norm_name] = []
        fs_file_map[norm_name].append((filename, full_path, rel_path, ext))
    
    # 遍历每条数据库记录，找到对应的文件并重命名
    renamed_count = 0
    not_found_count = 0
    skipped_count = 0
    
    for record_id, record_name, file_path in db_records:
        db_filename = os.path.basename(file_path)
        db_dir = os.path.dirname(file_path)
        norm_db_name, db_ext = normalize_filename(db_filename)
        
        # 查找对应的文件
        found = False
        if norm_db_name in fs_file_map:
            for fs_filename, fs_full_path, fs_rel_path, fs_ext in fs_file_map[norm_db_name]:
                # 找到匹配的文件，检查是否需要重命名
                if fs_filename != db_filename:
                    # 构建新的文件路径
                    target_dir = os.path.dirname(fs_full_path)
                    new_path = os.path.join(target_dir, db_filename)
                    
                    # 检查目标文件是否已存在
                    if os.path.exists(new_path):
                        logging.warning(f"跳过：目标文件已存在 - ID {record_id}: {fs_full_path} → {new_path}")
                        skipped_count += 1
                        continue
                    
                    try:
                        # 重命名文件
                        logging.info(f"重命名文件 - ID {record_id}: {fs_filename} → {db_filename}")
                        os.rename(fs_full_path, new_path)
                        renamed_count += 1
                        found = True
                        break
                    except Exception as e:
                        logging.error(f"重命名失败 - ID {record_id}: {e}")
                        skipped_count += 1
                else:
                    # 文件名已经匹配，不需要重命名
                    logging.info(f"文件名已匹配 - ID {record_id}: {fs_filename}")
                    skipped_count += 1
                    found = True
                    break
        
        if not found:
            logging.error(f"未找到匹配文件 - ID {record_id}: {db_filename}")
            not_found_count += 1
    
    logging.info(f"\n重命名总结:")
    logging.info(f"已重命名: {renamed_count}")
    logging.info(f"已跳过(已匹配或出错): {skipped_count}")
    logging.info(f"未找到匹配: {not_found_count}")

# 主函数
def main():
    logging.info("开始重命名文件，使其与数据库记录匹配...")
    
    # 创建备份
    backup_uploads_dir()
    
    # 执行重命名
    rename_files_to_match_db()
    
    logging.info("处理完成！请检查日志文件获取详细信息。")

if __name__ == "__main__":
    main()
