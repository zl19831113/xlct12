#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复试卷生成中的两个问题：
1. HTML实体编码(&middot;)显示问题
2. 题目顺序问题（确保按照选择顺序排列题目）
"""

import os
import re
import sys

# 服务器上app.py的路径
APP_PATH = "/var/www/question_bank/app.py"
# 本地备份路径
BACKUP_PATH = "/var/www/question_bank/app.py.bak"

def create_backup(file_path, backup_path):
    """创建备份文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
        return content
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)

def fix_html_entities(content):
    """修复HTML实体编码处理"""
    # 查找clean_and_split_question函数中的HTML实体替换部分
    pattern = r'(# 1\) 去除常见HTML实体和多余空格换行\n\s+replacements = \{[^}]+\})'
    
    # 检查是否找到匹配
    match = re.search(pattern, content)
    if not match:
        print("无法找到HTML实体替换代码段")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 添加&middot;的处理
    new_code = original_code.replace(
        '"&mdash;": "—"',
        '"&mdash;": "—",\n        "&middot;": "·"'
    )
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已添加&middot;实体处理")
    
    return content

def fix_question_order(content):
    """修复题目顺序问题"""
    # 查找generate_paper函数中的题目查询部分
    pattern = r'(question_ids = request\.json\.get\(\'question_ids\', \[\]\).*?\n.*?questions = SU\.query\.filter\(SU\.id\.in_\(question_ids\)\)\.all\(\))'
    
    # 检查是否找到匹配
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("无法找到题目查询代码段")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 新代码：保持原始顺序
    new_code = """question_ids = request.json.get('question_ids', [])
        paper_title = request.json.get('paper_title', '试卷')
        
        # 查询所有题目
        all_questions = SU.query.filter(SU.id.in_(question_ids)).all()
        
        # 创建ID到题目的映射
        question_map = {q.id: q for q in all_questions}
        
        # 按照原始顺序排列题目
        questions = [question_map[qid] for qid in question_ids if qid in question_map]"""
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已修复题目顺序问题")
    
    return content

def main():
    """主函数"""
    # 检查文件是否存在
    if not os.path.exists(APP_PATH):
        print(f"错误: 找不到文件 {APP_PATH}")
        sys.exit(1)
    
    # 创建备份
    content = create_backup(APP_PATH, BACKUP_PATH)
    
    # 修复HTML实体编码
    content = fix_html_entities(content)
    
    # 修复题目顺序
    content = fix_question_order(content)
    
    # 写回文件
    try:
        with open(APP_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复完成，已更新 {APP_PATH}")
    except Exception as e:
        print(f"写入文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
