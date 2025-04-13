#!/usr/bin/env python3
import json
import os

# 加载检查结果
with open('paper_consistency_check_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 创建SQL文件
with open('fix_subject_mismatches.sql', 'w', encoding='utf-8') as sql_file:
    # 写入SQL文件头部注释
    sql_file.write("-- 试卷科目不匹配修复SQL脚本\n")
    sql_file.write("-- 生成时间: " + os.popen('date').read().strip() + "\n")
    sql_file.write("-- 总共需要修复的记录数: " + str(len(results['mismatched_papers'])) + "\n\n")
    
    sql_file.write("BEGIN TRANSACTION;\n\n")
    
    # 为每个不匹配的试卷生成UPDATE语句
    for paper in results['mismatched_papers']:
        paper_id = paper['id']
        recorded_subject = paper['recorded_subject']
        detected_subjects = paper['detected_subjects']
        file_path = paper['file_path']
        name = paper['name']
        
        # 如果检测到多个科目，我们选择第一个作为修正值
        # 在实际应用中，你可能需要更复杂的逻辑来确定正确的科目
        new_subject = detected_subjects[0] if detected_subjects else recorded_subject
        
        # 生成UPDATE语句
        sql = f"-- ID: {paper_id}, 名称: {name}\n"
        sql += f"-- 原科目: {recorded_subject}, 检测科目: {', '.join(detected_subjects)}\n"
        sql += f"-- 文件路径: {file_path}\n"
        sql += f"UPDATE papers SET subject = '{new_subject}' WHERE id = {paper_id};\n\n"
        
        sql_file.write(sql)
    
    sql_file.write("COMMIT;\n")

print(f"已生成SQL修复脚本: fix_subject_mismatches.sql，共包含 {len(results['mismatched_papers'])} 条UPDATE语句")

# 生成缺失文件的统计报告
with open('missing_files_report.txt', 'w', encoding='utf-8') as report_file:
    report_file.write(f"# 缺失文件报告\n\n")
    report_file.write(f"总共有 {len(results['missing_files'])} 个文件缺失\n\n")
    
    # 按科目统计缺失文件数量
    subject_stats = {}
    for paper_id, name, subject, file_path in results['missing_files']:
        subject_stats[subject] = subject_stats.get(subject, 0) + 1
    
    report_file.write("## 按科目统计缺失文件数量\n\n")
    for subject, count in sorted(subject_stats.items(), key=lambda x: x[1], reverse=True):
        report_file.write(f"- {subject}: {count}个\n")
    
    report_file.write("\n## 缺失文件详情\n\n")
    for paper_id, name, subject, file_path in results['missing_files']:
        report_file.write(f"- ID: {paper_id}, 科目: {subject}, 名称: {name}\n  路径: {file_path}\n\n")

print(f"已生成缺失文件报告: missing_files_report.txt，共包含 {len(results['missing_files'])} 个缺失文件的信息") 