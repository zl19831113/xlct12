#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复app.py中的HTML实体和题目顺序问题
"""

import os
import re
import sys

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
    if "&middot;" not in original_code:
        new_code = original_code.replace(
            '"&mdash;": "—"',
            '"&mdash;": "—",\n        "&middot;": "·"'
        )
        
        # 替换代码
        content = content.replace(original_code, new_code)
        print("已添加&middot;实体处理")
    else:
        print("&middot;实体处理已存在")
    
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
    
    # 检查是否已经修复
    if "question_map" in original_code:
        print("题目顺序问题已修复")
        return content
    
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
    # 获取app.py路径
    app_path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
    
    # 检查文件是否存在
    if not os.path.exists(app_path):
        print(f"错误: 找不到文件 {app_path}")
        sys.exit(1)
    
    # 创建备份
    backup_path = f"{app_path}.bak"
    try:
        with open(app_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 修复HTML实体编码
    content = fix_html_entities(content)
    
    # 修复题目顺序
    content = fix_question_order(content)
    
    # 写回文件
    try:
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复完成，已更新 {app_path}")
    except Exception as e:
        print(f"写入文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
