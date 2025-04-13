#!/usr/bin/env python3
"""
批量修复文件名脚本: 将uploads/papers目录中带下划线的文件名重命名为数据库中无下划线的格式
"""
import os
import re
import sys
import sqlite3
from shutil import copy2
from datetime import datetime

# 配置
DB_PATH = '/var/www/question_bank/instance/questions.db'
PAPERS_DIR = '/var/www/question_bank/uploads/papers'
BACKUP_DIR = '/var/www/question_bank/uploads/papers_backup_{}'.format(
    datetime.now().strftime('%Y%m%d_%H%M%S')
)
DRY_RUN = True  # 设置为True时只显示会做什么而不实际修改

def backup_directory():
    """创建目录备份"""
    if DRY_RUN:
        print(f"[DRY RUN] 将创建备份目录: {BACKUP_DIR}")
        return
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"创建备份目录: {BACKUP_DIR}")
    
    # 复制所有文件到备份目录
    for filename in os.listdir(PAPERS_DIR):
        src_path = os.path.join(PAPERS_DIR, filename)
        if os.path.isfile(src_path):
            dst_path = os.path.join(BACKUP_DIR, filename)
            copy2(src_path, dst_path)
    
    print(f"已备份 {PAPERS_DIR} 中的所有文件到 {BACKUP_DIR}")

