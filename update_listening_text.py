import sqlite3
import os
import re

# 使用绝对路径
base_dir = '/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang86'
db_path = os.path.join(base_dir, 'instance/xlct12.db')

print(f"尝试连接数据库: {db_path}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找哪些表可能包含我们需要替换的文本
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"数据库中的表: {tables}")

# 替换文本的函数 - 使用正则表达式匹配包含"长对话"的标题
def replace_dialog_titles(table, column):
    try:
        # 查找包含"长对话"的记录总数
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} LIKE '%长对话%'")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"在表 {table} 的列 {column} 中找到 {count} 条包含'长对话'的记录")
            
            # 获取所有包含"长对话"的记录
            cursor.execute(f"SELECT id, {column} FROM {table} WHERE {column} LIKE '%长对话%'")
            records = cursor.fetchall()
            
            # 遍历所有匹配的记录
            for record_id, content in records:
                print(f"处理 ID: {record_id}")
                
                # 原始内容用于日志记录和比较
                original_content = content
                
                # 使用正则表达式查找包含"长对话"的标题部分
                title_matches = re.findall(r'([\d、．\.]*[\s]*听[^，。]*长对话[^，。]*[，。])', content)
                
                if title_matches:
                    for title in title_matches:
                        # 保留原始的序号前缀（如果有）
                        prefix_match = re.match(r'^(\d+[、．\.])', title)
                        prefix = prefix_match.group(0) if prefix_match else ''
                        
                        # 替换为标准格式
                        new_title = prefix + '听下面一段较长对话,回答以下小题。'
                        content = content.replace(title, new_title)
                    
                    # 只在内容实际变化时进行更新
                    if content != original_content:
                        cursor.execute(f"UPDATE {table} SET {column} = ? WHERE id = ?", (content, record_id))
                        print(f"已更新 ID: {record_id} 的内容")
            
            # 提交更改
            conn.commit()
            print(f"已更新表 {table} 中的记录")
            return count
        else:
            print(f"在表 {table} 的列 {column} 中没有找到包含'长对话'的记录")
            return 0
    except sqlite3.Error as e:
        print(f"处理表 {table} 列 {column} 时出错: {e}")
        return 0

# 检查可能包含该文本的列
potential_tables = ['papers', 'su', 'questions']
text_columns = ['question', 'content', 'question_content', 'stem']

total_replaced = 0

# 遍历表和可能的列
for table in potential_tables:
    for column in text_columns:
        try:
            # 检查表是否存在
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                # 检查列是否存在
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [info[1] for info in cursor.fetchall()]
                
                if column in columns:
                    # 检查该列是否有id字段（用于更新）
                    cursor.execute(f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='id'")
                    has_id = cursor.fetchone()[0] > 0
                    
                    if has_id:
                        replaced = replace_dialog_titles(table, column)
                        total_replaced += replaced
                    else:
                        print(f"表 {table} 没有id字段，跳过处理")
        except sqlite3.Error as e:
            print(f"处理表 {table} 时出错: {e}")

print(f"总共处理了 {total_replaced} 条记录")

# 关闭连接
conn.close()
print("数据库操作完成")
