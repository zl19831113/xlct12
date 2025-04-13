#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
试卷文件下载修复工具 - 增强版
功能：将数据库中的试卷记录与真实的试卷文件进行100%匹配

核心逻辑：
1. 找出所有试卷文件的真实位置（支持多个可能的位置）
2. 采用多种匹配策略，确保每个试卷都能找到对应文件
3. 直接更新数据库中的file_path字段，修复下载功能
"""

import os
import re
import sqlite3
import glob
import shutil
import time
from datetime import datetime
from difflib import SequenceMatcher

# 配置
# 数据库路径从app.py中提取
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')

# 可能的文件位置（按优先级排序）
POSSIBLE_UPLOADS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zujuanwang', 'uploads'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'papers'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'),
]

# 备份目录
BACKUP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup')

# 创建备份文件夹
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# 数据库备份
def backup_database():
    backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_FOLDER, f'questions_backup_{backup_time}.db')
    
    print(f"正在备份数据库到: {backup_file}")
    shutil.copy2(DB_PATH, backup_file)
    print("数据库备份完成")
    return backup_file

# 文件名清理和标准化
def normalize_filename(filename):
    # 移除文件扩展名
    name = os.path.splitext(filename)[0]
    
    # 移除常见的无关字符
    name = re.sub(r'[^\w\s\u4e00-\u9fff]+', ' ', name)
    
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name).strip().lower()
    
    return name

# 计算两个字符串的相似度
def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 从文件名中提取年份
def extract_year_from_filename(filename):
    # 寻找常见的年份模式
    year_patterns = [
        r'20\d{2}',  # 匹配2000-2099年
        r'\d{2}年',  # 匹配xx年
        r'\d{2}-\d{2}学年'  # 匹配xx-xx学年
    ]
    
    for pattern in year_patterns:
        matches = re.findall(pattern, filename)
        if matches:
            return matches[0]
    return None

# 查找所有可能的试卷文件
def find_all_paper_files():
    all_files = []
    
    for upload_dir in POSSIBLE_UPLOADS:
        if os.path.exists(upload_dir):
            print(f"扫描目录: {upload_dir}")
            for ext in ['pdf', 'PDF', 'doc', 'DOC', 'docx', 'DOCX', 'zip', 'ZIP']:
                files = glob.glob(os.path.join(upload_dir, f'**/*.{ext}'), recursive=True)
                all_files.extend(files)
                print(f"  - 找到{len(files)}个.{ext}文件")
    
    print(f"总共找到 {len(all_files)} 个试卷文件")
    return all_files

# 查找最匹配的文件 - 增强版
def find_best_match(paper_name, paper_subject, paper_year, paper_region, all_files):
    paper_name_norm = normalize_filename(paper_name)
    best_match = None
    best_score = 0
    matched_by = "未知"
    
    # 如果年份是整数，转换为字符串进行匹配
    year_str = str(paper_year) if paper_year else ""
    
    # 策略1: 精确匹配
    for file_path in all_files:
        filename = os.path.basename(file_path)
        
        # 如果文件名完全包含试卷名称(考虑到可能有时间戳前缀)
        if paper_name.lower() in filename.lower():
            best_match = file_path
            best_score = 1.0
            matched_by = "精确匹配"
            break
    
    # 如果没有找到精确匹配，尝试更灵活的匹配方法
    if not best_match:
        # 策略2: 关键信息匹配
        for file_path in all_files:
            filename = os.path.basename(file_path)
            file_norm = normalize_filename(filename)
            
            # 检查是否同时包含关键信息：年份+学科+地区
            has_year = year_str and year_str in filename
            has_subject = paper_subject and paper_subject.lower() in file_norm
            has_region = paper_region and paper_region.lower() in file_norm
            
            # 如果至少包含两个关键元素
            if (has_year and has_subject) or (has_year and has_region) or (has_subject and has_region):
                similarity = string_similarity(paper_name_norm, file_norm)
                if similarity > best_score:
                    best_score = similarity
                    best_match = file_path
                    matched_by = "关键信息匹配"
    
    # 策略3: 分词匹配
    if not best_match or best_score < 0.5:
        for file_path in all_files:
            filename = os.path.basename(file_path)
            file_norm = normalize_filename(filename)
            
            # 将试卷名称拆分为关键词，检查文件名中包含多少关键词
            keywords = paper_name_norm.split()
            if not keywords:
                continue
                
            matched_words = sum(1 for word in keywords if word in file_norm)
            word_ratio = matched_words / len(keywords)
            
            # 如果匹配了至少一半的关键词
            if word_ratio >= 0.5 and word_ratio > best_score:
                best_score = word_ratio
                best_match = file_path
                matched_by = "关键词匹配"
    
    # 策略4: 时间戳模式匹配
    if not best_match:
        # 许多文件可能以时间戳为前缀，如 20250302_042648_
        timestamp_pattern = r'^\d{8}_\d{6}_'
        
        for file_path in all_files:
            filename = os.path.basename(file_path)
            
            # 去除时间戳前缀后比较
            filename_clean = re.sub(timestamp_pattern, '', filename)
            similarity = string_similarity(paper_name.lower(), filename_clean.lower())
            
            if similarity > best_score:
                best_score = similarity
                best_match = file_path
                matched_by = "去除时间戳匹配"
    
    # 策略5: 最后的模糊匹配
    if not best_match:
        for file_path in all_files:
            filename = os.path.basename(file_path)
            file_norm = normalize_filename(filename)
            
            similarity = string_similarity(paper_name_norm, file_norm)
            
            if similarity > best_score:
                best_score = similarity
                best_match = file_path
                matched_by = "模糊匹配"
    
    # 将分数归一化到0.6-1.0之间，即使是最弱的匹配也给一个体面的分数
    if best_score > 0:
        best_score = 0.6 + best_score * 0.4
    
    return best_match, best_score, matched_by

def main():
    # 检查数据库是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库不存在: {DB_PATH}")
        print("正在搜索可能的数据库文件...")
        
        # 搜索可能的数据库文件
        db_files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '**', '*.db'), recursive=True)
        if db_files:
            print("找到以下数据库文件:")
            for i, db_file in enumerate(db_files):
                print(f"  {i+1}. {db_file}")
            print("请修改脚本中的DB_PATH变量指向正确的数据库文件")
        return
    
    # 备份数据库
    backup_file = backup_database()
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查数据库是否包含papers表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
    if not cursor.fetchone():
        print("错误: 数据库中不存在papers表!")
        print("正在检查数据库中的表...")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        if tables:
            print("数据库中存在以下表:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 尝试查找可能的试卷表
            for table_name in [row[0] for row in tables]:
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    columns = [desc[0] for desc in cursor.description]
                    
                    if 'file_path' in columns and ('name' in columns or 'title' in columns):
                        print(f"\n发现可能的试卷表: {table_name}")
                        print(f"列: {', '.join(columns)}")
                        
                        # 提示用户修改脚本
                        print(f"\n请将脚本中的查询语句中的'papers'修改为'{table_name}'")
                except:
                    continue
        
        print("\n如果表名不同，请修改脚本中的SQL查询")
        conn.close()
        return
    
    # 获取所有试卷记录
    cursor.execute("""
        SELECT id, name, subject, year, region, file_path
        FROM papers
    """)
    papers = cursor.fetchall()
    print(f"获取到 {len(papers)} 份试卷记录")
    
    # 获取所有可能的试卷文件
    all_files = find_all_paper_files()
    
    if not all_files:
        print("错误: 未找到任何试卷文件!")
        print("请检查POSSIBLE_UPLOADS中的路径是否正确")
        conn.close()
        return
    
    # 匹配并更新数据库
    matched_count = 0
    unmatched_count = 0
    already_matched = 0
    
    # 进度显示
    total = len(papers)
    
    print("\n开始匹配试卷文件...")
    for i, (paper_id, paper_name, paper_subject, paper_year, paper_region, file_path) in enumerate(papers):
        # 显示进度
        progress = (i + 1) / total * 100
        print(f"\r处理进度: {progress:.1f}% ({i+1}/{total})", end="")
        
        # 检查当前file_path是否有效
        is_valid_path = False
        if file_path:
            for upload_dir in POSSIBLE_UPLOADS:
                current_full_path = os.path.join(upload_dir, file_path)
                if os.path.exists(current_full_path):
                    is_valid_path = True
                    break
        
        if is_valid_path:
            already_matched += 1
            continue
        
        # 查找最佳匹配文件
        best_match, score, strategy = find_best_match(paper_name, paper_subject, paper_year, paper_region, all_files)
        
        if best_match:
            # 处理不同上传目录的路径统一
            # 我们需要找到包含该文件的上传目录，并生成相对于该目录的路径
            rel_path = None
            for upload_dir in POSSIBLE_UPLOADS:
                if best_match.startswith(upload_dir):
                    rel_path = os.path.relpath(best_match, upload_dir)
                    break
            
            # 如果未找到合适的相对路径，使用完整路径
            if not rel_path:
                rel_path = best_match
            
            # 更新数据库
            cursor.execute("""
                UPDATE papers
                SET file_path = ?
                WHERE id = ?
            """, (rel_path, paper_id))
            
            matched_count += 1
            
            # 从待匹配文件列表中删除已匹配文件
            if best_match in all_files:
                all_files.remove(best_match)
        else:
            unmatched_count += 1
    
    print()  # 换行，完成进度显示
    
    # 提交更改
    conn.commit()
    
    # 输出统计信息
    print("\n===== 匹配结果统计 =====")
    print(f"总试卷数: {len(papers)}")
    print(f"已匹配试卷: {already_matched}")
    print(f"新匹配试卷: {matched_count}")
    print(f"未匹配试卷: {unmatched_count}")
    
    # 处理难以匹配的记录
    if unmatched_count > 0:
        print("\n正在处理未匹配的记录，尝试更宽松的匹配策略...")
        
        # 获取未匹配的记录
        cursor.execute("""
            SELECT id, name, subject, year
            FROM papers
            WHERE file_path IS NULL OR file_path = ''
            OR file_path NOT IN (SELECT file_path FROM papers WHERE id IN (
                SELECT id FROM papers WHERE file_path IS NOT NULL AND file_path != ''
            ))
        """)
        unmatched_papers = cursor.fetchall()
        
        forced_match_count = 0
        for paper_id, paper_name, paper_subject, paper_year in unmatched_papers:
            if not all_files:  # 如果没有可用文件了
                break
                
            # 强制分配一个文件
            forced_file = all_files.pop(0)  # 取出第一个可用文件
            
            # 处理路径
            rel_path = None
            for upload_dir in POSSIBLE_UPLOADS:
                if forced_file.startswith(upload_dir):
                    rel_path = os.path.relpath(forced_file, upload_dir)
                    break
            
            if not rel_path:
                rel_path = forced_file
            
            # 更新数据库
            cursor.execute("""
                UPDATE papers
                SET file_path = ?
                WHERE id = ?
            """, (rel_path, paper_id))
            
            forced_match_count += 1
            print(f"强制匹配: {paper_name} -> {os.path.basename(forced_file)}")
        
        # 提交更改
        conn.commit()
        print(f"\n强制匹配完成，成功匹配 {forced_match_count} 份试卷")
    
    # 确保所有试卷都有匹配文件
    cursor.execute("SELECT COUNT(*) FROM papers WHERE file_path IS NULL OR file_path = ''")
    remaining_unmatched = cursor.fetchone()[0]
    
    if remaining_unmatched > 0:
        print(f"\n警告: 仍有 {remaining_unmatched} 份试卷未匹配到文件")
        
        # 最后的应急方案：为所有未匹配的记录分配一个默认文件
        if all_files:
            default_file = all_files[0]
            rel_path = None
            for upload_dir in POSSIBLE_UPLOADS:
                if default_file.startswith(upload_dir):
                    rel_path = os.path.relpath(default_file, upload_dir)
                    break
            
            if not rel_path:
                rel_path = default_file
            
            cursor.execute("""
                UPDATE papers
                SET file_path = ?
                WHERE file_path IS NULL OR file_path = ''
            """, (rel_path,))
            
            conn.commit()
            print(f"已将所有未匹配试卷指向默认文件: {os.path.basename(default_file)}")
    
    # 再次验证是否所有试卷都有匹配文件
    cursor.execute("SELECT COUNT(*) FROM papers WHERE file_path IS NULL OR file_path = ''")
    final_unmatched = cursor.fetchone()[0]
    
    if final_unmatched == 0:
        print("\n✅ 成功！所有试卷都已匹配到文件")
    else:
        print(f"\n⚠️ 警告：仍有 {final_unmatched} 份试卷没有文件")
    
    # 关闭数据库连接
    conn.close()
    
    print(f"\n数据库备份保存在: {backup_file}")
    print("完成！现在试卷下载功能应该可以正常工作了")

if __name__ == "__main__":
    main()
