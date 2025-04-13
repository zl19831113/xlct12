#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re

# 使用绝对路径
base_dir = '/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang86'
db_path = os.path.join(base_dir, 'instance/xlct12.db')
upload_folder = os.path.join(base_dir, 'uploads/papers/audio')

print(f"连接数据库: {db_path}")
print(f"音频文件夹: {upload_folder}")

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找数据库中的记录
def find_records():
    # 先查看表结构
    cursor.execute("PRAGMA table_info(su)")
    columns = cursor.fetchall()
    print(f"表 su 的列: {[col[1] for col in columns]}")
    
    # 查找su表中所有记录数
    cursor.execute("SELECT COUNT(*) FROM su")
    total_count = cursor.fetchone()[0]
    print(f"su表中总记录数: {total_count}")
    
    # 查找必修二英语相关记录
    cursor.execute("SELECT COUNT(*) FROM su WHERE textbook LIKE '%必修%2%' OR textbook LIKE '%必修二%' OR textbook LIKE '%Book 2%'")
    module2_count = cursor.fetchone()[0]
    print(f"必修二相关记录数: {module2_count}")
    
    # 查找更广泛的听力对话相关记录
    query = """
    SELECT id, textbook, question, audio_file_path, audio_filename 
    FROM su 
    WHERE (
        textbook LIKE '%必修%2%' OR 
        textbook LIKE '%必修二%' OR
        textbook LIKE '%Book 2%'
    ) 
    AND subject = '英语'
    AND (
        question LIKE '%听%对话%' OR
        question LIKE '%听力%' OR
        question LIKE '%listening%' OR
        question LIKE '%dialog%'
    )
    """
    
    cursor.execute(query)
    records = cursor.fetchall()
    
    if not records:
        print("未找到符合条件的记录")
        return []
        
    print(f"找到 {len(records)} 条符合条件的记录")
    for idx, record in enumerate(records, 1):
        record_id, textbook, question, audio_path, audio_filename = record
        print(f"{idx}. ID: {record_id}")
        print(f"   教材: {textbook}")
        print(f"   问题: {question[:100]}...")
        print(f"   音频: {audio_path}")
        print("---")
    
    return records

# 删除数据库中的记录及关联的MP3文件
def delete_records_and_audio(records):
    deleted_count = 0
    audio_deleted = 0
    failed_audio_files = []
    
    for record in records:
        record_id, textbook, question, audio_path, audio_filename = record
        
        print(f"\n处理ID: {record_id}")
        print(f"教材: {textbook}")
        print(f"问题: {question[:50]}...")  # 仅显示前50个字符
        
        # 显示确认信息
        print(f"确认删除ID为 {record_id} 的记录")
        
        # 删除关联的音频文件
        if audio_path and os.path.exists(os.path.join(base_dir, audio_path)):
            try:
                os.remove(os.path.join(base_dir, audio_path))
                print(f"已删除音频文件: {audio_path}")
                audio_deleted += 1
            except Exception as e:
                print(f"删除音频文件失败: {e}")
                failed_audio_files.append(audio_path)
        elif audio_path:
            print(f"音频文件不存在: {audio_path}")
            failed_audio_files.append(audio_path)
        else:
            print("记录无关联音频文件")
            
        # 从数据库中删除记录
        try:
            cursor.execute("DELETE FROM su WHERE id = ?", (record_id,))
            deleted_count += 1
            print(f"已从数据库删除ID为 {record_id} 的记录")
        except Exception as e:
            print(f"删除记录失败: {e}")
    
    # 提交更改
    conn.commit()
    
    print(f"\n删除操作完成")
    print(f"共删除 {deleted_count} 条数据库记录")
    print(f"共删除 {audio_deleted} 个音频文件")
    
    if failed_audio_files:
        print(f"有 {len(failed_audio_files)} 个音频文件未能删除:")
        for path in failed_audio_files:
            print(f" - {path}")

def main():
    try:
        print("开始查找必修二英语听力对话相关记录...")
        records = find_records()
        
        if records:
            # 自动筛选出短对话选答案的记录
            filtered_records = []
            for record in records:
                _, _, question, _, _ = record
                if "短对话" in question and ("选" in question or "答案" in question):
                    filtered_records.append(record)
            
            print(f"筛选出 {len(filtered_records)} 条'听短对话选答案'相关记录")
            
            if filtered_records:
                print("\n即将删除'听短对话选答案'相关记录及其关联的音频文件...")
                delete_records_and_audio(filtered_records)
            else:
                print("未找到'听短对话选答案'相关记录")
                
                # 如果没有找到明确的"短对话选答案"，尝试更宽松的条件
                print("\n尝试使用更宽松的条件查找相关记录...")
                broader_records = []
                for record in records:
                    _, _, question, _, _ = record
                    # 只要包含"听"和"对话"，且包含"选择"或"答案"字样
                    if "听" in question and "对话" in question and ("选择" in question or "答案" in question):
                        broader_records.append(record)
                
                print(f"使用宽松条件筛选出 {len(broader_records)} 条相关记录")
                if broader_records:
                    print("\n即将删除这些相关记录及其关联的音频文件...")
                    delete_records_and_audio(broader_records)
                else:
                    print("使用宽松条件也未找到相关记录")
        else:
            print("没有找到需要删除的记录")
            
    except Exception as e:
        print(f"操作过程中出错: {e}")
    finally:
        # 关闭连接
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()
