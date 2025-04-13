#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
紧急修复脚本 - 创建下划线和连字符版本的符号链接
运行方式：在服务器上执行 python3 create_symlinks.py
"""

import os
import sqlite3
import sys

# 服务器路径
DB_PATH = '/var/www/question_bank/instance/xlct12.db'
PAPERS_DIR = '/var/www/question_bank/uploads/papers'

print("===== 文件链接修复脚本 =====")
print(f"数据库路径: {DB_PATH}")
print(f"试卷目录: {PAPERS_DIR}")

# 检查目录是否存在
if not os.path.exists(PAPERS_DIR):
    print(f"错误: 试卷目录不存在: {PAPERS_DIR}")
    sys.exit(1)

if not os.path.exists(DB_PATH):
    print(f"错误: 数据库文件不存在: {DB_PATH}")
    sys.exit(1)

# 连接数据库
print("连接数据库...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取所有试卷文件路径
print("获取数据库中的文件路径...")
cursor.execute("SELECT id, name, file_path FROM papers")
papers = cursor.fetchall()
print(f"共找到 {len(papers)} 条试卷记录")

# 创建符号链接函数
def create_alternate_links(file_path):
    """为文件创建备用格式的符号链接（下划线和连字符的相互转换）"""
    if not file_path or not file_path.strip():
        return False
    
    # 提取文件名
    if file_path.startswith('uploads/papers/'):
        base_path = PAPERS_DIR
        rel_path = file_path[len('uploads/papers/'):]
    else:
        base_path = os.path.dirname(os.path.join(PAPERS_DIR, file_path))
        rel_path = os.path.basename(file_path)
    
    # 完整路径
    full_path = os.path.join(base_path, rel_path)
    
    # 如果文件存在，为它创建符号链接
    if os.path.exists(full_path):
        # 下划线版本
        underscore_name = rel_path.replace('-', '_')
        if underscore_name != rel_path:
            underscore_path = os.path.join(base_path, underscore_name)
            if not os.path.exists(underscore_path):
                try:
                    os.symlink(full_path, underscore_path)
                    print(f"  创建下划线链接: {underscore_path}")
                    return True
                except Exception as e:
                    print(f"  创建链接失败: {e}")
        
        # 连字符版本
        dash_name = rel_path.replace('_', '-')
        if dash_name != rel_path:
            dash_path = os.path.join(base_path, dash_name)
            if not os.path.exists(dash_path):
                try:
                    os.symlink(full_path, dash_path)
                    print(f"  创建连字符链接: {dash_path}")
                    return True
                except Exception as e:
                    print(f"  创建链接失败: {e}")
        
        return False
    else:
        # 如果原始文件不存在，尝试查找替代文件
        alt_found = False
        
        # 尝试下划线版本
        underscore_name = rel_path.replace('-', '_')
        if underscore_name != rel_path:
            underscore_path = os.path.join(base_path, underscore_name)
            if os.path.exists(underscore_path):
                try:
                    os.symlink(underscore_path, full_path)
                    print(f"  创建原始格式链接: {full_path} -> {underscore_path}")
                    alt_found = True
                except Exception as e:
                    print(f"  创建链接失败: {e}")
        
        # 尝试连字符版本
        dash_name = rel_path.replace('_', '-')
        if dash_name != rel_path and not alt_found:
            dash_path = os.path.join(base_path, dash_name)
            if os.path.exists(dash_path):
                try:
                    os.symlink(dash_path, full_path)
                    print(f"  创建原始格式链接: {full_path} -> {dash_path}")
                    alt_found = True
                except Exception as e:
                    print(f"  创建链接失败: {e}")
        
        return alt_found

# 处理特定ID
specific_id = None
if len(sys.argv) > 1:
    try:
        specific_id = int(sys.argv[1])
        print(f"将只处理ID为 {specific_id} 的文件")
    except ValueError:
        print("提供的ID无效，将处理所有文件")

# 创建链接
links_created = 0
files_processed = 0

print("\n开始创建符号链接...")
for paper_id, name, file_path in papers:
    if specific_id is not None and paper_id != specific_id:
        continue
    
    files_processed += 1
    print(f"处理 [{paper_id}] {name}")
    
    if create_alternate_links(file_path):
        links_created += 1
    
    # 定期提示进度
    if files_processed % 100 == 0:
        print(f"已处理 {files_processed}/{len(papers)} 个文件，创建了 {links_created} 个链接")

# 显示结果
print("\n处理完成！")
print(f"总计处理了 {files_processed} 个文件路径")
print(f"创建了 {links_created} 个符号链接")

# 测试特定ID的文件
if specific_id is not None:
    cursor.execute("SELECT file_path FROM papers WHERE id = ?", (specific_id,))
    result = cursor.fetchone()
    if result:
        file_path = result[0]
        print(f"\n测试ID为 {specific_id} 的文件:")
        print(f"数据库路径: {file_path}")
        
        # 检查文件是否存在
        if file_path.startswith('uploads/papers/'):
            full_path = os.path.join('/var/www/question_bank', file_path)
        else:
            full_path = os.path.join(PAPERS_DIR, os.path.basename(file_path))
        
        if os.path.exists(full_path):
            print(f"文件存在: {full_path}")
        else:
            print(f"文件不存在: {full_path}")
            
            # 尝试替代路径
            underscore_path = full_path.replace('-', '_')
            dash_path = full_path.replace('_', '-')
            
            if underscore_path != full_path and os.path.exists(underscore_path):
                print(f"找到下划线版本: {underscore_path}")
            
            if dash_path != full_path and os.path.exists(dash_path):
                print(f"找到连字符版本: {dash_path}")

print("\n脚本执行完毕。请重启Web服务以确保更改生效。")
conn.close() 