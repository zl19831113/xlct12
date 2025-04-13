import os
import sqlite3
import re
import sys

# 配置信息
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')

print(f"数据库路径: {DB_PATH}")

# 确认操作
if len(sys.argv) < 2 or sys.argv[1] != '--confirm':
    print("警告: 此脚本将修改数据库中的论文名称。")
    print("请确保您已备份数据库，避免数据丢失。")
    print("\n执行修改，请添加--confirm参数:")
    print("python clean_paper_names.py --confirm")
    sys.exit(1)

# 直接连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取papers表的所有记录
cursor.execute("SELECT id, name, file_path FROM papers")
results = cursor.fetchall()

print(f"找到 {len(results)} 条记录")

# 要清理的模式
patterns_to_remove = [
    r'【\s*高考\s*】',  # 【高考】或【 高考 】
    r'-1\b',         # -1（在单词边界处）
    r'（1）',         # （1）
    r'\(1\)',        # (1)
    r'【KS5U\s*高考】',  # 【KS5U高考】
    r'【KS5U】',      # 【KS5U】
    r'【真题】',      # 【真题】
]

# 更新计数器
updated_count = 0
unchanged_count = 0

# 处理每条记录
for record_id, name, file_path in results:
    original_name = name
    
    # 应用每个模式清理
    for pattern in patterns_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # 移除多余的空格
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 如果名称有改变，更新记录
    if name != original_name:
        cursor.execute("UPDATE papers SET name = ? WHERE id = ?", (name, record_id))
        print(f"ID {record_id}: {original_name} -> {name}")
        updated_count += 1
    else:
        unchanged_count += 1

# 提交更改
conn.commit()

# 输出统计信息
print("\n清理完成!")
print(f"共处理记录: {len(results)}")
print(f"已更新: {updated_count}")
print(f"无需更新: {unchanged_count}")

# 关闭连接
conn.close() 