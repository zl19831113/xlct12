import os
import sqlite3
import re
import sys
import shutil

# 配置信息
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"数据库路径: {DB_PATH}")
print(f"基础目录: {BASE_DIR}")

# 确认操作
if len(sys.argv) < 2 or sys.argv[1] != '--confirm':
    print("警告: 此脚本将修改数据库中的论文名称和文件名。")
    print("请确保您已备份数据库和文件，避免数据丢失。")
    print("脚本功能:")
    print("1. 清理数据库中论文名称中的特定字样")
    print("2. 如果指定了--rename-files参数，将重命名实际文件")
    print("\n执行清理名称，请添加--confirm参数:")
    print("python clean_paper_files.py --confirm")
    print("\n同时重命名文件，请添加--rename-files参数:")
    print("python clean_paper_files.py --confirm --rename-files")
    sys.exit(1)

# 是否重命名文件
rename_files = "--rename-files" in sys.argv

# 直接连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取papers表的所有记录
cursor.execute("SELECT id, name, file_path FROM papers")
results = cursor.fetchall()

print(f"找到 {len(results)} 条记录")
print(f"重命名文件: {'是' if rename_files else '否'}")

# 要清理的模式
patterns_to_remove = [
    r'【\s*高考\s*】',  # 【高考】或【 高考 】
    r'-1\b',         # -1（在单词边界处）
    r'（1）',         # （1）
    r'\(1\)',        # (1)
    r'【KS5U\s*高考】',  # 【KS5U高考】
    r'【KS5U】',      # 【KS5U】
    r'【真题】',      # 【真题】
    r'ks5u',         # ks5u（不区分大小写）
]

# 更新计数器
name_updated_count = 0
file_renamed_count = 0
file_rename_failed_count = 0
unchanged_count = 0

# 处理每条记录
for record_id, name, file_path in results:
    original_name = name
    
    # 清理论文名称
    cleaned_name = name
    for pattern in patterns_to_remove:
        cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
    
    # 移除多余的空格
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
    
    # 名称有改变
    name_changed = cleaned_name != original_name
    
    # 文件重命名处理
    file_renamed = False
    if rename_files and os.path.exists(file_path):
        # 处理绝对路径和相对路径
        if file_path.startswith('/'):
            full_path = file_path
        else:
            full_path = os.path.join(BASE_DIR, file_path)
        
        # 如果文件存在
        if os.path.exists(full_path):
            # 分解路径获取文件名
            dir_path = os.path.dirname(full_path)
            file_name = os.path.basename(full_path)
            file_ext = os.path.splitext(file_name)[1]
            
            # 提取时间戳部分 (例如 20250303_211456_12_)
            timestamp_match = re.match(r'(\d{8}_\d{6}_\d+_)(.*)', file_name)
            
            if timestamp_match:
                timestamp_prefix = timestamp_match.group(1)
                rest_of_name = timestamp_match.group(2)
                
                # 清理文件名中间部分
                cleaned_file_middle = rest_of_name
                for pattern in patterns_to_remove:
                    cleaned_file_middle = re.sub(pattern, '', cleaned_file_middle, flags=re.IGNORECASE)
                
                # 移除多余的空格
                cleaned_file_middle = re.sub(r'\s+', ' ', cleaned_file_middle).strip()
                
                # 构建新文件名
                new_file_name = timestamp_prefix + cleaned_file_middle
                new_full_path = os.path.join(dir_path, new_file_name)
                
                # 如果文件名有变化且新文件名不存在
                if new_full_path != full_path and not os.path.exists(new_full_path):
                    try:
                        # 重命名文件
                        shutil.move(full_path, new_full_path)
                        
                        # 更新数据库中的文件路径
                        if file_path.startswith('/'):
                            new_file_path = new_full_path
                        else:
                            # 保持相对路径
                            new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
                        
                        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", 
                                      (new_file_path, record_id))
                        
                        print(f"ID {record_id}: 重命名文件 {file_name} -> {new_file_name}")
                        file_renamed = True
                        file_renamed_count += 1
                    except Exception as e:
                        print(f"ID {record_id}: 重命名文件失败 {full_path}: {str(e)}")
                        file_rename_failed_count += 1
    
    # 更新论文名称（如果有变化）
    if name_changed:
        cursor.execute("UPDATE papers SET name = ? WHERE id = ?", (cleaned_name, record_id))
        print(f"ID {record_id}: 更新名称 {original_name} -> {cleaned_name}")
        name_updated_count += 1
    
    if not name_changed and not file_renamed:
        unchanged_count += 1

# 提交更改
conn.commit()

# 输出统计信息
print("\n清理完成!")
print(f"共处理记录: {len(results)}")
print(f"名称已更新: {name_updated_count}")
if rename_files:
    print(f"文件已重命名: {file_renamed_count}")
    print(f"文件重命名失败: {file_rename_failed_count}")
print(f"无需更新: {unchanged_count}")

# 关闭连接
conn.close() 