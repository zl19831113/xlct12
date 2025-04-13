#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重复文件处理工具
功能：检测并重命名或删除重复的试卷文件
"""

import os
import hashlib
import shutil
import sqlite3
from datetime import datetime
import logging
import re

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('duplicate_files.log')
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

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

def calculate_hash(file_path, block_size=8192):
    """计算文件的MD5哈希值"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

def create_backup_folder():
    """创建备份文件夹"""
    backup_dir = os.path.join(PROJECT_ROOT, 'duplicate_backups')
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = os.path.join(backup_dir, f'duplicate_files_{timestamp}')
    os.makedirs(backup_path, exist_ok=True)
    logger.info(f"已创建备份目录: {backup_path}")
    print(f"{YELLOW}已创建备份目录: {backup_path}{NC}")
    return backup_path

def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.duplicate_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"已创建数据库备份: {backup_path}")
    print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    return backup_path

def get_files_by_hash():
    """获取所有文件的哈希值，并按哈希值分组"""
    file_hashes = {}
    total_files = 0
    
    for root, _, files in os.walk(PAPERS_DIR):
        for filename in files:
            if filename.startswith('.'):
                continue
                
            if not filename.lower().endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                continue
                
            total_files += 1
            if total_files % 100 == 0:
                print(f"{BLUE}已处理 {total_files} 个文件...{NC}")
                
            file_path = os.path.join(root, filename)
            try:
                file_hash = calculate_hash(file_path)
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                
                file_hashes[file_hash].append({
                    'path': file_path,
                    'rel_path': rel_path,
                    'filename': filename,
                    'size': os.path.getsize(file_path)
                })
            except Exception as e:
                logger.error(f"处理文件时出错: {file_path}, 错误: {str(e)}")
    
    return file_hashes, total_files

