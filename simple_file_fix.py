#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import datetime

# 服务器端路径
APP_PY_PATH = '/var/www/question_bank/app.py'
BACKUP_DIR = '/var/www/question_bank/backups'

# 确保备份目录存在
os.makedirs(BACKUP_DIR, exist_ok=True)

# 备份app.py
backup_path = os.path.join(BACKUP_DIR, f"app.py.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
print(f"备份app.py到: {backup_path}")
shutil.copy2(APP_PY_PATH, backup_path)

# 新的函数定义
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
    def clean_name(name):
        name_no_ext = os.path.splitext(name)[0]
        return re.sub(r'[^\\w\\u4e00-\\u9fff]', '', name_no_ext).lower()
    
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

# 读取app.py
print("读取app.py文件...")
with open(APP_PY_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到find_actual_file_location函数的定义位置
print("查找find_actual_file_location函数...")
start_pattern = "def find_actual_file_location"
end_pattern = "# 添加papers路由和函数"

start_pos = content.find(start_pattern)
end_pos = content.find(end_pattern)

if start_pos == -1:
    print("错误: 找不到find_actual_file_location函数")
    exit(1)

if end_pos == -1:
    print("错误: 找不到函数后的标记，无法确定范围")
    exit(1)

# 找到函数定义的完整范围
function_text = content[start_pos:end_pos]
function_end = 0

# 寻找函数的结束位置
lines = function_text.split('\n')
indent_level = None
for i, line in enumerate(lines):
    if i == 0:  # 首行，确定缩进级别
        indent_level = len(line) - len(line.lstrip())
        continue
    
    if line.strip() and len(line) - len(line.lstrip()) <= indent_level:
        function_end = sum(len(l) + 1 for l in lines[:i])
        break

if function_end == 0:
    function_end = len(function_text)

# 截取函数范围
function_full = function_text[:function_end].strip()
print(f"原函数长度: {len(function_full)}字符")

# 替换函数
modified_content = content.replace(function_full, new_function.strip())

# 写回文件
print("写入修改后的文件...")
with open(APP_PY_PATH, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("\n修复完成！请重启Gunicorn服务使更改生效:")
print("  cd /var/www/question_bank")
print("  pkill -f gunicorn")
print("  /var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app -D")
print("  systemctl restart nginx") 