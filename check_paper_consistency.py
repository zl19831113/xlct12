#!/usr/bin/env python3
import os
import sqlite3
import zipfile
import re
import json
from collections import defaultdict

# 连接到数据库
conn = sqlite3.connect('instance/questions.db')
cursor = conn.cursor()

# 获取所有试卷记录
cursor.execute("SELECT id, name, subject, file_path FROM papers")
papers = cursor.fetchall()

print(f"总共找到 {len(papers)} 个试卷记录")

# 创建检查结果列表
mismatched_papers = []
missing_files = []

# 检查每个试卷
count = 0
for paper_id, name, subject, file_path in papers:
    count += 1
    if count % 1000 == 0:
        print(f"已检查 {count}/{len(papers)} 个试卷...")
    
    # 检查文件是否存在
    full_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(full_path):
        missing_files.append((paper_id, name, subject, file_path))
        continue
    
    # 检查zip文件内容
    if full_path.lower().endswith('.zip'):
        try:
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # 检查文件名中是否包含科目
                subject_in_files = False
                subject_keywords = {}
                
                # 定义各科目的关键词
                subject_keywords['语文'] = ['语文', 'chinese', '文言文', '古诗']
                subject_keywords['数学'] = ['数学', 'math', '函数', '方程', '几何']
                subject_keywords['英语'] = ['英语', 'english', '听力', 'listening']
                subject_keywords['物理'] = ['物理', 'physics', '力学', '电学']
                subject_keywords['化学'] = ['化学', 'chemistry', '酸碱', '元素']
                subject_keywords['生物'] = ['生物', 'biology', '细胞', '遗传']
                subject_keywords['历史'] = ['历史', 'history']
                subject_keywords['地理'] = ['地理', 'geography']
                subject_keywords['政治'] = ['政治', '思想', '道德与法治']
                
                # 检测文件内容与科目的匹配度
                detected_subjects = set()
                for filename in file_list:
                    for subj, keywords in subject_keywords.items():
                        for keyword in keywords:
                            if keyword in filename.lower() or keyword in name.lower():
                                detected_subjects.add(subj)
                
                # 如果检测到的科目与记录的科目不匹配，则记录
                if subject not in detected_subjects and detected_subjects:
                    mismatched_papers.append({
                        'id': paper_id,
                        'name': name,
                        'recorded_subject': subject,
                        'detected_subjects': list(detected_subjects),
                        'file_path': file_path,
                        'file_contents': file_list[:5]  # 只显示前5个文件名
                    })
        except zipfile.BadZipFile:
            print(f"错误：ID为{paper_id}的文件{file_path}不是有效的ZIP文件")
        except Exception as e:
            print(f"检查ID为{paper_id}的文件{file_path}时出错: {str(e)}")

# 统计结果
subject_mismatch_stats = defaultdict(int)
detected_subject_stats = defaultdict(int)

for paper in mismatched_papers:
    subject_mismatch_stats[paper['recorded_subject']] += 1
    for detected_subject in paper['detected_subjects']:
        detected_subject_stats[detected_subject] += 1

# 打印统计结果到控制台
print("\n==== 科目不匹配统计 ====")
print(f"总共找到 {len(mismatched_papers)} 个科目不匹配的试卷")
print(f"总共找到 {len(missing_files)} 个文件缺失的试卷")

print("\n按记录科目统计不匹配数量:")
for subject, count in sorted(subject_mismatch_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{subject}: {count}个")

print("\n按检测到的科目统计数量:")
for subject, count in sorted(detected_subject_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{subject}: {count}个")

# 将详细结果保存到文件
with open('paper_consistency_check_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'mismatched_papers': mismatched_papers,
        'missing_files': missing_files,
        'statistics': {
            'total_papers': len(papers),
            'mismatched_papers': len(mismatched_papers),
            'missing_files': len(missing_files),
            'subject_mismatch_stats': dict(subject_mismatch_stats),
            'detected_subject_stats': dict(detected_subject_stats)
        }
    }, f, ensure_ascii=False, indent=2)

print("\n详细结果已保存到 paper_consistency_check_results.json 文件")

# 关闭数据库连接
conn.close()