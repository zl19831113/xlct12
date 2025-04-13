#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
from datetime import datetime

# 使用绝对路径
base_dir = '/Volumes/小鹿出题/小鹿备份/4月4 日81/zujuanwang86'
db_path = os.path.join(base_dir, 'instance/xlct12.db')
upload_folder = os.path.join(base_dir, 'uploads/papers/audio')

print(f"连接数据库: {db_path}")
print(f"音频文件夹: {upload_folder}")

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 设置今天的日期字符串，用于匹配今天上传的文件
today_date = datetime.now().strftime('%Y%m%d')
print(f"当前日期: {today_date}")

# 查找最近上传的听力对话记录
def find_recent_listening_dialogs():
    # 查找所有听短对话选择题，且音频文件路径中包含今天日期的记录
    query = """
    SELECT id, textbook, question, audio_file_path, audio_filename 
    FROM su 
    WHERE subject = '英语'
    AND question LIKE '%听%对话%'
    AND audio_file_path LIKE ?
    ORDER BY id
    """
    
    cursor.execute(query, (f'%{today_date}%',))
    records = cursor.fetchall()
    
    if not records:
        print("未找到今天上传的听力对话记录")
        return []
        
    print(f"找到 {len(records)} 条今天上传的听力对话记录")
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
        print(f"问题: {question[:50]}...")
        
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

def find_short_dialog_records():
    # 查找所有听短对话选择题的记录
    query = """
    SELECT id, textbook, question, audio_file_path, audio_filename 
    FROM su 
    WHERE subject = '英语'
    AND (
        question LIKE '%听短对话%' OR
        question LIKE '%听下面%短对话%'
    )
    AND question LIKE '%选%'
    AND audio_file_path IS NOT NULL
    ORDER BY id
    """
    
    cursor.execute(query)
    records = cursor.fetchall()
    
    if not records:
        print("未找到'听短对话选答案'相关记录")
        return []
        
    print(f"找到 {len(records)} 条'听短对话选答案'相关记录")
    for idx, record in enumerate(records, 1):
        record_id, textbook, question, audio_path, audio_filename = record
        print(f"{idx}. ID: {record_id}")
        print(f"   教材: {textbook}")
        print(f"   问题: {question[:100]}...")
        print(f"   音频: {audio_path}")
        print("---")
    
    return records

def main():
    try:
        print("\n方法1: 查找今天上传的听力对话记录...")
        recent_records = find_recent_listening_dialogs()
        
        if recent_records:
            print("\n即将删除今天上传的听力对话记录及其关联的音频文件...")
            delete_records_and_audio(recent_records)
        else:
            print("未找到今天上传的听力对话记录")
            
            print("\n方法2: 查找所有'听短对话选答案'相关记录...")
            short_dialog_records = find_short_dialog_records()
            
            if short_dialog_records:
                print("\n即将删除所有'听短对话选答案'相关记录及其关联的音频文件...")
                delete_records_and_audio(short_dialog_records)
            else:
                print("未找到'听短对话选答案'相关记录")
                print("请确认数据库中是否存在需要删除的记录")
                
    except Exception as e:
        print(f"操作过程中出错: {e}")
    finally:
        # 关闭连接
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()
