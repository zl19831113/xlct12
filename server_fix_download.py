#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import shutil
import sqlite3
import time
from datetime import datetime

# 服务器端路径
SERVER_ROOT = '/var/www/question_bank'
DB_PATH = os.path.join(SERVER_ROOT, 'instance', 'xlct12.db')
PAPERS_DIR = os.path.join(SERVER_ROOT, 'uploads', 'papers')
BACKUP_DIR = os.path.join(SERVER_ROOT, 'backups')

# 确保备份目录存在
os.makedirs(BACKUP_DIR, exist_ok=True)

print(f"===== 文件下载修复脚本 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
print(f"数据库路径: {DB_PATH}")
print(f"试卷目录: {PAPERS_DIR}")

# 连接数据库
print("连接数据库...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 备份数据库
backup_db_path = os.path.join(BACKUP_DIR, f"xlct12.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
print(f"备份数据库到: {backup_db_path}")
shutil.copy2(DB_PATH, backup_db_path)

# 获取所有试卷记录
print("获取所有试卷记录...")
cursor.execute("SELECT id, name, file_path FROM papers")
papers = cursor.fetchall()
print(f"共发现 {len(papers)} 份试卷记录")

# 定义更灵活的文件名清理函数
def clean_filename(filename):
    """清理文件名，移除所有特殊字符，为模糊匹配做准备"""
    # 提取基本名称（无路径、无扩展名）
    base_name = os.path.basename(filename)
    name_no_ext = os.path.splitext(base_name)[0]
    
    # 移除所有非字母数字字符（保留中文）
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', name_no_ext)
    return cleaned.lower()

# 构建文件映射
print("构建文件映射...")
files_map = {}
for root, _, files in os.walk(PAPERS_DIR):
    for file in files:
        # 忽略隐藏文件和临时文件
        if file.startswith('.') or file.endswith('~'):
            continue
        
        # 获取文件的干净名称作为键，文件完整路径作为值
        clean_name = clean_filename(file)
        if clean_name:
            files_map[clean_name] = os.path.join(root, file)

print(f"发现 {len(files_map)} 个有效文件")

# 定义增强版文件查找函数
def find_actual_file(file_path):
    """查找文件的实际位置，忽略下划线、连字符等特殊字符的差异"""
    if not file_path:
        return None
    
    # 1. 直接检查路径是否存在
    full_path = os.path.join(SERVER_ROOT, file_path)
    if os.path.exists(full_path):
        return full_path
    
    # 2. 仅使用文件名检查
    file_name = os.path.basename(file_path)
    direct_match = os.path.join(PAPERS_DIR, file_name)
    if os.path.exists(direct_match):
        return direct_match
    
    # 3. 使用清理后的文件名进行模糊匹配
    clean_name = clean_filename(file_name)
    if clean_name in files_map:
        return files_map[clean_name]
    
    # 4. 尝试更模糊的匹配 - 检查数字部分
    if re.match(r'^\d+', file_name):
        # 提取文件名开头的数字部分
        prefix_match = re.match(r'^(\d+)', file_name)
        if prefix_match:
            prefix = prefix_match.group(1)
            # 查找以这些数字开头的文件
            for existing_file in os.listdir(PAPERS_DIR):
                if existing_file.startswith(prefix):
                    return os.path.join(PAPERS_DIR, existing_file)
    
    # 没有找到匹配
    return None

# 尝试测试几个文件
test_files_found = 0
test_files_total = min(5, len(papers))
print(f"\n测试 {test_files_total} 个样本文件:")
for i in range(test_files_total):
    paper_id, name, file_path = papers[i]
    actual_path = find_actual_file(file_path)
    status = "找到" if actual_path else "未找到"
    if actual_path:
        test_files_found += 1
    print(f"  [{status}] ID={paper_id}, 名称={name}, 路径={file_path}")
    if actual_path:
        print(f"      → 实际路径: {actual_path}")

# 生成验证报告
accuracy = test_files_found / test_files_total * 100 if test_files_total > 0 else 0
print(f"\n测试准确率: {accuracy:.1f}% ({test_files_found}/{test_files_total})")

# 确认是否应用修复
proceed = input("\n是否应用修复到app.py? (yes/no): ").strip().lower()
if proceed != 'yes':
    print("取消操作。")
    conn.close()
    exit(0)

# 备份app.py
app_path = os.path.join(SERVER_ROOT, 'app.py')
backup_app_path = os.path.join(BACKUP_DIR, f"app.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
print(f"备份app.py到: {backup_app_path}")
shutil.copy2(app_path, backup_app_path)

# 读取app.py内容
print("读取app.py内容...")
with open(app_path, 'r', encoding='utf-8') as f:
    app_content = f.read()

# 查找并替换find_actual_file_location函数
original_func_pattern = r'def find_actual_file_location\(.*?^\s*return None'
new_find_actual_file_location = '''def find_actual_file_location(file_name, paper_info=None):
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
        return re.sub(r'[^\w\u4e00-\u9fff]', '', name_no_ext).lower()
    
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
    num_prefix_match = re.match(r'^(\d+)', file_name)
    if num_prefix_match:
        prefix = num_prefix_match.group(1)
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for existing_file in os.listdir(search_dir):
                    if existing_file.startswith(prefix):
                        return os.path.join(search_dir, existing_file)
    
    # 所有尝试都失败，返回None
    return None'''

# 使用正则表达式替换函数
import re
new_content = re.sub(original_func_pattern, new_find_actual_file_location, app_content, flags=re.DOTALL | re.MULTILINE)

# 写回文件
print("写入修改后的app.py...")
with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n修复完成！请重启Gunicorn服务使更改生效:")
print("  cd /var/www/question_bank")
print("  pkill -f gunicorn")
print("  /var/www/question_bank/venv/bin/gunicorn -c gunicorn_config.py app:app -D")
print("  systemctl restart nginx")

# 关闭数据库连接
conn.close()
print("\n脚本执行完毕。")
