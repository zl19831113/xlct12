import os
import sqlite3
import sys

# 配置信息
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')

print(f"数据库路径: {DB_PATH}")

# 直接连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取命令行参数
show_all = True
limit = 20  # 默认显示20条
search_term = None

# 解析命令行参数
for i, arg in enumerate(sys.argv[1:], 1):
    if arg == '--limit' and i < len(sys.argv) - 1:
        try:
            limit = int(sys.argv[i+1])
        except ValueError:
            pass
    elif arg == '--search' and i < len(sys.argv) - 1:
        search_term = sys.argv[i+1]
        show_all = False

# 构建查询
query = "SELECT id, name, file_path, upload_time FROM papers"
params = []

if search_term:
    query += " WHERE name LIKE ? OR file_path LIKE ?"
    params = [f'%{search_term}%', f'%{search_term}%']

query += " ORDER BY id DESC LIMIT ?"
params.append(limit)

# 执行查询
cursor.execute(query, params)
results = cursor.fetchall()

# 显示结果
print(f"\n{'ID':<6} {'名称':<40} {'文件名':<40} {'上传时间'}")
print("-" * 100)

for record_id, name, file_path, upload_time in results:
    # 提取文件名
    file_name = os.path.basename(file_path)
    
    # 截断过长的文本
    if len(name) > 38:
        name = name[:35] + "..."
    if len(file_name) > 38:
        file_name = file_name[:35] + "..."
    
    print(f"{record_id:<6} {name:<40} {file_name:<40} {upload_time}")

print("-" * 100)
print(f"显示 {len(results)} 条记录")

# 如果显示所有记录，提供帮助信息
if show_all:
    print("\n提示:")
    print("查找特定记录: python show_paper_names.py --search <关键词>")
    print("限制显示数量: python show_paper_names.py --limit <数量>")
    print("组合使用: python show_paper_names.py --search <关键词> --limit <数量>")

# 关闭连接
conn.close() 