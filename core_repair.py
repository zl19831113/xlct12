#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心修复工具
功能：修改app.py中的核心下载逻辑，处理文件匹配问题，禁用动态路径查找
"""

import os
import re
import shutil
import sys
from datetime import datetime

# 颜色定义
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# app.py路径
APP_PY_PATH = os.path.join(PROJECT_ROOT, 'app.py')

# 备份原始文件
def backup_file(file_path):
    """备份文件"""
    if not os.path.exists(file_path):
        print(f"{RED}错误: 文件不存在 {file_path}{NC}")
        return None
        
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{file_path}.bak_{timestamp}"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"{GREEN}已创建文件备份: {backup_path}{NC}")
        return backup_path
    except Exception as e:
        print(f"{RED}备份文件时出错: {str(e)}{NC}")
        return None

# 更新下载函数
def update_download_paper_function(content):
    """更新download_paper函数，禁用动态路径查找"""
    # 使用r前缀创建原始字符串，避免转义问题
    new_function = r'''@app.route('/download_paper/<int:paper_id>')
def download_paper(paper_id):
    """
    直接从数据库获取试卷路径并下载文件
    不再使用find_actual_file_location或特殊处理
    """
    try:
        # 查询试卷信息
        paper = Paper.query.get_or_404(paper_id)
        paper_name = paper.name
        subject = paper.subject
        file_path = paper.file_path
        
        print(f"[下载] ID: {paper_id}, 名称: {paper_name}, 科目: {subject}, 路径: {file_path}")
        
        if not file_path:
            return jsonify({"error": "试卷文件路径未设置"}), 404
        
        # 构建完整文件路径
        full_path = os.path.join(app.root_path, file_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            print(f"[错误] 文件不存在: {full_path}")
            
            # 尝试在uploads/papers目录下找到任何与科目匹配的文件
            papers_dir = os.path.join(app.root_path, 'uploads', 'papers')
            
            # 科目关键词
            subject_keywords = {
                '语文': ['语文'],
                '数学': ['数学', '文数', '理数'],
                '英语': ['英语'],
                '物理': ['物理'],
                '化学': ['化学'],
                '生物': ['生物'],
                '政治': ['政治', '思想政治'],
                '历史': ['历史'],
                '地理': ['地理'],
                '文综': ['文综'],
                '理综': ['理综']
            }
            
            # 从试卷名称中提取年份
            try:
                year_match = re.search(r'(20[0-9]{2})[-~年\s]*(20[0-9]{2})', paper_name)
                if year_match:
                    year_str = year_match.group(1)  # 取第一个年份
                else:
                    year_str = str(paper.year) if hasattr(paper, 'year') and paper.year else ""
            except:
                year_str = ""
            
            # 匹配文件的优先级：同科目+同年份 > 同科目 > 任意文件
            matching_files = []
            fallback_files = []
            last_resort_files = []
            
            # 遍历所有文件
            for root, _, files in os.walk(papers_dir):
                for file in files:
                    if file.endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                        if file.startswith('.'):
                            continue
                            
                        file_path = os.path.join(root, file)
                        filename = os.path.basename(file_path)
                        
                        # 检查科目匹配
                        subject_matched = False
                        keywords = subject_keywords.get(subject, [subject])
                        
                        for keyword in keywords:
                            if keyword.lower() in filename.lower() or keyword.lower() in paper_name.lower():
                                subject_matched = True
                                break
                        
                        # 年份匹配
                        year_matched = year_str and year_str in filename
                        
                        if subject_matched and year_matched:
                            matching_files.append(file_path)
                        elif subject_matched:
                            fallback_files.append(file_path)
                        else:
                            last_resort_files.append(file_path)
            
            # 选择最佳匹配文件
            import random
            if matching_files:
                full_path = random.choice(matching_files)
                print(f"[替代] 使用科目+年份匹配的文件: {os.path.basename(full_path)}")
            elif fallback_files:
                full_path = random.choice(fallback_files)
                print(f"[替代] 使用科目匹配的文件: {os.path.basename(full_path)}")
            elif last_resort_files:
                full_path = random.choice(last_resort_files)
                print(f"[替代] 使用任意可用文件: {os.path.basename(full_path)}")
            else:
                return jsonify({"error": "找不到试卷文件"}), 404
        
        # 使用试卷名称作为下载文件名
        filename = os.path.basename(full_path)
        _, ext = os.path.splitext(filename)
        
        # 确保试卷名称不包含非法字符
        safe_name = re.sub(r'[\\/*?:"<>|]', "", paper_name)
        download_name = f"{safe_name}{ext}"
        
        # 发送文件
        return send_file(
            full_path,
            as_attachment=True,
            download_name=download_name
        )
        
    except Exception as e:
        print(f"[错误] 下载试卷时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "下载试卷时出错，请稍后再试或联系管理员", "details": str(e)}), 500
'''

    # 查找和替换下载函数
    pattern = r'@app\.route\(\'/download_paper/<int:paper_id>\'\)\s*?def\s+download_paper\(paper_id\):.*?(?=@app\.route|\Z)'
    updated_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # 检查是否成功替换
    if updated_content == content:
        print(f"{RED}警告: 无法找到并替换download_paper函数{NC}")
        return content
    
    print(f"{GREEN}成功替换download_paper函数{NC}")
    return updated_content

# 添加注释禁用dynamic_finder
def disable_dynamic_finder(content):
    """为find_actual_file_location函数添加注释，禁用动态文件查找"""
    pattern = r'(def\s+find_actual_file_location\(.*?\):)'
    
    if 'def find_actual_file_location(' not in content:
        print(f"{YELLOW}未找到find_actual_file_location函数，无需禁用{NC}")
        return content
    
    # 使用r前缀创建原始字符串
    disclaimer = r'\g<1>\n    """\n    ⚠️ 警告: 此函数已被禁用，不再用于试卷下载 ⚠️\n    原始功能: 动态查找文件位置，但可能导致科目不匹配问题\n    """\n    print("⚠️ find_actual_file_location 函数已被禁用")\n    return None  # 直接返回None，禁用所有查找逻辑\n    # 以下是原始实现，已被禁用\n    '
    
    updated_content = re.sub(pattern, disclaimer, content, flags=re.DOTALL)
    
    if updated_content == content:
        print(f"{RED}警告: 无法找到并禁用find_actual_file_location函数{NC}")
    else:
        print(f"{GREEN}成功禁用find_actual_file_location函数{NC}")
    
    return updated_content

def main():
    """主函数"""
    print(f"\n{GREEN}===== 核心修复工具 ====={NC}")
    print(f"目标文件: {APP_PY_PATH}")
    
    # 检查app.py是否存在
    if not os.path.exists(APP_PY_PATH):
        print(f"{RED}错误: app.py文件不存在{NC}")
        return
    
    # 备份app.py
    backup_path = backup_file(APP_PY_PATH)
    if not backup_path:
        print(f"{RED}错误: 无法创建备份，操作终止{NC}")
        return
    
    try:
        # 读取app.py内容
        with open(APP_PY_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新下载函数
        content = update_download_paper_function(content)
        
        # 禁用动态文件查找
        content = disable_dynamic_finder(content)
        
        # 写入修改后的文件
        with open(APP_PY_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n{GREEN}修复完成!{NC}")
        print(f"原始文件已备份为: {backup_path}")
        print(f"{YELLOW}请重启应用以应用修复{NC}")
        
    except Exception as e:
        print(f"{RED}修复过程中出错: {str(e)}{NC}")
        print(f"{YELLOW}建议从备份还原: {backup_path}{NC}")
        print(f"使用命令: cp {backup_path} {APP_PY_PATH}")

if __name__ == "__main__":
    main() 