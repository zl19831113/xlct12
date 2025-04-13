#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLAlchemy 2.0 兼容性修复脚本
修复 db.case() 函数的调用方式，适配 SQLAlchemy 2.0 的新语法
"""

import re
import os
import sys
import shutil
from datetime import datetime

# 要修改的文件
APP_FILE = 'app.py'

def backup_file(file_path):
    """创建备份文件"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{file_path}.bak_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"已创建备份: {backup_path}")
    return backup_path

def fix_case_syntax(content):
    """修复 SQLAlchemy case() 函数的语法"""
    # 创建一个函数，处理括号匹配和提取语句
    def extract_between_brackets(text, start_pos, open_char='(', close_char=')'):
        """提取括号内的内容，处理嵌套括号"""
        level = 0
        start = None
        for i in range(start_pos, len(text)):
            if text[i] == open_char:
                if level == 0:
                    start = i
                level += 1
            elif text[i] == close_char:
                level -= 1
                if level == 0 and start is not None:
                    return text[start+1:i], i+1
        return "", len(text)

    # 查找所有 db.case([ 的位置
    case_positions = []
    for m in re.finditer(r'db\.case\(\[', content):
        case_positions.append(m.start())
    
    # 如果没有找到匹配项，返回原始内容
    if not case_positions:
        return content
    
    # 逐个处理每个匹配项
    chunks = []
    last_pos = 0
    
    for pos in case_positions:
        # 添加之前未处理的内容
        chunks.append(content[last_pos:pos])
        
        # 提取整个 case 表达式
        case_start = pos + 8  # len("db.case([")
        inner_content, close_pos = extract_between_brackets(content, pos, '(', ')')
        
        # 检查是否有匹配的内容
        if inner_content and inner_content.startswith('['):
            # 去掉开头的 [ 和结尾的 ]
            inner_content = inner_content[1:-1]
            
            # 检查是否有 else_ 参数
            if 'else_=' in inner_content:
                parts = inner_content.rsplit(', else_=', 1)
                items_part = parts[0]
                else_part = parts[1] if len(parts) > 1 else '0'
                
                # 创建新的 case 表达式
                new_expr = f"db.case({items_part}, else_={else_part})"
                chunks.append(new_expr)
            else:
                # 没有 else_ 参数的情况
                new_expr = f"db.case({inner_content})"
                chunks.append(new_expr)
        else:
            # 如果提取失败，保留原始表达式
            chunks.append(content[pos:close_pos])
        
        # 更新处理位置
        last_pos = close_pos
    
    # 添加最后剩余的内容
    chunks.append(content[last_pos:])
    
    # 合并结果
    return ''.join(chunks)

def main():
    print("开始修复 SQLAlchemy case() 函数语法...")
    
    # 确保文件存在
    if not os.path.exists(APP_FILE):
        print(f"错误: 找不到 {APP_FILE} 文件")
        return 1
    
    # 备份原始文件
    backup_file(APP_FILE)
    
    # 读取文件内容
    with open(APP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复语法
    fixed_content = fix_case_syntax(content)
    
    # 写回文件
    with open(APP_FILE, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"已成功修复 {APP_FILE} 中的 SQLAlchemy case() 函数语法")
    print("请同步更新后的文件到服务器")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
