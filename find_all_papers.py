#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全面检查和修复所有缺失的试卷文件
使用高级算法查找和匹配文件
创建时间: 2025-03-29
"""

import os
import re
import sqlite3
import sys
import time
import shutil
from datetime import datetime
from collections import defaultdict
import difflib

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
RESULTS_PATH = os.path.join(PROJECT_DIR, 'paper_recovery_results.txt')

def print_color(message, color=None, log_file=None):
    """打印彩色文本并可选择记录到日志文件"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)
    
    if log_file:
        with open(log_file, 'a', encoding='utf-8') as f:
            # 去除颜色代码写入日志
            f.write(f"{message}\n")

def get_db_connection():
    """连接到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn

def load_all_papers():
    """从数据库加载所有试卷信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, file_path, region, subject, year FROM papers")
        papers = cursor.fetchall()
        conn.close()
        return papers
    except Exception as e:
        print_color(f"加载试卷信息时出错: {e}", RED)
        return []

def check_file_exists(file_path):
    """检查文件是否存在"""
    if not file_path:
        return False, None
    
    # 先检查是否为绝对路径
    if os.path.isabs(file_path):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return True, file_path
    
    # 如果是相对路径，尝试从项目根目录解析
    full_path = os.path.join(PROJECT_DIR, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return True, full_path
    
    return False, None

def normalize_text(text):
    """标准化文本以便更好地匹配"""
    if not text:
        return ""
    
    # 转为小写
    text = text.lower()
    
    # 移除标点符号和特殊字符
    text = re.sub(r'[（）()【】\[\]《》<>{},.，。、:：；;!！?？]', ' ', text)
    
    # 替换常见别名词
    replacements = {
        '高三': '高3',
        '一模': '一轮',
        '二模': '二轮',
        '联考': '联合考试',
        '月考': '月测',
        '期中': '期中考试',
        '期末': '期末考试',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(paper_name, file_name=None):
    """从试卷名称和文件名中提取关键词"""
    if not paper_name:
        return []
    
    # 分解名称
    name_parts = paper_name.split()
    
    # 提取最有意义的关键词
    important_parts = []
    regions = []
    subjects = []
    year_match = re.search(r'20\d{2}[届-]?', paper_name)
    year = year_match.group(0) if year_match else None
    
    # 地区匹配
    region_patterns = [
        '湖北省', '武汉市', '黄石市', '襄阳市', '十堰市', '荆州市', '宜昌市',
        '云学', '腾云', '名校联盟', '联盟'
    ]
    
    # 学科匹配
    subject_patterns = [
        '语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理'
    ]
    
    for part in name_parts:
        # 检查是否为地区
        for pattern in region_patterns:
            if pattern in part:
                regions.append(part)
                break
        
        # 检查是否为学科
        for pattern in subject_patterns:
            if pattern in part:
                subjects.append(pattern)
                break
        
        # 提取其他重要信息
        if len(part) > 1 and part not in ['试卷', '试题', '答案', '解析', '含', '版']:
            important_parts.append(part)
    
    # 如果从文件名中提取
    if file_name:
        base_name = os.path.splitext(file_name)[0]
        # 去掉前缀数字和时间戳
        clean_base = re.sub(r'^\d+_\d+_\d+_', '', base_name)
        if clean_base:
            important_parts.append(clean_base)
    
    # 组合所有关键词
    keywords = []
    if regions:
        keywords.extend(regions)
    if subjects:
        keywords.extend(subjects)
    if year:
        keywords.append(year)
    if important_parts:
        keywords.extend(important_parts)
    
    return keywords

def score_similarity(paper_name, file_name):
    """计算试卷名称和文件名之间的相似度得分"""
    if not paper_name or not file_name:
        return 0
    
    score = 0
    paper_norm = normalize_text(paper_name)
    file_norm = normalize_text(file_name)
    
    # 1. 序列匹配相似度 (0-1分)
    seq_ratio = difflib.SequenceMatcher(None, paper_norm, file_norm).ratio()
    score += seq_ratio
    
    # 2. 关键词匹配
    paper_keywords = extract_keywords(paper_name)
    for keyword in paper_keywords:
        if keyword and keyword.lower() in file_norm:
            score += 0.2  # 每个关键词匹配加0.2分
    
    # 3. 年份匹配
    year_patterns = ['2025', '2024', '2023']
    for year in year_patterns:
        if year in paper_name and year in file_name:
            score += 0.5
            break
    
    # 4. 文件扩展名检查
    _, ext = os.path.splitext(file_name)
    if ext.lower() in ['.pdf', '.doc', '.docx', '.zip', '.rar']:
        score += 0.3
        
        # 如果文件名中提到了该格式，加分
        format_patterns = {
            '.pdf': ['pdf', 'PDF'],
            '.doc': ['doc', 'Doc', 'word', 'Word'],
            '.docx': ['docx', 'Docx', 'word', 'Word'],
            '.zip': ['zip', 'Zip'],
            '.rar': ['rar', 'Rar']
        }
        
        for pattern in format_patterns.get(ext.lower(), []):
            if pattern in paper_name:
                score += 0.5
                break
    
    # 5. 区域/学校匹配
    region_patterns = ['湖北', '武汉', '云学', '腾云', '联盟']
    for region in region_patterns:
        if region in paper_name and region in file_name:
            score += 1.0
            break
    
    # 6. 科目匹配
    subject_patterns = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    for subject in subject_patterns:
        if subject in paper_name and subject in file_name:
            score += 1.0
            break
    
    return score

def find_similar_files(paper, all_files=None, threshold=1.5):
    """查找与试卷相似的文件"""
    paper_name = paper['name']
    file_name = os.path.basename(paper['file_path']) if paper['file_path'] else None
    
    # 如果没有提供文件列表，则扫描整个上传目录
    if all_files is None:
        all_files = []
        for root, _, files in os.walk(UPLOADS_DIR):
            for f in files:
                all_files.append(os.path.join(root, f))
    
    matches = []
    for file_path in all_files:
        file_basename = os.path.basename(file_path)
        score = score_similarity(paper_name, file_basename)
        
        if score >= threshold:
            matches.append({
                'path': file_path,
                'score': score,
                'name': file_basename
            })
    
    # 按得分排序
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

def find_missing_papers():
    """查找并修复缺失的试卷文件"""
    # 初始化日志文件
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        f.write(f"试卷文件恢复结果日志\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
    
    print_color("正在加载所有试卷信息...", BLUE, RESULTS_PATH)
    all_papers = load_all_papers()
    total_papers = len(all_papers)
    print_color(f"共加载 {total_papers} 条试卷记录", BLUE, RESULTS_PATH)
    
    # 建立文件缓存，避免重复扫描文件系统
    print_color("正在扫描uploads目录中的所有文件...", BLUE, RESULTS_PATH)
    all_files = []
    for root, _, files in os.walk(UPLOADS_DIR):
        for f in files:
            all_files.append(os.path.join(root, f))
    print_color(f"共扫描到 {len(all_files)} 个文件", BLUE, RESULTS_PATH)
    
    # 按扩展名对文件进行分类
    files_by_ext = defaultdict(list)
    for file_path in all_files:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        files_by_ext[ext].append(file_path)
    
    print_color("文件类型分布:", BLUE, RESULTS_PATH)
    for ext, files in sorted(files_by_ext.items(), key=lambda x: len(x[1]), reverse=True):
        print_color(f"  {ext}: {len(files)}个文件", BLUE, RESULTS_PATH)
    
    # 统计变量
    missing_count = 0
    fixed_count = 0
    unfixable_count = 0
    
    print_color("\n开始检查和修复缺失文件...", YELLOW, RESULTS_PATH)
    
    # 开始检查每一条试卷记录
    for i, paper in enumerate(all_papers):
        # 每100条显示进度
        if i % 100 == 0:
            print_color(f"进度: {i}/{total_papers} ({i/total_papers*100:.2f}%)", BLUE)
        
        # 检查文件是否存在
        exists, full_path = check_file_exists(paper['file_path'])
        
        if exists:
            continue  # 文件存在，跳过
        
        missing_count += 1
        
        # 查找相似文件
        matches = find_similar_files(paper, all_files)
        
        # 在日志中记录当前试卷
        with open(RESULTS_PATH, 'a', encoding='utf-8') as f:
            f.write(f"ID: {paper['id']}, 名称: {paper['name']}\n")
            f.write(f"原始路径: {paper['file_path']}\n")
        
        if matches:
            best_match = matches[0]
            
            # 只有当分数足够高时才自动修复
            if best_match['score'] >= 2.5:
                # 更新数据库
                if update_file_path(paper['id'], best_match['path']):
                    fixed_count += 1
                    with open(RESULTS_PATH, 'a', encoding='utf-8') as f:
                        f.write(f"✓ 已自动修复 (得分: {best_match['score']:.2f})\n")
                        f.write(f"新路径: {best_match['path']}\n\n")
                    
                    # 每100个修复显示一次进度
                    if fixed_count % 100 == 0:
                        print_color(f"已修复: {fixed_count}个文件", GREEN)
            else:
                # 分数不够高，需要人工确认
                unfixable_count += 1
                with open(RESULTS_PATH, 'a', encoding='utf-8') as f:
                    f.write(f"? 找到可能的匹配，但置信度不够 (得分: {best_match['score']:.2f})\n")
                    for j, match in enumerate(matches[:3]):
                        f.write(f"  候选{j+1}: {match['name']} (得分: {match['score']:.2f})\n")
                    f.write("\n")
        else:
            # 未找到任何匹配
            unfixable_count += 1
            with open(RESULTS_PATH, 'a', encoding='utf-8') as f:
                f.write(f"✗ 未找到匹配文件\n\n")
    
    print_color("\n" + "="*80, GREEN, RESULTS_PATH)
    print_color("检查和修复总结:", BOLD + GREEN, RESULTS_PATH)
    print_color(f"总试卷数: {total_papers}", GREEN, RESULTS_PATH)
    print_color(f"缺失文件: {missing_count}", YELLOW, RESULTS_PATH)
    print_color(f"已修复: {fixed_count}", GREEN, RESULTS_PATH)
    print_color(f"未能修复: {unfixable_count}", RED, RESULTS_PATH)
    print_color("="*80 + "\n", GREEN, RESULTS_PATH)
    
    print_color(f"结果已保存到: {RESULTS_PATH}", BLUE)
    return fixed_count, unfixable_count

def find_specific_papers():
    """搜索特定的缺失试卷"""
    specific_papers = [
        "湖北省云学名校联盟2025届高三下学期2月联考试题 英语 PDF版含解析（含听力）",
        "湖北省腾云联盟2025届高三上学期12月联考（一模）英语试卷含听力 Word版含答案"
    ]
    
    # 查找这些特定试卷的ID
    conn = get_db_connection()
    paper_ids = []
    
    for paper_name in specific_papers:
        # 使用模糊匹配查找试卷
        cursor = conn.execute(
            "SELECT id FROM papers WHERE name LIKE ?",
            (f"%{paper_name}%",)
        )
        results = cursor.fetchall()
        if results:
            for r in results:
                paper_ids.append(r['id'])
    
    conn.close()
    
    if not paper_ids:
        print_color("未找到指定的试卷", RED)
        return
    
    print_color(f"找到 {len(paper_ids)} 条匹配记录", BLUE)
    
    # 对这些特定试卷进行深度搜索
    conn = get_db_connection()
    papers = []
    
    for paper_id in paper_ids:
        cursor = conn.execute(
            "SELECT id, name, file_path, region, subject, year FROM papers WHERE id = ?",
            (paper_id,)
        )
        result = cursor.fetchone()
        if result:
            papers.append(dict(result))
    
    conn.close()
    
    # 加载所有文件
    all_files = []
    for root, _, files in os.walk(UPLOADS_DIR):
        for f in files:
            all_files.append(os.path.join(root, f))
    
    # 使用更低的阈值进行更广泛的搜索
    for paper in papers:
        print_color(f"\n正在深度搜索: {paper['name']}", YELLOW)
        matches = find_similar_files(paper, all_files, threshold=0.8)
        
        if matches:
            print_color(f"找到 {len(matches)} 个可能匹配:", GREEN)
            for i, match in enumerate(matches[:5]):
                print_color(f"[{i+1}] 得分: {match['score']:.2f}, 文件: {match['name']}", GREEN)
                
                # 如果分数足够高，自动更新
                if match['score'] >= 1.5:
                    if update_file_path(paper['id'], match['path']):
                        print_color(f"✓ 已更新文件路径", GREEN)
        else:
            print_color(f"未找到任何可能的匹配", RED)

def main():
    """主函数"""
    start_time = time.time()
    
    print_color("=" * 80, GREEN)
    print_color(" 全面检查和修复所有缺失的试卷文件 ", BOLD + GREEN)
    print_color("=" * 80, GREEN)
    print_color(f"项目目录: {PROJECT_DIR}")
    print_color(f"数据库路径: {DB_PATH}")
    print_color(f"上传目录: {UPLOADS_DIR}")
    print_color("=" * 80, GREEN)
    
    # 是否要搜索特定试卷
    specific_search = input("是否要先搜索特定的试卷? (y/n): ").strip().lower()
    if specific_search == 'y':
        find_specific_papers()
    
    # 是否要全面检查所有缺失文件
    full_scan = input("是否要全面扫描所有缺失文件? (y/n): ").strip().lower()
    if full_scan == 'y':
        fixed, unfixed = find_missing_papers()
        print_color(f"共修复 {fixed} 个文件，还有 {unfixed} 个文件需要手动处理", BLUE)
    
    end_time = time.time()
    print_color(f"\n执行时间: {end_time - start_time:.2f}秒", BLUE)
    print_color("=" * 80, GREEN)
    print_color("检查完成!", BOLD + GREEN)
    print_color("=" * 80, GREEN)

if __name__ == "__main__":
    main()
