import os
import sqlite3
import sys

# 配置信息
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"数据库路径: {DB_PATH}")
print(f"基础目录: {BASE_DIR}")

# 直接连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取papers表的所有记录
cursor.execute("SELECT id, name, file_path FROM papers")
results = cursor.fetchall()

print(f"找到 {len(results)} 条记录")

# 存储结果的列表
missing_files = []
found_files = []

# 检查每个文件
for record_id, name, file_path in results:
    # 处理相对路径和绝对路径
    if not file_path.startswith('/'):
        # 相对路径，从基础目录开始
        full_path = os.path.join(BASE_DIR, file_path)
    else:
        # 绝对路径
        full_path = file_path
        
        # 尝试在当前系统也查找
        if not os.path.exists(full_path):
            # 提取文件名
            file_name = os.path.basename(file_path)
            # 检查是否存在于不同的目录结构
            alt_paths = [
                os.path.join(BASE_DIR, 'uploads', 'papers', file_name),
                os.path.join(BASE_DIR, 'uploads', 'papers', 'papers', file_name)
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    full_path = alt_path
                    break
    
    # 检查文件是否存在
    if os.path.exists(full_path):
        found_files.append((record_id, name, file_path, full_path))
    else:
        missing_files.append((record_id, name, file_path))

# 关闭数据库连接
conn.close()

# 输出结果
print("\n检查结果:")
print(f"总记录数: {len(results)}")
print(f"找到的文件: {len(found_files)}")
print(f"丢失的文件: {len(missing_files)}")

# 详细输出丢失的文件
if missing_files:
    print("\n===== 丢失的文件 =====")
    for record_id, name, file_path in missing_files:
        print(f"ID: {record_id}, 名称: {name}, 路径: {file_path}")

# 输出建议
if missing_files:
    print("\n建议:")
    print("1. 请运行 migrate_papers.py 脚本尝试自动迁移和修复文件路径")
    print("2. 如果仍有文件丢失，请检查旧系统中是否存在这些文件")
    print("3. 修复完成后，再次运行此脚本确认所有文件都能找到")
else:
    print("\n太好了！所有文件都已找到。") 