def handle_duplicates(dry_run=True, mode='rename'):
    """处理重复文件
    
    参数:
    - dry_run: 是否仅演习不实际操作
    - mode: 处理模式 'rename'(重命名) 或 'delete'(删除)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"{GREEN}正在扫描文件并计算哈希值...{NC}")
    file_hashes, total_files = get_files_by_hash()
    
    # 筛选出有重复的文件
    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
    
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())
    duplicate_groups = len(duplicates)
    
    logger.info(f"总文件数: {total_files}, 重复文件组: {duplicate_groups}, 重复文件数: {total_duplicates}")
    print(f"\n{GREEN}扫描完成!{NC}")
    print(f"总文件数: {total_files}")
    print(f"重复文件组: {duplicate_groups}")
    print(f"重复文件数: {total_duplicates}")
    
    if duplicate_groups == 0:
        print(f"{GREEN}没有发现重复文件，无需处理。{NC}")
        conn.close()
        return 0
    
    # 创建备份目录
    if not dry_run:
        backup_dir = create_backup_folder()
    
    # 统计处理信息
    processed = 0
    file_updates = []
    
    # 处理每组重复文件
    for hash_value, files in duplicates.items():
        # 按文件名排序，保留第一个文件
        sorted_files = sorted(files, key=lambda x: x['filename'])
        keep_file = sorted_files[0]
        duplicate_files = sorted_files[1:]
        
        logger.info(f"保留文件: {keep_file['rel_path']}")
        
        # 显示信息
        if dry_run or processed < 5:  # 仅显示前5组详情
            print(f"\n{YELLOW}重复文件组 #{processed+1}:{NC}")
            print(f"  {GREEN}保留: {keep_file['filename']}{NC}")
            for i, dup in enumerate(duplicate_files):
                print(f"  {RED}重复 {i+1}: {dup['filename']}{NC}")
        
        # 处理重复文件
        for i, dup_file in enumerate(duplicate_files):
            # 查询数据库中引用该文件的记录
            cursor.execute("SELECT id, name FROM papers WHERE file_path = ?", (dup_file['rel_path'],))
            referring_records = cursor.fetchall()
            
            if not dry_run:
                if mode == 'rename':
                    # 重命名文件
                    filename, ext = os.path.splitext(dup_file['filename'])
                    new_filename = f"{filename}.duplicate.{i+1}{ext}"
                    new_path = os.path.join(os.path.dirname(dup_file['path']), new_filename)
                    new_rel_path = os.path.relpath(new_path, PROJECT_ROOT)
                    
                    # 创建文件备份
                    backup_file = os.path.join(backup_dir, dup_file['filename'])
                    shutil.copy2(dup_file['path'], backup_file)
                    
                    # 重命名文件
                    shutil.move(dup_file['path'], new_path)
                    logger.info(f"重命名: {dup_file['rel_path']} -> {new_rel_path}")
                    
                    # 更新数据库中的引用
                    for record_id, _ in referring_records:
                        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", 
                                      (keep_file['rel_path'], record_id))
                        file_updates.append((record_id, dup_file['rel_path'], keep_file['rel_path']))
                
                elif mode == 'delete':
                    # 创建文件备份
                    backup_file = os.path.join(backup_dir, dup_file['filename'])
                    shutil.copy2(dup_file['path'], backup_file)
                    
                    # 删除文件
                    os.remove(dup_file['path'])
                    logger.info(f"删除: {dup_file['rel_path']}")
                    
                    # 更新数据库中的引用
                    for record_id, _ in referring_records:
                        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", 
                                      (keep_file['rel_path'], record_id))
                        file_updates.append((record_id, dup_file['rel_path'], keep_file['rel_path']))
        
        processed += 1
        
        # 每处理10组显示进度
        if processed % 10 == 0:
            print(f"{BLUE}已处理 {processed}/{duplicate_groups} 组重复文件...{NC}")
    
    # 提交数据库更改
    if not dry_run:
        conn.commit()
        
        # 记录数据库更新
        for record_id, old_path, new_path in file_updates:
            logger.info(f"更新记录: ID={record_id}, {old_path} -> {new_path}")
    
    conn.close()
    
    # 显示结果
    if dry_run:
        print(f"\n{YELLOW}[演习模式] 以上是将要处理的重复文件{NC}")
        print(f"模式: {'重命名' if mode == 'rename' else '删除'}")
        print(f"找到 {duplicate_groups} 组重复文件，共 {total_duplicates} 个重复")
        print(f"\n{GREEN}要实际处理这些文件，请运行:{NC}")
        if mode == 'rename':
            print(f"python3 remove_duplicate_files.py --rename --confirm")
        else:
            print(f"python3 remove_duplicate_files.py --delete --confirm")
    else:
        print(f"\n{GREEN}重复文件处理完成!{NC}")
        print(f"模式: {'重命名' if mode == 'rename' else '删除'}")
        print(f"处理了 {duplicate_groups} 组重复文件，共 {total_duplicates} 个重复")
        print(f"更新了 {len(file_updates)} 条数据库记录")
        print(f"{YELLOW}所有操作已完成，请重启应用以应用更改{NC}")
    
    return total_duplicates

def main():
    """主函数"""
    import sys
    
    # 解析参数
    confirm = '--confirm' in sys.argv
    rename_mode = '--rename' in sys.argv
    delete_mode = '--delete' in sys.argv
    
    # 如果没有指定模式，默认为重命名
    if not rename_mode and not delete_mode:
        rename_mode = True
    
    mode = 'rename' if rename_mode else 'delete'
    
    print(f"\n{GREEN}===== 重复文件处理工具 ====={NC}")
    
    if not confirm:
        print(f"{YELLOW}[演习模式] 将只显示要处理的文件，不会实际操作。{NC}")
        print(f"{YELLOW}模式: {'重命名' if mode == 'rename' else '删除'}{NC}")
        print(f"{YELLOW}如需实际操作，请添加 --confirm 参数{NC}\n")
    else:
        print(f"{RED}[执行模式] 将实际{'重命名' if mode == 'rename' else '删除'}重复文件！{NC}\n")
        
        # 备份数据库
        backup_path = backup_database()
    
    # 处理重复文件
    handle_duplicates(dry_run=not confirm, mode=mode)

if __name__ == "__main__":
    main() 