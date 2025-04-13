import os
import sqlite3
import re
import shutil
import sys

# 配置信息
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# 旧的系统根路径列表（尝试多个可能的旧路径）
OLD_SYSTEM_ROOTS = [
    r'/Users/sl19831113/Desktop/未命名文件夹/zujuanwang47',
    r'/Users/sl19831113/Desktop/未命名文件夹/zujuanwang48_副本3'
]

# 新系统根路径
NEW_SYSTEM_ROOT = os.path.dirname(os.path.abspath(__file__))

print(f"数据库路径: {DB_PATH}")
print(f"当前系统根路径: {NEW_SYSTEM_ROOT}")
print(f"上传目录: {UPLOADS_DIR}")

# 确认操作
if len(sys.argv) < 2 or sys.argv[1] != '--confirm':
    print("警告: 此脚本将迁移文件并修改数据库中的文件路径。")
    print("请确保您已备份数据库和文件，避免数据丢失。")
    print("运行此脚本前，请验证以下信息:")
    print("1. 数据库文件路径是否正确")
    print("2. 旧系统路径是否正确")
    print("3. 新系统路径是否正确")
    print("\n执行迁移，请添加--confirm参数:")
    print("python migrate_papers.py --confirm")
    sys.exit(1)

# 直接连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取papers表的所有记录
cursor.execute("SELECT id, file_path FROM papers")
results = cursor.fetchall()

print(f"找到 {len(results)} 条记录")

# 更新计数器
updated_count = 0
copied_count = 0
failed_count = 0
already_ok_count = 0

# 处理每条记录
for record_id, old_path in results:
    # 如果路径已经是相对路径且文件存在，跳过
    if (old_path.startswith('uploads/') or old_path.startswith('uploads\\')) and os.path.exists(old_path):
        already_ok_count += 1
        print(f"ID {record_id}: 已是正确路径 {old_path}")
        continue
    
    # 提取文件名
    file_name = os.path.basename(old_path)
    
    # 检查路径格式，确定相对路径格式
    if 'papers/papers' in old_path.replace('\\', '/') or 'papers\\papers' in old_path:
        rel_path = os.path.join('uploads', 'papers', 'papers', file_name)
    else:
        rel_path = os.path.join('uploads', 'papers', file_name)
    
    # 新文件的绝对路径
    new_abs_path = os.path.join(NEW_SYSTEM_ROOT, rel_path)
    
    # 检查新系统中文件是否已存在
    if os.path.exists(new_abs_path):
        # 更新数据库记录为相对路径
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, record_id))
        print(f"ID {record_id}: 更新路径 {old_path} -> {rel_path} (文件已存在)")
        updated_count += 1
        continue
    
    # 尝试从旧系统复制文件
    file_copied = False
    for old_root in OLD_SYSTEM_ROOTS:
        # 构建可能的旧文件绝对路径
        for old_subpath in [
            old_path,  # 原始路径
            os.path.join(old_root, 'uploads', 'papers', file_name),  # uploads/papers/文件名
            os.path.join(old_root, 'uploads', 'papers', 'papers', file_name)  # uploads/papers/papers/文件名
        ]:
            if os.path.exists(old_subpath):
                # 确保目标目录存在
                os.makedirs(os.path.dirname(new_abs_path), exist_ok=True)
                
                # 复制文件
                try:
                    shutil.copy2(old_subpath, new_abs_path)
                    print(f"ID {record_id}: 复制文件 {old_subpath} -> {new_abs_path}")
                    
                    # 更新数据库记录
                    cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, record_id))
                    print(f"ID {record_id}: 更新路径 {old_path} -> {rel_path}")
                    
                    updated_count += 1
                    copied_count += 1
                    file_copied = True
                    break
                except Exception as e:
                    print(f"ID {record_id}: 复制文件失败 {old_subpath} -> {new_abs_path}: {str(e)}")
        
        if file_copied:
            break
    
    # 如果文件无法复制
    if not file_copied:
        print(f"ID {record_id}: 无法找到或复制文件 {file_name}")
        failed_count += 1

# 提交更改
conn.commit()

# 输出统计信息
print("\n迁移完成!")
print(f"共处理记录: {len(results)}")
print(f"已是正确路径: {already_ok_count}")
print(f"成功更新路径: {updated_count}")
print(f"成功复制文件: {copied_count}")
print(f"处理失败: {failed_count}")

# 关闭连接
conn.close()

print("\n如果有处理失败的记录，请手动检查这些文件。")
print("您也可以运行脚本 fix_file_paths.py 来进一步修复路径问题。") 