#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
试卷精确匹配工具
功能：确保数据库中的试卷记录准确对应到真实文件
"""

import os
import sqlite3
import re
import shutil
from datetime import datetime
import logging
import difflib

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('paper_matching.log')
    ]
)
logger = logging.getLogger(__name__)

# 颜色定义 (终端输出)
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 试卷目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')

# 特定试卷关键词映射 (用于更精确的匹配)
SPECIAL_KEYWORDS = {
    '云学名校联盟': ['云学名校联盟', '云学', '名校联盟'],
    '高考真题': ['高考真题', '高考模拟', '高考押题'],
    '期中考试': ['期中考试', '期中测试', '期中'],
    '期末考试': ['期末考试', '期末测试', '期末'],
    '学业水平测试': ['学业水平测试', '学业测试'],
    '联考': ['联考', '联合考试']
}

# 科目关键词映射
SUBJECT_KEYWORDS = {
    '语文': ['语文'],
    '数学': ['数学', '文数', '理数', '数学（文）', '数学（理）'],
    '英语': ['英语'],
    '物理': ['物理'],
    '化学': ['化学'],
    '生物': ['生物'],
    '政治': ['政治', '思想政治', '道德与法治'],
    '历史': ['历史'],
    '地理': ['地理'],
    '文综': ['文综', '文科综合'],
    '理综': ['理综', '理科综合']
}

# 区域关键词（省份）
REGION_KEYWORDS = {
    '全国': ['全国', '全国卷'],
    '北京': ['北京'],
    '天津': ['天津'],
    '河北': ['河北'],
    '山西': ['山西'],
    '内蒙古': ['内蒙古'],
    '辽宁': ['辽宁'],
    '吉林': ['吉林'],
    '黑龙江': ['黑龙江'],
    '上海': ['上海'],
    '江苏': ['江苏'],
    '浙江': ['浙江'],
    '安徽': ['安徽'],
    '福建': ['福建'],
    '江西': ['江西'],
    '山东': ['山东'],
    '河南': ['河南'],
    '湖北': ['湖北'],
    '湖南': ['湖南'],
    '广东': ['广东'],
    '广西': ['广西'],
    '海南': ['海南'],
    '重庆': ['重庆'],
    '四川': ['四川'],
    '贵州': ['贵州'],
    '云南': ['云南'],
    '西藏': ['西藏'],
    '陕西': ['陕西'],
    '甘肃': ['甘肃'],
    '青海': ['青海'],
    '宁夏': ['宁夏'],
    '新疆': ['新疆']
}

# 年级关键词
GRADE_KEYWORDS = {
    '高一': ['高一', '高1', '高中一年级'],
    '高二': ['高二', '高2', '高中二年级'],
    '高三': ['高三', '高3', '高中三年级'],
    '初一': ['初一', '初1', '初中一年级', '七年级'],
    '初二': ['初二', '初2', '初中二年级', '八年级'],
    '初三': ['初三', '初3', '初中三年级', '九年级']
}

def backup_database():
    """创建数据库备份"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{DB_PATH}.matching_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    logger.info(f"已创建数据库备份: {backup_path}")
    print(f"{YELLOW}已创建数据库备份: {backup_path}{NC}")
    return backup_path

def extract_keywords(text):
    """从文本中提取关键信息"""
    info = {
        'subject': None,
        'region': None,
        'year': None,
        'grade': None,
        'special_type': None,
    }
    
    # 提取年份 (4位数字)
    year_match = re.search(r'(20\d{2})', text)
    if year_match:
        info['year'] = year_match.group(1)
    
    # 提取科目
    for subject, keywords in SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                info['subject'] = subject
                break
        if info['subject']:
            break
    
    # 提取区域
    for region, keywords in REGION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                info['region'] = region
                break
        if info['region']:
            break
    
    # 提取年级
    for grade, keywords in GRADE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                info['grade'] = grade
                break
        if info['grade']:
            break
    
    # 提取特殊试卷类型
    for special_type, keywords in SPECIAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                info['special_type'] = special_type
                break
        if info['special_type']:
            break
    
    return info

def get_all_paper_files():
    """获取所有试卷文件及其元信息"""
    paper_files = []
    
    for root, _, files in os.walk(PAPERS_DIR):
        for filename in files:
            if filename.startswith('.'):
                continue
                
            if not filename.lower().endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                continue
                
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)
            
            # 提取文件名中的关键信息
            file_info = extract_keywords(filename)
            
            paper_files.append({
                'path': rel_path,
                'filename': filename,
                'info': file_info
            })
    
    return paper_files

