import os
import sqlite3
import re
from flask import Flask
from sqlalchemy import create_engine, text
import sys

# 创建临时Flask应用以获取配置
app = Flask(__name__)
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
db_path = os.path.join(instance_path, 'questions.db')
db_uri = f'sqlite:///{os.path.abspath(db_path)}'

print(f"数据库路径: {db_path}")
print(f"数据库URI: {db_uri}")

# 确认操作
if len(sys.argv) < 2 or sys.argv[1] != '--confirm':
    print("警告: 此脚本将修改数据库中的文件路径。")
    print("请确保您已备份数据库，避免数据丢失。")
    print("运行此脚本前，请验证以下信息:")
    print("1. 数据库文件路径是否正确")
    print("2. 上传文件的实际位置是否正确")
    print("\n执行修复，请添加--confirm参数:")
    print("python fix_file_paths.py --confirm")
    sys.exit(1)

# 直接连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取papers表的所有记录
cursor.execute("SELECT id, file_path FROM papers")
results = cursor.fetchall()

print(f"找到 {len(results)} 条记录")

# 定义路径转换函数
def convert_to_relative_path(old_path):
    # 提取文件名
    file_name = os.path.basename(old_path)
    
    # 构建新的相对路径
    # 检查路径中是否包含 'papers/papers'
    if 'papers/papers' in old_path or 'papers\\papers' in old_path:
        new_path = os.path.join('uploads', 'papers', 'papers', file_name)
    else:
        new_path = os.path.join('uploads', 'papers', file_name)
    
    return new_path

# 检查文件是否存在
def check_file_exists(path):
    return os.path.exists(path)

# 更新计数器
updated_count = 0
failed_count = 0
already_relative_count = 0

# 处理每条记录
for record_id, file_path in results:
    # 跳过已经是相对路径的记录
    if file_path.startswith('uploads/') or file_path.startswith('uploads\\'):
        already_relative_count += 1
        continue
        
    # 转换路径
    new_path = convert_to_relative_path(file_path)
    
    # 检查新文件是否存在
    if check_file_exists(new_path):
        # 更新数据库记录
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, record_id))
        print(f"ID {record_id}: 更新路径 {file_path} -> {new_path}")
        updated_count += 1
    else:
        print(f"ID {record_id}: 文件不存在 {new_path}, 保留原路径 {file_path}")
        failed_count += 1

# 提交更改
conn.commit()

# 输出统计信息
print("\n路径修复完成!")
print(f"共处理记录: {len(results)}")
print(f"已是相对路径: {already_relative_count}")
print(f"成功更新: {updated_count}")
print(f"更新失败: {failed_count}")

# 关闭连接
conn.close() 