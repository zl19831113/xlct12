#!/usr/bin/env python3
import os
import sqlite3
import glob
import re
from pathlib import Path

def search_paper_files(paper_id=13165, paper_name="化学丨湖北省黄冈市2025届高三下学期3月核心预测卷化学试卷及答案", 
                      subject="化学", region="湖北", year=2025):
    """
    深度搜索系统中的试卷文件并尝试匹配特定试卷
    """
    print(f"开始搜索试卷文件: ID={paper_id}, 名称={paper_name}")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {project_root}")
    
    # 定义要搜索的目录
    search_dirs = [
        os.path.join(project_root, 'uploads'),
        os.path.join(project_root, 'uploads', 'papers'),
        os.path.join(project_root, 'static', 'uploads'),
        os.path.join(project_root, 'static', 'papers'),
        project_root
    ]
    
    # 将搜索扩展到更多可能的位置
    for i in range(3):  # 向上查找3级目录
        parent_dir = os.path.dirname(project_root)
        if os.path.exists(parent_dir):
            project_root = parent_dir
            search_dirs.append(os.path.join(project_root, 'uploads'))
            search_dirs.append(os.path.join(project_root, 'papers'))
    
    # 提取关键词用于匹配
    keywords = [
        str(year),  # 年份
        region,     # 地区
        subject,    # 科目
        "高三",      # 学段
        "核心",      # 特定关键词
        "预测",      # 特定关键词
        "黄冈"       # 特定关键词
    ]
    
    # 过滤出更简洁的关键词用于搜索
    search_keywords = [k for k in keywords if len(k) > 1]
    print(f"搜索关键词: {search_keywords}")
    
    # 存储匹配文件
    matches = []
    all_pdf_files = []
    
    # 遍历所有可能的目录
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            print(f"目录不存在，跳过: {search_dir}")
            continue
            
        print(f"正在搜索目录: {search_dir}")
        
        # 搜索该目录下所有PDF、DOC、DOCX和ZIP文件
        for ext in ['pdf', 'doc', 'docx', 'zip']:
            pattern = os.path.join(search_dir, f"**/*.{ext}")
            files = glob.glob(pattern, recursive=True)
            
            if ext == 'pdf':
                all_pdf_files.extend(files)
                
            for file_path in files:
                filename = os.path.basename(file_path).lower()
                
                # 计算匹配度分数
                score = 0
                for keyword in search_keywords:
                    if keyword.lower() in filename:
                        score += 1
                
                # 特殊加分
                if subject.lower() in filename:
                    score += 3
                if str(year) in filename:
                    score += 3
                if region.lower() in filename:
                    score += 2
                if f"{paper_id}" in filename:
                    score += 10
                
                # 高分匹配加入结果
                if score >= 3:
                    matches.append({
                        'path': file_path,
                        'score': score,
                        'filename': os.path.basename(file_path)
                    })
    
    # 按匹配度排序
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # 输出结果
    print(f"\n找到 {len(matches)} 个可能匹配的文件:")
    for i, match in enumerate(matches[:20]):  # 只显示前20个最相关的
        print(f"{i+1}. 得分:{match['score']} - {match['filename']}")
        print(f"   路径: {match['path']}")
    
    # 统计所有PDF文件
    print(f"\n系统中PDF文件总数: {len(all_pdf_files)}")
    
    # 检查数据库中的文件路径
    print("\n检查数据库中的记录:")
    db_path = os.path.join(project_root, 'instance', 'questions.db')
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, file_path FROM papers WHERE id = ?", (paper_id,))
            result = cursor.fetchone()
            
            if result:
                print(f"数据库记录: ID={result[0]}, 名称={result[1]}, 文件路径={result[2]}")
                full_path = os.path.join(project_root, result[2])
                print(f"完整路径: {full_path}")
                print(f"该路径是否存在: {os.path.exists(full_path)}")
                
                # 如果找到了匹配度高的文件，尝试更新数据库
                if matches:
                    best_match = matches[0]
                    relative_path = os.path.relpath(best_match['path'], project_root)
                    print(f"\n建议更新数据库文件路径为: {relative_path}")
                    
                    update_choice = input("是否更新数据库中的文件路径? (y/n): ")
                    if update_choice.lower() == 'y':
                        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", 
                                      (relative_path, paper_id))
                        conn.commit()
                        print(f"已更新文件路径: {relative_path}")
            else:
                print(f"未找到ID为 {paper_id} 的试卷记录")
                
            conn.close()
        except Exception as e:
            print(f"数据库操作出错: {str(e)}")
    else:
        print(f"数据库文件不存在: {db_path}")
    
    # 返回最佳匹配的文件路径
    if matches:
        return matches[0]['path']
    return None

if __name__ == "__main__":
    # 调用搜索函数
    best_match = search_paper_files()
    
    if best_match:
        print(f"\n找到最佳匹配文件: {best_match}")
        print("建议将此文件路径更新到数据库中，或将此文件复制到数据库中指定的位置。")
    else:
        print("\n未找到匹配的文件。可能需要重新上传此试卷。")
