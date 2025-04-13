#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找所有缺失的真实试卷文件并更新数据库路径
使用高级匹配算法将数据库记录与实际文件关联
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
RESULTS_PATH = os.path.join(PROJECT_DIR, 'match_real_files_results.txt')
MATCH_THRESHOLD = 2.5  # 自动更新数据库的相似度得分阈值

def print_color(message, color=None, log_file=None):
    """打印彩色文本并可选择记录到日志文件"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)
    
    if log_file:
        log_message = re.sub(r'\033\[[0-9;]*m', '', message) # 去除颜色代码
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{log_message}\n")

def get_db_connection():
    """连接到数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print_color(f"数据库连接错误: {e}", RED)
        sys.exit(1)

def create_backup():
    """创建数据库备份"""
    backup_dir = os.path.join(PROJECT_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = os.path.join(backup_dir, f"questions_db_before_match_{timestamp}.db")
    try:
        shutil.copy2(DB_PATH, backup_path)
        print_color(f"已创建数据库备份: {backup_path}", GREEN, RESULTS_PATH)
        return True
    except Exception as e:
        print_color(f"创建备份失败: {e}", RED, RESULTS_PATH)
        return False

def load_all_papers_from_db():
    """从数据库加载所有试卷信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 加载所有相关字段用于匹配
        cursor.execute("SELECT id, name, file_path, region, subject, year FROM papers")
        papers = cursor.fetchall()
        conn.close()
        # 将sqlite3.Row转换为字典列表，方便处理
        return [dict(p) for p in papers]
    except Exception as e:
        print_color(f"加载试卷信息时出错: {e}", RED, RESULTS_PATH)
        return []

def scan_upload_files():
    """扫描uploads目录中的所有文件"""
    all_files = []
    print_color(f"开始扫描上传目录: {UPLOADS_DIR}", BLUE, RESULTS_PATH)
    start_scan = time.time()
    file_count = 0
    try:
        for root, _, files in os.walk(UPLOADS_DIR):
            for f in files:
                # 忽略隐藏文件和常见临时文件
                if f.startswith('.') or f.endswith( ('.tmp', '.temp') ):
                    continue
                full_path = os.path.join(root, f)
                try:
                    # 尝试获取文件大小以确认可访问性
                    size = os.path.getsize(full_path)
                    # 存储绝对路径和文件名
                    all_files.append({'path': full_path, 'name': f, 'size': size})
                    file_count += 1
                    if file_count % 5000 == 0:
                         print_color(f"  已扫描 {file_count} 个文件...", BLUE)
                except OSError as e:
                     print_color(f"  无法访问文件 {full_path}: {e}", YELLOW, RESULTS_PATH)
                     continue # 跳过无法访问的文件
    except Exception as e:
        print_color(f"扫描文件时出错: {e}", RED, RESULTS_PATH)
    
    end_scan = time.time()
    print_color(f"扫描完成，共找到 {file_count} 个有效文件，耗时 {end_scan - start_scan:.2f} 秒", GREEN, RESULTS_PATH)
    return all_files

def check_file_path_valid(file_path):
    """检查数据库中的文件路径是否有效且存在"""
    if not file_path or not isinstance(file_path, str):
        return False, None
    
    # 尝试多种路径组合
    possible_paths = [
        file_path, # 直接使用路径
        os.path.join(PROJECT_DIR, file_path), # 相对于项目根目录
        os.path.join(UPLOADS_DIR, file_path), # 相对于uploads目录
        os.path.join(PROJECT_DIR, 'static', file_path) # 兼容旧的static路径?
    ]
    
    # 添加uploads子目录的检查
    if 'uploads/' not in file_path.lower() and not os.path.isabs(file_path):
        possible_paths.append(os.path.join(UPLOADS_DIR, file_path))
        possible_paths.append(os.path.join(UPLOADS_DIR, 'papers', 'papers', os.path.basename(file_path))) # 特殊嵌套目录

    for p in possible_paths:
        # 规范化路径，处理 `.` 和 `..`
        abs_path = os.path.abspath(p)
        # 确保路径在项目目录内，防止路径遍历攻击
        if not abs_path.startswith(os.path.abspath(PROJECT_DIR)):
             continue
        
        try:
            if os.path.exists(abs_path) and os.path.isfile(abs_path):
                # 确认文件可读
                with open(abs_path, 'rb') as f_test:
                    f_test.read(1)
                return True, abs_path # 返回找到的绝对路径
        except (IOError, OSError):
            continue # 文件存在但不可读，视为无效
            
    return False, None

def normalize_text(text):
    """标准化文本以便更好地匹配 (保持和 find_all_papers 一致)"""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[（）()【】\[\]《》<>{}.,，。、:：；;!！?？_\-\\/]', ' ', text)
    replacements = {
        '高三': '高3', '一模': '一轮', '二模': '二轮',
        '联考': '联合考试', '月考': '月测', '期中': '期中考试', '期末': '期末考试',
        'word': '文档', 'pdf': '文档', 'docx': '文档', 'zip': '压缩包', 'rar': '压缩包',
        '试卷': '', '试题': '', '答案': '', '解析': '', '含': '', '版': ''
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_keywords_from_name(paper_name):
    """从试卷名称中提取关键词"""
    if not paper_name:
        return set()
    
    norm_name = normalize_text(paper_name)
    # 提取所有长度大于1的词语作为关键词
    keywords = {word for word in norm_name.split() if len(word) > 1}
    
    # 添加年份 (如 2025)
    year_match = re.search(r'(20\d{2})', paper_name)
    if year_match:
        keywords.add(year_match.group(1))
        
    # 添加可能的学科
    subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    for subj in subjects:
        if subj in paper_name:
            keywords.add(subj)
            
    # 添加可能的地区或机构关键词
    regions = ['湖北', '武汉', '云学', '腾云', '联盟', '名校']
    for region in regions:
        if region in paper_name:
            keywords.add(region)
            
    return keywords

def score_similarity(paper_record, file_info):
    """计算数据库记录和文件信息之间的相似度得分 (改进版)"""
    paper_name = paper_record.get('name', '')
    file_name = file_info.get('name', '')
    
    if not paper_name or not file_name:
        return 0
    
    score = 0
    paper_norm = normalize_text(paper_name)
    file_norm = normalize_text(file_name)
    
    # 1. Jaccard 相似度 (基于词语集合) (0-1分)
    paper_words = set(paper_norm.split())
    file_words = set(file_norm.split())
    intersection = len(paper_words.intersection(file_words))
    union = len(paper_words.union(file_words))
    jaccard_sim = intersection / union if union > 0 else 0
    score += jaccard_sim * 2 # Jaccard 权重设为 2
    
    # 2. SequenceMatcher 相似度 (0-1分)
    seq_ratio = difflib.SequenceMatcher(None, paper_norm, file_norm).ratio()
    score += seq_ratio # SequenceMatcher 权重设为 1
    
    # 3. 关键词匹配 (每个匹配加分)
    paper_keywords = extract_keywords_from_name(paper_name)
    matched_keywords = 0
    for keyword in paper_keywords:
        if keyword and keyword in file_norm:
            score += 0.3 # 每个关键词匹配加 0.3 分
            matched_keywords += 1
    
    # 4. 关键信息匹配 (年份、学科、区域)
    # 年份
    year_match_db = re.search(r'(20\d{2})', paper_name)
    year_db = year_match_db.group(1) if year_match_db else None
    if year_db and year_db in file_name:
        score += 1.0 # 年份匹配加 1 分
        
    # 学科
    subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理']
    for subj in subjects:
        if subj in paper_name and subj in file_name:
            score += 1.0 # 学科匹配加 1 分
            break # 只加一次分
            
    # 区域/机构
    regions = ['湖北', '武汉', '云学', '腾云', '联盟', '名校']
    for region in regions:
        if region in paper_name and region in file_name:
            score += 0.5 # 区域匹配加 0.5 分
            break
            
    # 5. 文件类型检查 (如果名称中提到类型)
    _, file_ext = os.path.splitext(file_name)
    file_ext = file_ext.lower()
    format_hints = {
        'pdf': ['.pdf'],
        'word': ['.doc', '.docx'], '文档': ['.doc', '.docx', '.pdf'],
        'zip': ['.zip'], 'rar': ['.rar'], '压缩包': ['.zip', '.rar']
    }
    for hint, exts in format_hints.items():
        if hint in paper_norm and file_ext in exts:
            score += 0.5 # 类型暗示匹配加 0.5 分
            break

    # 6. 如果文件名包含数据库记录的ID，给予高分奖励
    paper_id_str = str(paper_record.get('id', ''))
    if paper_id_str and f"_{paper_id_str}." in file_name or file_name.startswith(paper_id_str + "_"):
        score += 3.0 # ID 匹配奖励 3 分 (很强的信号)
            
    return score

def find_best_match_for_paper(paper_record, all_files_index):
    """为单个试卷记录查找最佳匹配文件"""
    matches = []
    for file_info in all_files_index:
        score = score_similarity(paper_record, file_info)
        if score > 1.0: # 基础过滤，得分太低的直接忽略
            matches.append({
                'path': file_info['path'],
                'name': file_info['name'],
                'score': score
            })
    
    # 按得分排序，返回最佳匹配
    if matches:
        return sorted(matches, key=lambda x: x['score'], reverse=True)[0]
    else:
        return None

def update_paper_path_in_db(paper_id, new_file_path):
    """更新数据库中的文件路径"""
    try:
        # 计算相对于项目根目录的路径
        relative_path = os.path.relpath(new_file_path, PROJECT_DIR)
        # 统一使用 posix 风格的路径分隔符 `/`
        relative_path = relative_path.replace(os.path.sep, '/')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (relative_path, paper_id))
        conn.commit()
        conn.close()
        return True, relative_path
    except Exception as e:
        print_color(f"更新数据库时出错 (ID: {paper_id}): {e}", RED, RESULTS_PATH)
        return False, None

def main():
    """主函数"""
    start_time = time.time()
    # 初始化日志
    with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
        f.write(f"真实试卷文件匹配与修复日志\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")

    print_color("=" * 80, BOLD + GREEN)
    print_color(" 开始查找真实试卷文件并更新数据库路径 ", BOLD + GREEN)
    print_color("=" * 80, BOLD + GREEN)

    # 1. 创建备份
    if not create_backup():
        if input("数据库备份失败，是否继续? (y/n): ").lower() != 'y':
            print_color("操作已取消", RED)
            return
        print_color("警告: 未创建备份，继续执行...", YELLOW, RESULTS_PATH)

    # 2. 加载所有数据库记录
    print_color("正在加载数据库中的所有试卷记录...", BLUE, RESULTS_PATH)
    all_db_papers = load_all_papers_from_db()
    total_db_records = len(all_db_papers)
    if total_db_records == 0:
        print_color("未能从数据库加载任何试卷记录，无法继续", RED, RESULTS_PATH)
        return
    print_color(f"从数据库加载了 {total_db_records} 条试卷记录", GREEN, RESULTS_PATH)

    # 3. 扫描文件系统
    all_upload_files = scan_upload_files()
    if not all_upload_files:
        print_color("在 uploads 目录中未找到任何文件，无法进行匹配", RED, RESULTS_PATH)
        return

    # 4. 识别需要修复的记录
    papers_to_fix = []
    valid_papers_count = 0
    print_color("正在检查数据库记录对应的文件有效性...", BLUE, RESULTS_PATH)
    checked_count = 0
    for paper in all_db_papers:
        is_valid, _ = check_file_path_valid(paper.get('file_path'))
        if not is_valid:
            papers_to_fix.append(paper)
        else:
            valid_papers_count += 1
        checked_count += 1
        if checked_count % 1000 == 0:
             print_color(f"  已检查 {checked_count}/{total_db_records} 条记录...", BLUE)
             
    initial_missing_count = len(papers_to_fix)
    print_color(f"检查完成: {valid_papers_count} 条记录已有有效文件，{initial_missing_count} 条记录需要尝试匹配", GREEN, RESULTS_PATH)

    if initial_missing_count == 0:
        print_color("所有数据库记录都已指向有效文件，无需修复！", GREEN, RESULTS_PATH)
        return

    # 5. 进行匹配和更新
    print_color(f"开始为 {initial_missing_count} 条记录查找匹配的真实文件...", YELLOW, RESULTS_PATH)
    fixed_count = 0
    still_unmatched = []
    processed_count = 0

    for paper in papers_to_fix:
        processed_count += 1
        if processed_count % 100 == 0:
            progress = processed_count / initial_missing_count * 100
            print_color(f"  匹配进度: {processed_count}/{initial_missing_count} ({progress:.1f}%) - 已修复: {fixed_count}", BLUE)
        
        best_match = find_best_match_for_paper(paper, all_upload_files)
        
        log_entry = f"\n处理 ID: {paper['id']}, 名称: {paper['name']}\n  原始路径: {paper['file_path']}"
        
        if best_match and best_match['score'] >= MATCH_THRESHOLD:
            # 找到高置信度匹配，更新数据库
            success, new_rel_path = update_paper_path_in_db(paper['id'], best_match['path'])
            if success:
                fixed_count += 1
                log_entry += f"\n{GREEN}✓ 找到匹配并更新! (得分: {best_match['score']:.2f}){NC}\n  新文件: {best_match['name']}\n  新路径: {new_rel_path}"
            else:
                log_entry += f"\n{RED}✗ 找到匹配但数据库更新失败 (得分: {best_match['score']:.2f}){NC}\n  匹配文件: {best_match['name']}"
                still_unmatched.append(paper) # 更新失败也算未匹配
        elif best_match:
             # 找到匹配但分数不够高
             log_entry += f"\n{YELLOW}? 找到低置信度匹配 (得分: {best_match['score']:.2f}) - 未自动更新{NC}\n  最相似文件: {best_match['name']}"
             still_unmatched.append(paper)
        else:
            # 未找到任何像样的匹配
            log_entry += f"\n{RED}✗ 未找到任何匹配的文件{NC}"
            still_unmatched.append(paper)
            
        print_color(log_entry, log_file=RESULTS_PATH) # 记录日志

    # 6. 输出总结报告
    final_unmatched_count = len(still_unmatched)
    end_time = time.time()
    
    summary = f"\n" + "="*80 + "\n"
    summary += f" 匹配与修复总结 \n"
    summary += f"" + "="*80 + "\n"
    summary += f"总处理时间: {end_time - start_time:.2f} 秒\n"
    summary += f"数据库总记录数: {total_db_records}\n"
    summary += f"初始有效记录数: {valid_papers_count}\n"
    summary += f"需要匹配的记录数: {initial_missing_count}\n"
    summary += f"{GREEN}成功匹配并更新数据库: {fixed_count} 条{NC}\n"
    summary += f"{RED}最终未能匹配/更新的记录: {final_unmatched_count} 条{NC}\n"
    summary += f"="*80 + "\n"
    summary += f"详细日志已保存到: {RESULTS_PATH}\n"
    
    if final_unmatched_count > 0:
        summary += f"\n以下 {final_unmatched_count} 条记录未能找到对应的真实文件:\n"
        for i, paper in enumerate(still_unmatched):
            if i < 50: # 最多显示前 50 条
                 summary += f"  - ID: {paper['id']}, 名称: {paper['name']}\n"
            elif i == 50:
                 summary += f"  ... (更多未匹配记录请查看日志文件)"
                 break
    
    print_color(summary, BOLD + BLUE)
    # 也将总结写入日志文件顶部
    with open(RESULTS_PATH, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        # 去掉颜色代码再写入
        log_summary = re.sub(r'\033\[[0-9;]*m', '', summary)
        f.write(log_summary + "\n" + "="*80 + "\n\n" + content)

if __name__ == "__main__":
    main()
