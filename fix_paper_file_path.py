#!/usr/bin/env python3
import os
import sqlite3
import glob
import re
from pathlib import Path

def fix_paper_file_path(paper_id=13165, paper_name="化学丨湖北省黄冈市2025届高三下学期3月核心预测卷化学试卷及答案", 
                      subject="化学", region="湖北", year=2025):
    """
    查找特定试卷的文件，并更新数据库中的文件路径
    """
    print(f"开始修复试卷文件路径: ID={paper_id}, 名称={paper_name}")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"项目根目录: {project_root}")
    
    # 使用正确的数据库路径
    db_path = os.path.join(project_root, "instance", "questions.db")
    print(f"数据库路径: {db_path}")
    
    # 检查数据库是否存在
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return None
    
    # 定义要搜索的目录
    search_dirs = [
        os.path.join(project_root, 'uploads'),
        os.path.join(project_root, 'uploads', 'papers'),
        os.path.join(project_root, 'static', 'uploads'),
        project_root
    ]
    
    # 提取关键词用于匹配
    keywords = [
        str(year),       # 年份
        region,          # 地区
        subject,         # 科目
        "高三",           # 学段
        "核心",           # 特定关键词
        "预测",           # 特定关键词
        "黄冈",           # 特定关键词
        "月"              # 月份考试
    ]
    
    # 筛选有效关键词
    search_keywords = [k for k in keywords if len(k) > 1]
    print(f"搜索关键词: {search_keywords}")
    
    # 查询数据库获取当前记录
    current_file_path = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, file_path, subject, region, year FROM papers WHERE id = ?", (paper_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"数据库记录: ID={result[0]}, 名称={result[1]}, 文件路径={result[2]}")
            current_file_path = result[2]
            
            # 更新搜索信息
            if result[3]:  # subject
                subject = result[3]
            if result[4]:  # region
                region = result[4]
            if result[5]:  # year
                year = result[5]
        else:
            print(f"警告: 未找到ID为 {paper_id} 的试卷记录")
    except Exception as e:
        print(f"数据库查询出错: {str(e)}")
        return None
    
    # 存储匹配文件
    matches = []
    
    # 搜索所有可能的文件
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            print(f"目录不存在，跳过: {search_dir}")
            continue
            
        print(f"正在搜索目录: {search_dir}")
        
        # 搜索该目录下所有PDF、DOC、DOCX和ZIP文件
        for ext in ['pdf', 'doc', 'docx', 'zip']:
            pattern = os.path.join(search_dir, f"**/*.{ext}")
            files = glob.glob(pattern, recursive=True)
            
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
                if "化学" in filename and "黄冈" in filename:
                    score += 3
                if "预测" in filename and "核心" in filename:
                    score += 3
                
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
    for i, match in enumerate(matches[:10]):  # 只显示前10个最相关的
        print(f"{i+1}. 得分:{match['score']} - {match['filename']}")
        print(f"   路径: {match['path']}")
    
    # 如果有匹配文件，尝试更新数据库
    if matches:
        best_match = matches[0]
        relative_path = os.path.relpath(best_match['path'], project_root)
        print(f"\n最佳匹配: {best_match['filename']}")
        print(f"相对路径: {relative_path}")
        
        try:
            # 备份当前文件路径 
            if current_file_path:
                try:
                    cursor.execute("INSERT INTO paper_file_backups (paper_id, original_path, update_time) VALUES (?, ?, datetime('now'))", 
                                 (paper_id, current_file_path))
                    print("已备份原始文件路径")
                except Exception as e:
                    # 如果备份表不存在，创建一个
                    if "no such table" in str(e).lower():
                        cursor.execute("CREATE TABLE IF NOT EXISTS paper_file_backups (id INTEGER PRIMARY KEY, paper_id INTEGER, original_path TEXT, update_time TIMESTAMP)")
                        cursor.execute("INSERT INTO paper_file_backups (paper_id, original_path, update_time) VALUES (?, ?, datetime('now'))", 
                                     (paper_id, current_file_path))
                        print("已创建备份表并备份原始文件路径")
                    else:
                        print(f"备份文件路径出错: {str(e)}")
            
            # 更新文件路径
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (relative_path, paper_id))
            conn.commit()
            print(f"成功: 已更新数据库中的文件路径为: {relative_path}")
            return best_match['path']
        except Exception as e:
            print(f"更新数据库出错: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
    else:
        print("\n未找到匹配的文件。可能需要重新上传此试卷。")
        return None

if __name__ == "__main__":
    # 修复特定试卷的文件路径
    result = fix_paper_file_path()
    
    if result:
        print("\n修复成功! 现在应该可以下载此试卷了。请刷新页面并重试。")
    else:
        print("\n修复失败! 可能需要重新上传此试卷或手动设置文件路径。")
