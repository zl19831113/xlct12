#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 简化版的直接修改脚本，避免使用复杂的正则表达式
# 服务器上执行：python3 direct_fix.py

import os
import shutil
from datetime import datetime

# 备份目录和文件
APP_PATH = '/var/www/question_bank/app.py'
BACKUP_DIR = '/var/www/question_bank/backups'
os.makedirs(BACKUP_DIR, exist_ok=True)

# 备份原始文件
backup_name = f"app.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_path = os.path.join(BACKUP_DIR, backup_name)
shutil.copy2(APP_PATH, backup_path)
print(f"已备份原始文件到: {backup_path}")

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
    elif func_found and line.strip() and len(line) - len(line.lstrip()) <= indent:
        end_line = i
        break

if not func_found:
    print("错误: 找不到find_actual_file_location函数")
    exit(1)

if end_line == -1:
    print("错误: 无法确定函数结束位置")
    exit(1)

print(f"找到函数: 第{start_line+1}行到第{end_line}行")

# 替换函数的新代码
new_function = [
    "def find_actual_file_location(file_name, paper_info=None):\n",
    "    \"\"\"\n",
    "    查找文件的实际位置，更灵活地处理下划线连字符等特殊字符\n",
    "    \n",
    "    Args:\n",
    "        file_name: 文件名\n",
    "        paper_info: 可选的试卷信息字典，包含id, name, year, subject, region等字段\n",
    "    \n",
    "    Returns:\n",
    "        找到的文件路径，如果未找到则返回None\n",
    "    \"\"\"\n",
    "    if not file_name:\n",
    "        return None\n",
    "    \n",
    "    # 获取项目根目录\n",
    "    project_root = os.path.dirname(os.path.abspath(__file__))\n",
    "    \n",
    "    # 可能的文件位置优先级列表\n",
    "    search_dirs = [\n",
    "        os.path.join(project_root, 'uploads', 'papers'),\n",
    "        os.path.join(project_root, 'uploads', 'papers', 'papers'),\n",
    "        os.path.join(project_root, 'uploads')\n",
    "    ]\n",
    "    \n",
    "    # 1. 首先尝试直接匹配文件名，不考虑下划线差异\n",
    "    for search_dir in search_dirs:\n",
    "        if os.path.exists(search_dir):\n",
    "            # 直接路径匹配\n",
    "            full_path = os.path.join(search_dir, file_name)\n",
    "            if os.path.isfile(full_path):\n",
    "                return full_path\n",
    "            \n",
    "            # 将下划线替换为连字符再匹配\n",
    "            dash_name = file_name.replace('_', '-')\n",
    "            if dash_name != file_name:\n",
    "                dash_path = os.path.join(search_dir, dash_name)\n",
    "                if os.path.isfile(dash_path):\n",
    "                    return dash_path\n",
    "            \n",
    "            # 将连字符替换为下划线再匹配\n",
    "            underscore_name = file_name.replace('-', '_')\n",
    "            if underscore_name != file_name:\n",
    "                underscore_path = os.path.join(search_dir, underscore_name)\n",
    "                if os.path.isfile(underscore_path):\n",
    "                    return underscore_path\n",
    "    \n",
    "    # 2. 如果直接匹配失败，尝试在所有目录中深度搜索\n",
    "    all_files = []\n",
    "    for search_dir in search_dirs:\n",
    "        if os.path.exists(search_dir):\n",
    "            for root, _, files in os.walk(search_dir):\n",
    "                for f in files:\n",
    "                    if f.endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):\n",
    "                        all_files.append(os.path.join(root, f))\n",
    "    \n",
    "    # 如果提供了试卷信息，可以使用更高级的匹配算法\n",
    "    if paper_info:\n",
    "        # 优先使用ID匹配\n",
    "        if 'id' in paper_info:\n",
    "            id_pattern = f\"_{paper_info['id']}_\"\n",
    "            id_matches = [f for f in all_files if id_pattern in os.path.basename(f)]\n",
    "            if id_matches:\n",
    "                return id_matches[0]\n",
    "    \n",
    "    # 3. 尝试基于部分文件名匹配\n",
    "    file_base = os.path.splitext(file_name)[0]\n",
    "    for file_path in all_files:\n",
    "        if file_base in os.path.basename(file_path):\n",
    "            return file_path\n",
    "    \n",
    "    # 4. 尝试使用数字前缀进行匹配\n",
    "    if file_name.startswith('20'):\n",
    "        prefix = file_name.split('_')[0] if '_' in file_name else file_name[:8]\n",
    "        for file_path in all_files:\n",
    "            if os.path.basename(file_path).startswith(prefix):\n",
    "                return file_path\n",
    "    \n",
    "    # 如果都失败了，返回None\n",
    "    return None\n"
]

# 修改内容
modified_content = content[:start_line] + new_function + content[end_line:]

# 写回文件
with open(APP_PATH, 'w', encoding='utf-8') as f:
    f.writelines(modified_content)

print(f"成功修改函数，替换了 {end_line - start_line} 行代码")
print("请重启服务使改动生效:")
print("  cd /var/www/question_bank")
print("  pkill -f gunicorn")
print("  /var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app -D")
print("  systemctl restart nginx") 