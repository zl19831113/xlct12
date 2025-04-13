#!/usr/bin/env python3
# 修复app.py中的db.case语法问题
import re
import os
import datetime

# 备份原始文件
def backup_file(file_path):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{file_path}.bak_{timestamp}"
    with open(file_path, 'r', encoding='utf-8') as src:
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    print(f"原文件已备份为: {backup_path}")

# 修复db.case语法
def fix_case_syntax(content):
    # 替换列表风格的case为单独参数风格
    # 匹配类似 db.case([(condition, value)], else_=0)
    case_list_pattern = r'db\.case\(\[\s*\((.+?),\s*(\d+)\)\s*\],\s*else_=(\d+)\)'
    fixed_content = re.sub(case_list_pattern, r'db.case((\1, \2), else_=\3)', content)
    
    # 匹配类似 db.case([(...), (...),...], else_=0)
    case_multi_list_pattern = r'db\.case\(\[\s*\((.+?),\s*(\d+)\)\s*,\s*\((.+?),\s*(\d+)\)\s*\],\s*else_=(\d+)\)'
    fixed_content = re.sub(case_multi_list_pattern, r'db.case((\1, \2), (\3, \4), else_=\5)', fixed_content)
    
    # 处理带有第三个条件的情况
    case_three_list_pattern = r'db\.case\(\[\s*\((.+?),\s*(\d+)\)\s*,\s*\((.+?),\s*(\d+)\)\s*,\s*\((.+?),\s*(\d+)\)\s*\],\s*else_=(\d+)\)'
    fixed_content = re.sub(case_three_list_pattern, r'db.case((\1, \2), (\3, \4), (\5, \6), else_=\7)', fixed_content)
    
    return fixed_content

def main():
    file_path = 'app.py'
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        return
    
    # 备份原始文件
    backup_file(file_path)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复语法
    fixed_content = fix_case_syntax(content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"已修复 {file_path} 中的db.case语法")

if __name__ == "__main__":
    main() 