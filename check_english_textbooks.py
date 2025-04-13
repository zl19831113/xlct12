#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

# 使用绝对路径
base_dir = '/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang86'
db_path = os.path.join(base_dir, 'instance/xlct12.db')

print(f"连接数据库: {db_path}")

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"数据库中的表: {[table[0] for table in tables]}")

# 查找英语学科的记录
print("\n查找英语学科记录...")
try:
    cursor.execute("SELECT COUNT(*) FROM su WHERE subject='英语'")
    count = cursor.fetchone()[0]
    print(f"英语学科记录总数: {count}")
    
    # 统计英语教材分布
    cursor.execute("SELECT textbook, COUNT(*) FROM su WHERE subject='英语' GROUP BY textbook ORDER BY COUNT(*) DESC")
    textbooks = cursor.fetchall()
    print("\n英语教材分布:")
    for textbook, count in textbooks:
        print(f"  {textbook}: {count}条记录")
    
    # 查找可能的必修二记录
    print("\n可能的必修二记录:")
    for keyword in ['必修二', '必修 二', '必修2', '必修 2', 'Book 2', 'Module 2']:
        cursor.execute(f"SELECT COUNT(*) FROM su WHERE subject='英语' AND textbook LIKE '%{keyword}%'")
        count = cursor.fetchone()[0]
        print(f"  包含'{keyword}'的记录: {count}条")
    
    # 查找听力对话相关记录
    print("\n听力对话相关记录:")
    cursor.execute("SELECT COUNT(*) FROM su WHERE subject='英语' AND (question LIKE '%听%对话%' OR question LIKE '%listening%' OR question LIKE '%dialog%')")
    count = cursor.fetchone()[0]
    print(f"  听力对话相关记录: {count}条")
    
    # 如果有听力对话相关记录，查看前5条
    if count > 0:
        cursor.execute("SELECT id, textbook, question FROM su WHERE subject='英语' AND (question LIKE '%听%对话%' OR question LIKE '%listening%' OR question LIKE '%dialog%') LIMIT 5")
        samples = cursor.fetchall()
        print("\n听力对话记录样例:")
        for id, textbook, question in samples:
            print(f"  ID: {id}")
            print(f"  教材: {textbook}")
            print(f"  问题: {question[:100]}...")
            print("---")
    
    # 查找音频文件相关记录
    print("\n音频文件相关记录:")
    cursor.execute("SELECT COUNT(*) FROM su WHERE subject='英语' AND audio_file_path IS NOT NULL AND audio_file_path != ''")
    count = cursor.fetchone()[0]
    print(f"  包含音频文件的记录: {count}条")
    
    # 如果有音频文件相关记录，查看前5条
    if count > 0:
        cursor.execute("SELECT id, textbook, question, audio_file_path FROM su WHERE subject='英语' AND audio_file_path IS NOT NULL AND audio_file_path != '' LIMIT 5")
        samples = cursor.fetchall()
        print("\n音频文件记录样例:")
        for id, textbook, question, audio_path in samples:
            print(f"  ID: {id}")
            print(f"  教材: {textbook}")
            print(f"  问题: {question[:100]}...")
            print(f"  音频: {audio_path}")
            print("---")
    
except Exception as e:
    print(f"查询出错: {e}")
finally:
    # 关闭连接
    conn.close()
    print("\n数据库连接已关闭")
