import sqlite3
import re
import os

# 数据库文件路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'xlct12.db')

print(f"使用数据库: {db_path}")
print(f"数据库文件是否存在: {os.path.exists(db_path)}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 要搜索的字符串
search_text = "听下面一段对话，回答以下小题。"
replace_text = "听下面一段较长对话,回答以下小题。"

# 在su表格中查找并替换此文本
try:
    # 首先获取所有包含"段对话"的条目（但不包括已经包含"较长对话"的条目）
    cursor.execute(
        "SELECT id, question FROM su WHERE question LIKE '%段对话%' AND question NOT LIKE '%较长对话%'"
    )
    rows = cursor.fetchall()
    
    print(f"找到 {len(rows)} 条包含 '段对话' 但不包含 '较长对话' 的记录")
    
    # 更新计数器
    updated_count = 0
    
    # 遍历所有匹配的记录
    for row_id, question in rows:
        if search_text in question:
            # 直接替换为新文本
            new_question = question.replace(search_text, replace_text)
            cursor.execute("UPDATE su SET question = ? WHERE id = ?", (new_question, row_id))
            updated_count += 1
            print(f"更新 ID {row_id}: 将文本 '{search_text}' 替换为 '{replace_text}'")
    
    print(f"总共更新了 {updated_count} 条记录")
    
    # 提交更改
    conn.commit()
    print("更改已保存到数据库")
    
except sqlite3.Error as e:
    conn.rollback()
    print(f"数据库操作错误: {e}")
finally:
    # 关闭数据库连接
    conn.close()
    print("数据库连接已关闭")
