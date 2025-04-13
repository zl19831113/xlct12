#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import shutil
from datetime import datetime
import logging
import csv

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'filename_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

# 配置 - 使用绝对路径
DB_PATH = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/instance/xlct12.db"
PAPERS_DIR = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads/papers"
BACKUP_DIR = f"/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/uploads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
CSV_EXPORT = f"/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76/papers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# 导出数据库表
def export_db_table():
    logging.info(f"正在从数据库导出papers表...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, file_path FROM papers")
    records = cursor.fetchall()
    conn.close()
    
    # 导出为CSV
    with open(CSV_EXPORT, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', '名称', '文件路径'])
        for record in records:
            writer.writerow(record)
    
    logging.info(f"已将 {len(records)} 条记录导出到 {CSV_EXPORT}")
    return records

# 备份uploads/papers目录
def backup_papers_dir():
    logging.info(f"正在备份 {PAPERS_DIR} 目录到 {BACKUP_DIR}...")
    if not os.path.exists(PAPERS_DIR):
        logging.error(f"错误: {PAPERS_DIR} 目录不存在！")
        return False
    
    try:
        shutil.copytree(PAPERS_DIR, BACKUP_DIR)
        logging.info(f"备份完成")
        return True
    except Exception as e:
        logging.error(f"备份失败: {str(e)}")
        return False

# 从数据库记录中提取文件名
def extract_db_filename(file_path):
    return os.path.basename(file_path)

# 重命名文件以匹配数据库记录
def rename_files_to_match_db(db_records):
    # 扫描uploads/papers目录中的所有文件
    files_to_rename = []
    
    if not os.path.exists(PAPERS_DIR):
        logging.error(f"错误: {PAPERS_DIR} 目录不存在！")
        return
    
    # 获取所有文件（不包括子目录）
    direct_files = [(f, os.path.join(PAPERS_DIR, f)) for f in os.listdir(PAPERS_DIR) 
                   if os.path.isfile(os.path.join(PAPERS_DIR, f))]
    logging.info(f"在 {PAPERS_DIR} 目录下直接找到 {len(direct_files)} 个文件")
    
    # 递归获取所有文件（包括子目录）
    all_files = []
    for root, _, filenames in os.walk(PAPERS_DIR):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            all_files.append((filename, full_path))
    
    logging.info(f"总共找到 {len(all_files)} 个文件（包括子目录）")
    
    # 创建文件名映射 - 去除扩展名和分隔符后的文件名 -> 原始文件信息
    file_mapping = {}
    for filename, filepath in all_files:
        base_name = os.path.splitext(filename)[0]
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', base_name).lower()
        
        if clean_name not in file_mapping:
            file_mapping[clean_name] = []
        file_mapping[clean_name].append((filename, filepath))
    
    # 遍历数据库记录，查找对应文件并处理下划线
    renamed_count = 0
    skipped_count = 0
    not_found_count = 0
    
    for record_id, record_name, file_path in db_records:
        db_filename = extract_db_filename(file_path)
        db_basename, db_ext = os.path.splitext(db_filename)
        
        # 提取无分隔符的数据库文件名用于匹配
        clean_db_name = re.sub(r'[^a-zA-Z0-9]', '', db_basename).lower()
        
        if clean_db_name in file_mapping:
            # 找到匹配的文件(s)
            matched_files = file_mapping[clean_db_name]
            
            for orig_filename, orig_filepath in matched_files:
                orig_basename, orig_ext = os.path.splitext(orig_filename)
                
                # 检查文件名是否已经与数据库记录匹配
                if orig_filename == db_filename:
                    logging.info(f"无需修改 - ID {record_id}: {orig_filename} 已匹配")
                    skipped_count += 1
                    continue
                
                # 确定新文件名
                # 使用数据库记录中的文件名，但保留原始扩展名
                new_filename = db_basename + orig_ext
                new_filepath = os.path.join(os.path.dirname(orig_filepath), new_filename)
                
                # 检查目标文件是否已存在
                if os.path.exists(new_filepath) and orig_filepath != new_filepath:
                    logging.warning(f"目标文件已存在，跳过 - ID {record_id}: {orig_filename} → {new_filename}")
                    skipped_count += 1
                    continue
                
                try:
                    # 重命名文件
                    os.rename(orig_filepath, new_filepath)
                    logging.info(f"已重命名 - ID {record_id}: {orig_filename} → {new_filename}")
                    renamed_count += 1
                except Exception as e:
                    logging.error(f"重命名失败 - ID {record_id}: {str(e)}")
                    skipped_count += 1
        else:
            logging.warning(f"未找到匹配文件 - ID {record_id}: {db_filename}")
            not_found_count += 1
    
    logging.info(f"\n重命名总结:")
    logging.info(f"文件总数: {len(all_files)}")
    logging.info(f"已重命名: {renamed_count}")
    logging.info(f"已跳过: {skipped_count}")
    logging.info(f"未找到匹配: {not_found_count}")

# 主函数
def main():
    logging.info("开始修复文件名，使其与数据库记录匹配...")
    
    # 导出数据库记录
    db_records = export_db_table()
    
    # 备份目录
    if not backup_papers_dir():
        response = input("备份失败，是否继续? (y/n): ")
        if response.lower() != 'y':
            logging.info("已取消操作")
            return
    
    # 重命名文件
    rename_files_to_match_db(db_records)
    
    logging.info("处理完成！")

if __name__ == "__main__":
    main()
