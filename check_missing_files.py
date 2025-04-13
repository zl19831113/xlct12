#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查缺失的试卷文件并尝试修复
创建时间: 2025-03-29
"""

import os
import re
import sqlite3
import sys
from collections import defaultdict
import shutil
import time

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'  # 无颜色

# 配置
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, 'instance', 'questions.db')
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'uploads')

def print_color(message, color=None):
    """打印彩色文本"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn

def load_paper_info(paper_ids=None, keywords=None):
    """从数据库加载试卷信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if paper_ids:
            placeholders = ', '.join('?' for _ in paper_ids)
            cursor.execute(f"SELECT id, name, file_path, region, subject, year FROM papers WHERE id IN ({placeholders})", paper_ids)
        elif keywords:
            # 构建搜索条件
            search_terms = []
            params = []
            for keyword in keywords:
                search_terms.append("name LIKE ?")
                params.append(f"%{keyword}%")
            
            where_clause = " AND ".join(search_terms)
            cursor.execute(f"SELECT id, name, file_path, region, subject, year FROM papers WHERE {where_clause}", params)
        else:
            cursor.execute("SELECT id, name, file_path, region, subject, year FROM papers ORDER BY id DESC LIMIT 100")
        
        papers = cursor.fetchall()
        conn.close()
        return papers
    except Exception as e:
        print_color(f"加载试卷信息时出错: {e}", RED)
        return []

def check_file_exists(file_path):
    """检查文件是否存在"""
    if not file_path:
        return False
    
    # 先检查是否为绝对路径
    if os.path.isabs(file_path):
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    # 如果是相对路径，尝试从项目根目录解析
    full_path = os.path.join(PROJECT_DIR, file_path)
    return os.path.exists(full_path) and os.path.isfile(full_path)

def find_similar_files(paper_name, file_name):
    """在uploads目录中查找与试卷名称相似的文件"""
    if not os.path.exists(UPLOADS_DIR):
        return []
    
    matches = []
    
    # 从试卷名中提取关键词
    # 移除常见词和标点符号，只保留可能的独特标识词
    clean_name = re.sub(r'[（）()【】\[\]《》<>{},.，。、:：；;!！?？]', ' ', paper_name)
    keywords = clean_name.split()
    
    # 过滤掉常见短词
    stopwords = ['试卷', '试题', '答案', '解析', '含', '版', '高三', '高中', '中学', '届', '学年', '上学期', '下学期', '月考', '期中', '期末', 'PDF', 'Word']
    keywords = [k for k in keywords if len(k) > 1 and k not in stopwords]
    
    # 如果关键词太少，就使用原始文件名的一部分
    if len(keywords) < 2 and file_name:
        base_name = os.path.splitext(file_name)[0]
        # 尝试去掉前缀数字和时间戳
        clean_base = re.sub(r'^\d+_\d+_\d+_', '', base_name)
        if clean_base:
            keywords.append(clean_base)
    
    # 遍历uploads目录查找匹配文件
    for root, _, files in os.walk(UPLOADS_DIR):
        for f in files:
            score = 0
            f_lower = f.lower()
            
            # 检查文件扩展名
            _, ext = os.path.splitext(f)
            if ext.lower() in ['.pdf', '.doc', '.docx', '.zip', '.rar']:
                score += 1
                
                # 关键词匹配
                for keyword in keywords:
                    if keyword.lower() in f_lower:
                        score += 2
                
                # 年份匹配
                if '2025' in f and '2025' in paper_name:
                    score += 3
                    
                # 检查是否包含学校名或区域名
                school_match = False
                for region in ['湖北', '云学', '腾云', '联盟']:
                    if region in paper_name and region in f:
                        score += 5
                        school_match = True
                
                # 若关键词匹配足够多，添加到结果
                if score >= 5 or school_match:
                    matches.append({
                        'path': os.path.join(root, f),
                        'score': score,
                        'name': f
                    })
    
    # 按匹配分数排序
    return sorted(matches, key=lambda x: x['score'], reverse=True)

def update_file_path(paper_id, new_path):
    """更新数据库中的文件路径"""
    try:
        conn = get_db_connection()
        rel_path = os.path.relpath(new_path, PROJECT_DIR)
        conn.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, paper_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print_color(f"更新文件路径时出错: {e}", RED)
        return False

def search_specific_papers():
    """根据用户提供的具体试卷名搜索缺失的文件"""
    print_color("\n===== 搜索特定试卷 =====", YELLOW)
    
    specific_papers = [
        "湖北省云学名校联盟2025届高三下学期2月联考试题 英语 PDF版含解析",
        "湖北省腾云联盟2025届高三上学期12月联考 英语试卷含听力"
    ]
    
    found_files = defaultdict(list)  # 用于存储找到的文件
    
    for paper_name in specific_papers:
        # 拆分关键词
        keywords = paper_name.split()
        if len(keywords) > 3:
            # 提取最关键的几个词
            main_keywords = [kw for kw in keywords if len(kw) > 1 and kw not in ['PDF', 'Word', '版', '含']][:3]
        else:
            main_keywords = keywords
        
        print_color(f"\n查找试卷: {paper_name}", BLUE)
        print_color(f"使用关键词: {main_keywords}", BLUE)
        
        # 从数据库中查找匹配的试卷
        papers = load_paper_info(keywords=main_keywords)
        
        if not papers:
            print_color(f"在数据库中未找到与 '{paper_name}' 匹配的试卷记录", RED)
            continue
        
        print_color(f"找到 {len(papers)} 条可能的匹配记录", GREEN)
        
        for i, paper in enumerate(papers):
            print_color(f"\n[{i+1}] ID: {paper['id']}, 名称: {paper['name']}", BOLD)
            print(f"    文件路径: {paper['file_path']}")
            
            # 检查文件是否存在
            if paper['file_path'] and check_file_exists(paper['file_path']):
                full_path = os.path.join(PROJECT_DIR, paper['file_path']) if not os.path.isabs(paper['file_path']) else paper['file_path']
                print_color(f"    ✓ 文件存在: {full_path}", GREEN)
                found_files[paper['id']].append({'type': 'exact', 'path': full_path})
            else:
                print_color(f"    ✗ 文件不存在", RED)
                
                # 提取文件名
                file_name = os.path.basename(paper['file_path']) if paper['file_path'] else None
                
                # 尝试查找相似文件
                similar_files = find_similar_files(paper['name'], file_name)
                
                if similar_files:
                    print_color(f"    找到 {len(similar_files)} 个可能匹配的文件:", BLUE)
                    for j, match in enumerate(similar_files[:3]):  # 只显示前3个最佳匹配
                        print_color(f"      [{j+1}] 匹配度: {match['score']}, 文件: {match['name']}", BLUE)
                        found_files[paper['id']].append({'type': 'similar', 'path': match['path'], 'score': match['score']})
                else:
                    print_color(f"    未找到可能匹配的文件", RED)
    
    return found_files

def batch_check_missing_files():
    """检查所有缺失的试卷文件"""
    print_color("\n===== 批量检查缺失文件 =====", YELLOW)
    
    try:
        conn = get_db_connection()
        # 获取所有试卷记录，包括更多信息
        cursor = conn.execute("SELECT id, name, file_path, region, subject, year FROM papers")
        all_papers = cursor.fetchall()
        conn.close()
        
        total = len(all_papers)
        print_color(f"总试卷数量: {total}", BLUE)
        
        missing_files = []
        invalid_files = []
        valid_files = 0
        
        for i, paper in enumerate(all_papers):
            # 每1000条显示进度
            if i % 1000 == 0:
                print_color(f"进度: {i}/{total} ({i*100/total:.1f}%)", BLUE)
            
            if not paper['file_path']:
                missing_files.append(paper)
            elif not check_file_exists(paper['file_path']):
                invalid_files.append(paper)
            else:
                valid_files += 1
        
        # 显示统计结果
        print_color(f"\n=== 文件状态统计 ===", GREEN)
        print_color(f"有效文件数量: {valid_files} ({valid_files*100/total:.1f}%)", GREEN)
        print_color(f"缺失文件路径数量: {len(missing_files)} ({len(missing_files)*100/total:.1f}%)", YELLOW if missing_files else GREEN)
        print_color(f"无效文件路径数量: {len(invalid_files)} ({len(invalid_files)*100/total:.1f}%)", YELLOW if invalid_files else GREEN)
        
        # 显示前10个缺失文件
        if missing_files:
            print_color("\n部分缺失文件路径的试卷:", YELLOW)
            for i, paper in enumerate(missing_files[:10]):
                print(f"[{i+1}] ID: {paper['id']}, 名称: {paper['name']}, 科目: {paper['subject']}, 年份: {paper['year']}")
        
        # 显示前10个无效文件
        if invalid_files:
            print_color("\n部分无效文件路径的试卷:", YELLOW)
            for i, paper in enumerate(invalid_files[:10]):
                print(f"[{i+1}] ID: {paper['id']}, 名称: {paper['name']}, 科目: {paper['subject']}, 年份: {paper['year']}")
                print(f"    文件路径: {paper['file_path']}")
        
        # 按科目统计
        subject_stats = defaultdict(lambda: {'total': 0, 'missing': 0, 'invalid': 0})
        for paper in all_papers:
            subject = paper['subject'] or '未知'
            subject_stats[subject]['total'] += 1
            
        for paper in missing_files:
            subject = paper['subject'] or '未知'
            subject_stats[subject]['missing'] += 1
            
        for paper in invalid_files:
            subject = paper['subject'] or '未知'
            subject_stats[subject]['invalid'] += 1
        
        # 按科目显示统计信息
        print_color("\n=== 按科目统计 ===", GREEN)
        for subject, stats in sorted(subject_stats.items(), key=lambda x: (x[1]['missing'] + x[1]['invalid'])/x[1]['total'] if x[1]['total'] > 0 else 0, reverse=True):
            total = stats['total']
            missing = stats['missing']
            invalid = stats['invalid']
            problem_rate = (missing + invalid) * 100 / total if total else 0
            
            if total > 5:  # 只显示数量超过5个的科目
                if problem_rate > 50:
                    color = RED
                elif problem_rate > 30:
                    color = YELLOW
                else:
                    color = GREEN
                    
                print_color(f"{subject}: 总数 {total}, 有效 {total-missing-invalid} ({(total-missing-invalid)*100/total:.1f}%), 问题数 {missing+invalid} ({problem_rate:.1f}%)", color)
        
        # 按文件类型统计
        print_color("\n=== 按文件类型统计 ===", GREEN)
        exts = defaultdict(int)
        missing_exts = defaultdict(int)
        invalid_exts = defaultdict(int)
        
        for paper in all_papers:
            if paper['file_path']:
                ext = os.path.splitext(paper['file_path'])[1].lower() or '无扩展名'
                exts[ext] += 1
        
        for paper in missing_files:
            if paper['file_path']:
                ext = os.path.splitext(paper['file_path'])[1].lower() or '无扩展名'
                missing_exts[ext] += 1
        
        for paper in invalid_files:
            if paper['file_path']:
                ext = os.path.splitext(paper['file_path'])[1].lower() or '无扩展名'
                invalid_exts[ext] += 1
        
        for ext, count in sorted(exts.items(), key=lambda x: x[1], reverse=True)[:10]:
            if count > 10:  # 只显示较常见的文件类型
                missing = missing_exts[ext]
                invalid = invalid_exts[ext]
                problem_rate = (missing + invalid) * 100 / count if count else 0
                
                color = RED if problem_rate > 50 else (YELLOW if problem_rate > 30 else GREEN)
                print_color(f"{ext}: 总数 {count}, 问题数 {missing+invalid} ({problem_rate:.1f}%)", color)
        
        return (missing_files, invalid_files)
    except Exception as e:
        print_color(f"批量检查文件时出错: {e}", RED)
        return ([], [])

def fix_specific_papers(found_files):
    """修复特定的试卷文件"""
    print_color("\n===== 修复特定试卷 =====", YELLOW)
    
    if not found_files:
        print_color("没有找到可以修复的文件", RED)
        return
    
    for paper_id, matches in found_files.items():
        try:
            # 获取试卷信息
            papers = load_paper_info(paper_ids=[paper_id])
            if not papers:
                continue
            
            paper = papers[0]
            print_color(f"\n修复试卷: ID={paper_id}, 名称={paper['name']}", BOLD)
            
            # 首先检查是否有精确匹配
            exact_matches = [m for m in matches if m['type'] == 'exact']
            if exact_matches:
                print_color(f"已有匹配文件，无需修复", GREEN)
                continue
            
            # 然后检查相似匹配
            similar_matches = [m for m in matches if m['type'] == 'similar']
            if not similar_matches:
                print_color(f"未找到可能匹配的文件，无法修复", RED)
                continue
            
            # 使用最佳匹配
            best_match = similar_matches[0]
            print_color(f"使用最佳匹配文件: {os.path.basename(best_match['path'])}", BLUE)
            
            # 更新数据库记录
            if update_file_path(paper_id, best_match['path']):
                print_color(f"✓ 成功更新文件路径", GREEN)
            else:
                print_color(f"✗ 更新文件路径失败", RED)
                
        except Exception as e:
            print_color(f"修复试卷 ID={paper_id} 时出错: {e}", RED)

def main():
    """主函数"""
    start_time = time.time()
    
    print_color("=" * 80, GREEN)
    print_color(" 检查和修复缺失的试卷文件 ", BOLD + GREEN)
    print_color("=" * 80, GREEN)
    print_color(f"项目目录: {PROJECT_DIR}")
    print_color(f"数据库路径: {DB_PATH}")
    print_color(f"上传目录: {UPLOADS_DIR}")
    print_color("=" * 80, GREEN)
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        # 搜索特定试卷
        found_files = search_specific_papers()
        
        # 修复特定试卷
        fix_specific_papers(found_files)
    else:
        # 批量检查所有缺失文件
        missing_files, invalid_paths = batch_check_missing_files()
        
        # 询问是否要尝试修复
        if len(missing_files) + len(invalid_paths) > 0:
            print_color("\n检测到有试卷文件缺失或无效", YELLOW)
            print_color("如需尝试自动修复，请使用以下命令运行修复脚本：", YELLOW)
            print_color("python3 fix_paper_downloads.py", BOLD + BLUE)
    
    end_time = time.time()
    print_color(f"\n执行时间: {end_time - start_time:.2f}秒", BLUE)
    print_color("=" * 80, GREEN)
    print_color("检查完成!", BOLD + GREEN)
    print_color("=" * 80, GREEN)

if __name__ == "__main__":
    main()
