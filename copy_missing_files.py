#!/usr/bin/env python3
import os
import sqlite3
import shutil
import time
from pathlib import Path

# 设置源路径和目标路径
SOURCE_PATH = "/Users/sl19831113/Desktop/未命名文件夹/zujuanwang47/uploads/papers"
TARGET_PATH = "/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang81/uploads/papers"

# 确保目标目录存在
os.makedirs(TARGET_PATH, exist_ok=True)

# 连接数据库
conn = sqlite3.connect('xlct12.db')
cursor = conn.cursor()

# 获取所有文件路径中包含 zujuanwang47 的记录
cursor.execute("SELECT id, name, file_path, subject FROM papers WHERE file_path LIKE '%zujuanwang47%'")
zujuanwang47_files = cursor.fetchall()

print(f"找到 {len(zujuanwang47_files)} 个在zujuanwang47的文件记录")

# 创建日志文件
log_file = f"copy_files_{time.strftime('%Y%m%d_%H%M%S')}.log"
with open(log_file, "w") as log:
    log.write(f"文件复制日志 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write("=" * 80 + "\n\n")

copied_count = 0
error_count = 0
skipped_count = 0
already_exists_count = 0

# 处理每个文件
print("\n开始复制文件...")
for idx, (file_id, name, file_path, subject) in enumerate(zujuanwang47_files, 1):
    if idx % 10 == 0:
        print(f"处理第 {idx}/{len(zujuanwang47_files)} 个文件...")
        
    # 提取原始文件名
    filename = os.path.basename(file_path)
    
    # 构建源文件和目标文件的完整路径
    source_file = file_path
    target_file = os.path.join(TARGET_PATH, filename)
    
    # 检查目标文件是否已存在
    if os.path.exists(target_file):
        already_exists_count += 1
        with open(log_file, "a") as log:
            log.write(f"跳过(已存在): ID={file_id}, 名称={name}, 文件名={filename}\n")
        continue
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        skipped_count += 1
        with open(log_file, "a") as log:
            log.write(f"跳过(源文件不存在): ID={file_id}, 名称={name}, 路径={source_file}\n")
        continue
    
    # 复制文件
    try:
        # 创建目标文件的父目录
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # 复制文件
        shutil.copy2(source_file, target_file)
        copied_count += 1
        
        with open(log_file, "a") as log:
            log.write(f"成功: ID={file_id}, 名称={name}, 从 {source_file} 复制到 {target_file}\n")
            
        # 如果希望在数据库中更新文件路径，取消注释以下代码
        # new_path = target_file
        # cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, file_id))
        # conn.commit()
        
    except Exception as e:
        error_count += 1
        with open(log_file, "a") as log:
            log.write(f"错误: ID={file_id}, 名称={name}, 错误信息={str(e)}\n")

# 打印摘要
print("\n== 复制操作摘要 ==")
print(f"总文件数: {len(zujuanwang47_files)}")
print(f"成功复制: {copied_count}")
print(f"已存在(跳过): {already_exists_count}")
print(f"源不存在(跳过): {skipped_count}")
print(f"错误: {error_count}")
print(f"日志文件: {log_file}")

# 关闭数据库连接
conn.close()

print("\n完成!")