def get_db_filenames():
    """从数据库获取所有试卷文件名"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_path FROM papers")
        results = cursor.fetchall()
        conn.close()
        
        # 提取文件名和ID
        db_files = {}
        for paper_id, file_path in results:
            if file_path:
                filename = os.path.basename(file_path)
                db_files[filename] = paper_id
        
        print(f"从数据库获取了 {len(db_files)} 个文件记录")
        return db_files
    except Exception as e:
        print(f"读取数据库出错: {e}")
        sys.exit(1)

def remove_underscores(filename):
    """从文件名中删除下划线"""
    if filename.startswith('20') and '_' in filename[:15]:
        # 处理类似 20250226_084908_2024-202512.docx 的格式
        parts = filename.split('_', 2)
        if len(parts) >= 3:
            return parts[0] + parts[1] + '_' + parts[2]
        elif len(parts) == 2:
            return parts[0] + parts[1]
    return filename

def normalize_filename(filename):
    """标准化文件名以便比较"""
    # 移除所有下划线和连字符
    return re.sub(r'[_-]', '', filename.lower())

def compare_filenames(db_file, dir_file):
    """比较两个文件名的相似度"""
    # 如果都是以20开头的时间戳文件名
    if db_file.startswith('20') and dir_file.startswith('20'):
        # 获取db_file中时间部分(去掉下划线)
        db_prefix = db_file[:8]  # 日期部分 (20250226)
        db_time = ''
        if len(db_file) > 8:
            db_time_match = re.search(r'^\d{8}(\d{6})', db_file)
            if db_time_match:
                db_time = db_time_match.group(1)  # 时间部分 (084908)
        
        # 获取dir_file中时间部分
        dir_prefix = dir_file[:8]  # 日期部分
        dir_time = ''
        if '_' in dir_file and len(dir_file) > 9:
            dir_time_match = re.search(r'^\d{8}_(\d{6})', dir_file)
            if dir_time_match:
                dir_time = dir_time_match.group(1)  # 时间部分
        
        # 首先比较日期前缀
        if db_prefix != dir_prefix:
            return 0  # 日期不匹配
        
        # 如果时间部分存在且匹配
        if db_time and dir_time and db_time == dir_time:
            return 100  # 完全匹配
        
        # 获取文件名的剩余部分（去掉时间戳部分）
        db_rest = db_file[14:] if len(db_file) > 14 else ''
        dir_rest = ''
        if '_' in dir_file:
            parts = dir_file.split('_', 2)
            if len(parts) >= 3:
                dir_rest = parts[2]
        
        # 比较剩余部分
        if db_rest and dir_rest:
            # 如果剩余部分完全相同
            if db_rest == dir_rest:
                return 90
            
            # 如果剩余部分相似（忽略下划线和连字符）
            db_clean = normalize_filename(db_rest)
            dir_clean = normalize_filename(dir_rest)
            if db_clean == dir_clean:
                return 80
            
            # 如果剩余部分包含关系
            if db_clean in dir_clean or dir_clean in db_clean:
                return 70
    
    # 标准化后完全相同
    if normalize_filename(db_file) == normalize_filename(dir_file):
        return 60
    
    # 部分包含关系
    norm_db = normalize_filename(db_file)
    norm_dir = normalize_filename(dir_file)
    if norm_db in norm_dir or norm_dir in norm_db:
        return 50
    
    return 0  # 不匹配

def fix_filenames():
    """修复文件名与数据库记录不匹配的问题"""
    # 获取数据库中记录的文件名
    db_files = get_db_filenames()
    
    # 获取实际目录中的文件
    dir_files = os.listdir(PAPERS_DIR)
    
    # 跟踪处理的文件
    renamed_files = 0
    unchanged_files = 0
    problematic_files = []
    
    # 跟踪已经使用的目录文件，避免重复使用
    used_dir_files = set()
    
    # 首先创建一个映射: 去除下划线后的文件名 -> 原始文件名
    raw_to_underscore = {}
    for filename in dir_files:
        # 仅处理以20开头且包含下划线的文件
        if filename.startswith('20') and '_' in filename[:15]:
            no_underscore = remove_underscores(filename)
            raw_to_underscore[no_underscore] = filename
    
    # 对数据库中的每个文件进行处理
    for db_filename, paper_id in db_files.items():
        # 检查文件是否已存在
        db_filepath = os.path.join(PAPERS_DIR, db_filename)
        
        if os.path.exists(db_filepath):
            unchanged_files += 1
            continue
            
        # 检查去除下划线后是否匹配
        if db_filename in raw_to_underscore:
            # 找到了匹配的文件，需要重命名
            original_name = raw_to_underscore[db_filename]
            if original_name in used_dir_files:
                problematic_files.append((db_filename, f"对应的文件 {original_name} 已被使用"))
                continue
                
            src_path = os.path.join(PAPERS_DIR, original_name)
            dst_path = os.path.join(PAPERS_DIR, db_filename)
            
            if DRY_RUN:
                print(f"[DRY RUN] 将重命名: {original_name} -> {db_filename} (Paper ID: {paper_id})")
            else:
                try:
                    os.rename(src_path, dst_path)
                    print(f"已重命名: {original_name} -> {db_filename} (Paper ID: {paper_id})")
                    renamed_files += 1
                    used_dir_files.add(original_name)
                except Exception as e:
                    print(f"重命名出错 {original_name}: {e}")
                    problematic_files.append((original_name, str(e)))
        else:
            # 尝试其他模式匹配
            found_match = False
            best_match = None
            best_score = 0
            
            # 查找最佳匹配
            for dir_file in dir_files:
                if dir_file in used_dir_files:
                    continue
                    
                score = compare_filenames(db_filename, dir_file)
                if score > best_score:
                    best_score = score
                    best_match = dir_file
            
            # 如果找到足够相似的匹配
            if best_match and best_score >= 70:  # 至少70%相似度
                src_path = os.path.join(PAPERS_DIR, best_match)
                dst_path = os.path.join(PAPERS_DIR, db_filename)
                
                if DRY_RUN:
                    print(f"[DRY RUN] 将重命名(相似度{best_score}%): {best_match} -> {db_filename} (Paper ID: {paper_id})")
                else:
                    try:
                        os.rename(src_path, dst_path)
                        print(f"已重命名(相似度{best_score}%): {best_match} -> {db_filename} (Paper ID: {paper_id})")
                        renamed_files += 1
                        used_dir_files.add(best_match)
                        found_match = True
                    except Exception as e:
                        print(f"重命名出错 {best_match}: {e}")
                        problematic_files.append((best_match, str(e)))
            
            if not found_match:
                problematic_files.append((db_filename, "未找到匹配文件"))
    
    # 输出统计信息
    print("\n===== 处理结果 =====")
    print(f"已重命名: {renamed_files} 个文件")
    print(f"无需更改: {unchanged_files} 个文件")
    print(f"问题文件: {len(problematic_files)} 个")
    
    if problematic_files:
        print("\n问题文件清单:")
        for filename, error in problematic_files[:50]:  # 只显示前50个
            print(f"- {filename}: {error}")
        
        if len(problematic_files) > 50:
            print(f"...以及 {len(problematic_files) - 50} 个更多问题文件")

if __name__ == "__main__":
    print("批量修复文件名与数据库不匹配问题脚本")
    print(f"数据库: {DB_PATH}")
    print(f"文件目录: {PAPERS_DIR}")
    
    if DRY_RUN:
        print("\n[DRY RUN 模式 - 不会实际修改文件]\n")
    else:
        print("\n[警告] 即将对文件进行实际重命名操作!\n")
        confirm = input("是否继续? (y/n): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    # 创建备份
    backup_directory()
    
    # 修复文件名
    fix_filenames()
    
    print("\n完成!") 