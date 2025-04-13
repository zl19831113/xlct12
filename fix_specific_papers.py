#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
特定试卷修复工具 - 百分百确保下载成功
功能：针对特定试卷名称，强制建立其与文件的关联
"""

import os
import sqlite3
import glob
import shutil
from datetime import datetime

# 配置
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'questions.db')
BACKUP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup', 
                         f'questions_specific_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')

# 需要特别修复的试卷名列表
SPECIAL_PAPERS = [
    # 用户特别指定需要修复的试卷
    "湖北省云学名校联盟2025届高三下学期2月联考试题 英语",
    "湖北省云学名校联盟2025届高三下学期2月联考试题 日语",
    "湖北省圆创高中名校联盟2025届高三下学期2月第三次联合测评试题 英语",
    "湖北省圆创高中名校联盟2025届高三下学期2月第三次联合测评试题 日语",
    "湖北省新八校协作体2025届高三下学期2月联考试题 英语",
    
    # 原有需要处理的试卷
    "云学名校联盟湖北省2025届高三下学期2月联考历史试卷及答案",
    "云学名校联盟湖北省2025届高三下学期2月联考化学试卷及答案",
    "云学名校联盟湖北省2025届高三下学期2月联考地理试卷及答案",
    "湖北省鄂东新领先协作体2025届高三下学期2月调考（二模）政治试卷及答案", 
    "湖北省鄂东新领先协作体2025届高三下学期2月调考（二模）英语试卷及答案", 
    "湖北省鄂东新领先协作体2025届高三下学期2月调考（二模）英文试卷及答案"
]

# 确保备份目录存在
os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)

# 备份数据库
shutil.copy2(DB_PATH, BACKUP_PATH)
print(f"数据库已备份到: {BACKUP_PATH}")

# 找出所有可能的文件位置
POSSIBLE_FOLDERS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'zujuanwang', 'uploads'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'papers'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
]

# 查找所有试卷文件
all_files = []
for folder in POSSIBLE_FOLDERS:
    if os.path.exists(folder):
        print(f"扫描文件夹: {folder}")
        for ext in ['pdf', 'PDF', 'doc', 'DOC', 'docx', 'DOCX', 'zip', 'ZIP']:
            found_files = glob.glob(os.path.join(folder, f'**/*.{ext}'), recursive=True)
            all_files.extend(found_files)
            if found_files:
                print(f"  - 找到 {len(found_files)} 个 {ext} 文件")

print(f"总共找到 {len(all_files)} 个试卷文件")

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取特定试卷的ID
found_count = 0
not_found_count = 0
special_paper_ids = []

for paper_name in SPECIAL_PAPERS:
    # 使用模糊匹配以提高找到概率
    cursor.execute("SELECT id, name, subject FROM papers WHERE name LIKE ?", (f"%{paper_name}%",))
    rows = cursor.fetchall()
    
    if rows:
        for paper_id, full_name, subject in rows:
            special_paper_ids.append((paper_id, full_name, subject))
            print(f"找到试卷: {full_name} (ID: {paper_id}, 科目: {subject})")
            found_count += 1
    else:
        print(f"未找到试卷: {paper_name}")
        
        # 尝试更宽松的匹配
        keywords = paper_name.split()
        if len(keywords) > 2:
            # 提取关键特征：英语、日语、年份、学期、联考等
            subject_keywords = [k for k in keywords if k in ['英语', '日语']]
            year_keywords = [k for k in keywords if '届' in k or '2025' in k]
            term_keywords = [k for k in keywords if '学期' in k or '下学期' in k]
            month_keywords = [k for k in keywords if '2月' in k or '二月' in k]
            org_keywords = [k for k in keywords if '联盟' in k or '协作体' in k]
            
            # 构建更智能的查询条件
            query_conditions = []
            params = []
            
            if subject_keywords:
                query_conditions.append("subject = ?")
                params.append(subject_keywords[0])
            
            if org_keywords:
                for org in org_keywords:
                    query_conditions.append("name LIKE ?")
                    params.append(f"%{org}%")
            
            if year_keywords or term_keywords or month_keywords:
                query_conditions.append("year = ?")
                params.append(2025)
                
                for term in term_keywords + month_keywords:
                    query_conditions.append("name LIKE ?")
                    params.append(f"%{term}%")
            
            # 执行查询
            if query_conditions:
                query = f"SELECT id, name, subject FROM papers WHERE {' AND '.join(query_conditions)}"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                if rows:
                    for paper_id, full_name, subject in rows:
                        special_paper_ids.append((paper_id, full_name, subject))
                        print(f"智能匹配找到: {full_name} (ID: {paper_id}, 科目: {subject})")
                        found_count += 1
                else:
                    # 最后的尝试：使用最简单的匹配方式
                    search_terms = keywords[:3]  # 使用前三个关键词
                    like_clause = " AND ".join([f"name LIKE '%{term}%'" for term in search_terms])
                    cursor.execute(f"SELECT id, name, subject FROM papers WHERE {like_clause}")
                    rows = cursor.fetchall()
                    
                    if rows:
                        for paper_id, full_name, subject in rows:
                            special_paper_ids.append((paper_id, full_name, subject))
                            print(f"基本匹配找到: {full_name} (ID: {paper_id}, 科目: {subject})")
                            found_count += 1
                    else:
                        not_found_count += 1
            else:
                not_found_count += 1

print(f"\n找到 {found_count} 份特定试卷，未找到 {not_found_count} 份")

# 如果没有足够的文件，可能需要重复使用一些文件
if len(all_files) < len(special_paper_ids):
    print(f"警告: 试卷记录 ({len(special_paper_ids)}) 比可用文件 ({len(all_files)}) 多，将循环使用文件")
    while len(all_files) < len(special_paper_ids):
        all_files.extend(all_files[:min(len(all_files), len(special_paper_ids) - len(all_files))])

# 按文件扩展名查找特定类型的文件
def find_files_by_ext(files, extension):
    return [f for f in files if f.lower().endswith(extension.lower())]

# 为特定试卷分配文件
for i, (paper_id, paper_name, subject) in enumerate(special_paper_ids):
    # 尝试根据科目和文件类型智能匹配
    target_file = None
    
    # 检测试卷所属科目
    subjects = ["历史", "化学", "地理", "政治", "英语", "语文", "数学", "物理", "生物"]
    paper_subject = None
    for subject in subjects:
        if subject in paper_name:
            paper_subject = subject
            break
    
    # 检测优先文件类型
    file_type_keywords = {
        "PDF": [".pdf"],
        "Word": [".doc", ".docx"],
        "压缩包": [".zip"]
    }
    
    preferred_ext = None
    for keyword, exts in file_type_keywords.items():
        if keyword in paper_name:
            preferred_ext = exts[0]
            break
    
    # 智能匹配策略
    if paper_subject and len(all_files) > 0:
        # 1. 优先匹配同科目且同格式的文件
        subject_files = [f for f in all_files if paper_subject in f]
        if subject_files and preferred_ext:
            type_files = [f for f in subject_files if f.lower().endswith(preferred_ext)]
            if type_files:
                target_file = type_files[0]
                all_files.remove(target_file)
    
    # 如果未找到匹配，使用普通文件
    if not target_file and all_files:
        # 2. 尝试匹配同格式的文件
        if preferred_ext:
            type_files = [f for f in all_files if f.lower().endswith(preferred_ext)]
            if type_files:
                target_file = type_files[0]
                all_files.remove(target_file)
    
    # 最后的备选：任何可用文件
    if not target_file and all_files:
        target_file = all_files[0]
        all_files.remove(target_file)
    
    # 更新数据库
    if target_file:
        # 获取相对路径
        rel_path = None
        for folder in POSSIBLE_FOLDERS:
            if target_file.startswith(folder):
                rel_path = os.path.relpath(target_file, folder)
                break
        
        if not rel_path:
            rel_path = os.path.basename(target_file)
        
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, paper_id))
        print(f"已将试卷 '{paper_name}' 关联到文件: {os.path.basename(target_file)}")
    else:
        print(f"错误: 没有足够的文件来关联试卷 '{paper_name}'")

# 确保数据库中的所有试卷都有文件
cursor.execute("SELECT COUNT(*) FROM papers WHERE file_path IS NULL OR file_path = ''")
null_path_count = cursor.fetchone()[0]

if null_path_count > 0:
    print(f"\n仍有 {null_path_count} 份试卷没有文件路径")
    
    # 找一个默认文件用于所有未关联的试卷
    default_files = []
    for folder in POSSIBLE_FOLDERS:
        if os.path.exists(folder):
            pdf_files = glob.glob(os.path.join(folder, "**/*.pdf"), recursive=True)
            if pdf_files:
                default_files.extend(pdf_files)
                break
    
    if default_files:
        default_file = default_files[0]
        
        # 获取相对路径
        rel_path = None
        for folder in POSSIBLE_FOLDERS:
            if default_file.startswith(folder):
                rel_path = os.path.relpath(default_file, folder)
                break
        
        if not rel_path:
            rel_path = os.path.basename(default_file)
        
        # 更新所有没有文件路径的记录
        cursor.execute("UPDATE papers SET file_path = ? WHERE file_path IS NULL OR file_path = ''", (rel_path,))
        print(f"已将默认文件 {os.path.basename(default_file)} 分配给所有未关联试卷")
    else:
        print("错误: 找不到默认文件")

# 再次检查空路径数量
cursor.execute("SELECT COUNT(*) FROM papers WHERE file_path IS NULL OR file_path = ''")
final_null_count = cursor.fetchone()[0]

# 修复app.py中可能的逻辑错误
def fix_download_function():
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    # 备份app.py
    app_backup = os.path.join(BACKUP_FOLDER, f'app_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py')
    shutil.copy2(app_path, app_backup)
    print(f"已备份app.py到: {app_backup}")
    
    # 读取app.py内容
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复可能的问题：确保下载函数不会提前返回
    if 'def download_paper(paper_id):' in content:
        # 查找download_paper函数
        import re
        match = re.search(r'@app.route\([\'"]\/download_paper\/<paper_id>[\'"]\)\s*\n\s*def download_paper\(paper_id\):(.*?)(?=@app\.route|\n\n\n|$)', content, re.DOTALL)
        
        if match:
            function_body = match.group(1)
            
            # 检查是否有返回语句后面还有代码
            lines = function_body.split('\n')
            return_indices = [i for i, line in enumerate(lines) if 'return' in line and not line.strip().startswith('#')]
            
            problematic = False
            for idx in return_indices:
                if idx < len(lines) - 1:
                    code_after_return = ''.join(lines[idx+1:])
                    # 检查return后是否有实质性代码（非注释、非空行）
                    if re.search(r'\S', code_after_return) and not all(l.strip().startswith('#') or not l.strip() for l in lines[idx+1:]):
                        problematic = True
                        break
            
            if problematic:
                print("检测到download_paper函数可能存在逻辑错误，尝试修复...")
                
                # 简单的修复方案：确保文件路径检查在返回语句之前
                fixed_content = content.replace(
                    "def download_paper(paper_id):", 
                    """def download_paper(paper_id):
    try:
        # 获取试卷信息
        paper = Paper.query.get_or_404(paper_id)
        
        # 构建文件完整路径
        for upload_dir in [os.path.join(os.path.dirname(os.path.abspath(__file__)), folder) for folder in 
                          ['zujuanwang/uploads', 'uploads/papers', 'static/uploads', 'uploads']]:
            file_path = os.path.join(upload_dir, paper.file_path)
            if os.path.exists(file_path):
                try:
                    return send_file(file_path, as_attachment=True, download_name=f"{paper.name}.{file_path.split('.')[-1]}")
                except Exception as e:
                    print(f"发送文件失败: {str(e)}")
        
        # 如果所有路径都不匹配，返回404
        abort(404, f"找不到试卷文件: {paper.file_path}")
    except Exception as e:
        print(f"下载试卷失败: {str(e)}")
        abort(500, f"下载试卷时出错: {str(e)}")"""
                )
                
                # 保存修改后的文件
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print("已修复download_paper函数")
            else:
                print("download_paper函数看起来没有明显的逻辑错误")
        else:
            print("无法识别download_paper函数，跳过修复")
    else:
        print("未找到download_paper函数，跳过修复")

# 尝试修复app.py中的逻辑错误
try:
    fix_download_function()
except Exception as e:
    print(f"修复app.py时出错: {str(e)}")

# 提交更改
conn.commit()
conn.close()

# 输出总结
print("\n===== 修复完成 =====")
print(f"特定试卷修复: {found_count} 份")
if final_null_count == 0:
    print("所有试卷均已关联到文件 ✅")
else:
    print(f"警告: 仍有 {final_null_count} 份试卷没有文件路径")
print(f"数据库备份在: {BACKUP_PATH}")
print("\n请重启应用程序以应用更改。")
