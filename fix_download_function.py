#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接修复 find_actual_file_location 函数的简化脚本
使用方法: 在服务器上运行 python3 fix_download_function.py
"""

import os
import shutil
from datetime import datetime

# 服务器路径
APP_PATH = '/var/www/question_bank/app.py'
BACKUP_DIR = '/var/www/question_bank/backups'

# 确保备份目录存在
os.makedirs(BACKUP_DIR, exist_ok=True)

# 备份原始文件
backup_name = f"app.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_path = os.path.join(BACKUP_DIR, backup_name)
shutil.copy2(APP_PATH, backup_path)
print(f"已备份原始文件到: {backup_path}")

# 新的函数定义 - 注意所有正则表达式中的 \w 改为 [\\w]，避免错误
new_function = '''
def find_actual_file_location(file_name, paper_info=None):
    """
    查找文件的实际位置，更灵活地处理下划线和连字符等特殊字符
    
    Args:
        file_name: 文件名
        paper_info: 可选的试卷信息字典，包含id, name, year, subject, region等字段
    
    Returns:
        找到的文件路径，如果未找到则返回None
    """
    if not file_name:
        return None
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 可能的文件位置优先级列表
    search_dirs = [
        os.path.join(project_root, 'uploads', 'papers'),
        os.path.join(project_root, 'uploads', 'papers', 'papers'),
        os.path.join(project_root, 'uploads')
    ]
    
    # 1. 首先尝试直接匹配文件名，不考虑下划线差异
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            # 直接路径匹配
            full_path = os.path.join(search_dir, file_name)
            if os.path.isfile(full_path):
                return full_path
            
            # 将下划线替换为连字符再匹配
            dash_name = file_name.replace('_', '-')
            if dash_name != file_name:
                dash_path = os.path.join(search_dir, dash_name)
                if os.path.isfile(dash_path):
                    return dash_path
            
            # 将连字符替换为下划线再匹配
            underscore_name = file_name.replace('-', '_')
            if underscore_name != file_name:
                underscore_path = os.path.join(search_dir, underscore_name)
                if os.path.isfile(underscore_path):
                    return underscore_path
    
    # 2. 如果直接匹配失败，尝试更灵活的模式匹配
    # 创建一个清理后的文件名（去除所有特殊字符，仅保留字母、数字和中文）
    import re
    def clean_name(name):
        name_no_ext = os.path.splitext(name)[0]
        return re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', name_no_ext).lower()
    
    clean_file_name = clean_name(file_name)
    
    # 如果清理后的文件名非空，尝试模糊匹配
    if clean_file_name:
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for existing_file in os.listdir(search_dir):
                    if os.path.isfile(os.path.join(search_dir, existing_file)):
                        # 如果清理后的名称匹配，返回该文件
                        if clean_name(existing_file) == clean_file_name:
                            return os.path.join(search_dir, existing_file)
    
    # 3. 如果模糊匹配也失败，且提供了文件ID信息，尝试匹配ID部分
    if paper_info and 'id' in paper_info:
        paper_id = str(paper_info['id'])
        # 提取文件名开头的数字部分
        id_pattern = f"_{paper_id}_"
        
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for existing_file in os.listdir(search_dir):
                    # 检查文件名中是否包含ID
                    if id_pattern in existing_file:
                        return os.path.join(search_dir, existing_file)
    
    # 4. 最后的尝试: 如果文件名以数字开头（如时间戳格式），尝试匹配前缀
    import re
    num_prefix_match = re.match(r'^(\\d+)', file_name)
    if num_prefix_match:
        prefix = num_prefix_match.group(1)
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for existing_file in os.listdir(search_dir):
                    if existing_file.startswith(prefix):
                        return os.path.join(search_dir, existing_file)
    
    # 所有尝试都失败，返回None
    return None
'''

# 读取原始文件
with open(APP_PATH, 'r', encoding='utf-8') as f:
    content = f.readlines()

# 查找find_actual_file_location函数
func_found = False
start_line = -1
end_line = -1
indent = 0

for i, line in enumerate(content):
    if 'def find_actual_file_location' in line and not func_found:
        func_found = True
        start_line = i
        # 确定函数缩进级别
        indent = len(line) - len(line.lstrip())
    elif func_found and line.strip() == 'return None':
        if i+1 < len(content) and len(content[i+1].strip()) == 0:
            end_line = i + 1
            break
        else:
            end_line = i
            break

if not func_found:
    print("错误: 未找到find_actual_file_location函数")
    exit(1)

print(f"找到函数位置: 行 {start_line+1} 到 {end_line+1}")

# 准备新的函数内容（保持正确的缩进）
new_function_lines = new_function.strip().split('\n')
indented_lines = [' ' * indent + line for line in new_function_lines]

# 替换函数
new_content = content[:start_line] + indented_lines + content[end_line+1:]

# 写回文件
with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.writelines([line + '\n' for line in new_content])

print("函数已成功替换")
print("\n修复完成！请重启Gunicorn服务使更改生效:")
print("  cd /var/www/question_bank")
print("  pkill -f gunicorn")
print("  /var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app -D")
print("  systemctl restart nginx") 