def calculate_similarity(paper_name, file_info):
    """计算试卷名称与文件信息的匹配度"""
    score = 0
    max_score = 0
    
    # 提取试卷名称中的关键信息
    paper_info = extract_keywords(paper_name)
    
    # 科目匹配 (权重: 10)
    if paper_info['subject'] and file_info['subject']:
        max_score += 10
        if paper_info['subject'] == file_info['subject']:
            score += 10
    
    # 区域匹配 (权重: 5)
    if paper_info['region'] and file_info['region']:
        max_score += 5
        if paper_info['region'] == file_info['region']:
            score += 5
    
    # 年份匹配 (权重: 8)
    if paper_info['year'] and file_info['year']:
        max_score += 8
        if paper_info['year'] == file_info['year']:
            score += 8
    
    # 年级匹配 (权重: 6)
    if paper_info['grade'] and file_info['grade']:
        max_score += 6
        if paper_info['grade'] == file_info['grade']:
            score += 6
    
    # 特殊类型匹配 (权重: 7)
    if paper_info['special_type'] and file_info['special_type']:
        max_score += 7
        if paper_info['special_type'] == file_info['special_type']:
            score += 7
    
    # 文本相似度 (使用difflib)
    text_similarity = difflib.SequenceMatcher(None, paper_name, file_info['filename']).ratio()
    text_score = text_similarity * 10  # 满分10分
    score += text_score
    max_score += 10
    
    # 防止除零错误
    if max_score == 0:
        return 0
    
    # 返回百分比得分
    return (score / max_score) * 100

def exact_match_papers():
    """精确匹配试卷名称与文件"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, name, subject, region, file_path FROM papers")
    papers = cursor.fetchall()
    
    total_records = len(papers)
    logger.info(f"找到 {total_records} 条试卷记录")
    print(f"\n{GREEN}找到 {total_records} 条试卷记录{NC}")
    
    # 获取所有试卷文件
    all_files = get_all_paper_files()
    total_files = len(all_files)
    logger.info(f"找到 {total_files} 个试卷文件")
    print(f"{GREEN}找到 {total_files} 个试卷文件{NC}")
    
    if total_files == 0:
        logger.error("未找到任何试卷文件，无法进行匹配")
        print(f"{RED}错误: 未找到任何试卷文件，无法进行匹配{NC}")
        conn.close()
        return
    
    # 更新计数
    updated = 0
    not_updated = 0
    
    # 遍历每条试卷记录
    for paper_id, name, subject, region, current_path in papers:
        # 检查当前路径是否有效
        current_full_path = os.path.join(PROJECT_ROOT, current_path) if current_path else None
        if current_full_path and os.path.exists(current_full_path):
            # 文件已存在，跳过
            not_updated += 1
            continue
        
        # 首先查找科目和名称完全匹配的文件
        best_match = None
        best_score = 0
        
        for file_info in all_files:
            # 计算匹配分数
            score = calculate_similarity(name, file_info)
            
            # 如果是特定需求的试卷，记录日志
            if "云学名校联盟" in name and "语文" in name:
                logger.info(f"云学语文试卷匹配: [{score:.1f}%] {name} -> {file_info['filename']}")
            
            # 更新最佳匹配
            if score > best_score:
                best_score = score
                best_match = file_info
        
        # 如果找到匹配度大于60%的文件，更新数据库
        if best_match and best_score > 60:
            new_path = best_match['path']
            cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (new_path, paper_id))
            updated += 1
            
            # 对于特定类型的试卷，输出匹配信息
            if "云学名校联盟" in name and "语文" in name:
                logger.info(f"已匹配云学名校联盟语文试卷: [{best_score:.1f}%] {name}")
                print(f"{CYAN}已匹配云学名校联盟语文试卷: [{best_score:.1f}%]{NC}")
                print(f"  {BLUE}试卷: {name}{NC}")
                print(f"  {GREEN}文件: {best_match['filename']}{NC}")
            
            # 每1000条记录显示一次进度
            if updated % 1000 == 0:
                print(f"{BLUE}已更新 {updated} 条记录...{NC}")
        
    # 提交更改
    conn.commit()
    conn.close()
    
    logger.info(f"匹配完成! 总记录数: {total_records}, 已更新: {updated}, 未更新(已有文件): {not_updated}")
    print(f"\n{GREEN}匹配完成!{NC}")
    print(f"总记录数: {total_records}")
    print(f"已更新记录: {updated}")
    print(f"未更新记录(已有文件): {not_updated}")

def main():
    """主函数"""
    print(f"\n{GREEN}===== 试卷精确匹配工具 ====={NC}")
    
    # 检查papers目录是否存在
    if not os.path.exists(PAPERS_DIR):
        logger.error(f"试卷目录不存在: {PAPERS_DIR}")
        print(f"{RED}错误: 试卷目录不存在: {PAPERS_DIR}{NC}")
        return
    
    # 备份数据库
    backup_path = backup_database()
    
    # 精确匹配试卷
    print(f"\n{YELLOW}正在进行试卷精确匹配...{NC}")
    exact_match_papers()
    
    print(f"\n{GREEN}匹配完成!{NC}")
    logger.info(f"数据库已备份为: {backup_path}")
    print(f"{YELLOW}数据库已备份为: {backup_path}{NC}")
    print(f"{YELLOW}请重启应用以应用更改{NC}")

if __name__ == "__main__":
    main() 