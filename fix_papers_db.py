#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复试卷数据库记录与真实文件的匹配 - 增强版
功能：更新数据库中papers表的file_path字段，使其指向真实的试卷文件
特别优化：增强对云学名校联盟等特定命名模式试卷的匹配
"""

import os
import re
import sqlite3
import glob
from datetime import datetime
from difflib import SequenceMatcher

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, 'questions.db')

# 可能的文件目录
PAPERS_DIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers')
PAPERS_SUBDIR = os.path.join(PROJECT_ROOT, 'uploads', 'papers', 'papers')
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')

# 计算字符串相似度
def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 规范化文件名以便于比较
def normalize_filename(filename):
    # 移除扩展名
    name = os.path.splitext(os.path.basename(filename))[0]
    # 移除常见的数字前缀（如时间戳）
    name = re.sub(r'^\d+_\d+_\d+_', '', name)
    # 移除特殊字符
    name = re.sub(r'[^\w\s\u4e00-\u9fff]+', '', name)
    # 转换为小写并去除额外空格
    name = re.sub(r'\s+', ' ', name).strip().lower()
    # 删除常见的无关词汇
    for word in ['云学名校联盟', '名校联盟', '资料', '答案', '试卷及答案', '试题', '及答案', '解析']:
        name = name.replace(word, '')
    return name.strip()

# 提取文件名中的关键特征
def extract_features(filename):
    """提取文件名中的关键特征"""
    features = {
        'year': None,
        'month': None,
        'subject': None,
        'region': None
    }
    
    # 提取年份（2023/2024/2025等）
    year_match = re.search(r'20\d{2}', filename)
    if year_match:
        features['year'] = year_match.group(0)
    
    # 提取月份（1-12月）
    month_match = re.search(r'[第]?([1一二三四五六七八九十]{1,2})[月]', filename)
    if month_match:
        month_map = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', 
                     '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
        month_text = month_match.group(1)
        features['month'] = month_map.get(month_text, month_text)
    else:
        # 尝试匹配"上/下学期"（上学期通常对应1-2月，下学期对应3月）
        if '下学期' in filename:
            features['month'] = '3' # 默认下学期对应3月
        elif '上学期' in filename:
            features['month'] = '1' # 默认上学期对应1月
    
    # 提取科目关键字
    subjects = {
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
        '理综': ['理综'],
        '综合': ['综合']
    }
    
    for subject, keywords in subjects.items():
        if any(keyword in filename for keyword in keywords):
            features['subject'] = subject
            break
    
    # 提取地区
    regions = ['湖北', '安徽', '北京', '重庆', '福建', '甘肃', '广东', '广西', '贵州', 
               '海南', '河北', '黑龙江', '河南', '湖南', '吉林', '江苏', '江西', '辽宁', 
               '内蒙古', '宁夏', '青海', '山东', '山西', '陕西', '上海', '四川', '天津', 
               '新疆', '西藏', '云南', '浙江']
    
    for region in regions:
        if region in filename:
            features['region'] = region
            break
    
    return features

# 查找文件的主函数 - 增强版
def find_paper_file(paper_id, paper_name, paper_year, paper_subject, paper_region):
    print(f"查找试卷: ID={paper_id}, 名称='{paper_name}', 年份={paper_year}, 科目={paper_subject}, 地区={paper_region}")
    
    # 收集所有可能的试卷文件
    all_files = []
    
    # 首先检查uploads/papers/papers目录
    if os.path.exists(PAPERS_SUBDIR):
        for root, _, files in os.walk(PAPERS_SUBDIR):
            for file in files:
                if file.endswith(('.pdf', '.docx', '.doc', '.zip', '.rar')):
                    all_files.append(os.path.join(root, file))
    
    # 然后检查uploads/papers目录
    if os.path.exists(PAPERS_DIR):
        for root, _, files in os.walk(PAPERS_DIR):
            for file in files:
                if file.endswith(('.pdf', '.docx', '.doc', '.zip', '.rar')):
                    all_files.append(os.path.join(root, file))
    
    # 最后检查uploads目录
    if os.path.exists(UPLOADS_DIR):
        for root, _, files in os.walk(UPLOADS_DIR):
            for file in files:
                if file.endswith(('.pdf', '.docx', '.doc', '.zip', '.rar')):
                    all_files.append(os.path.join(root, file))
    
    print(f"共找到 {len(all_files)} 个候选文件")
    
    # 匹配策略1: ID匹配
    id_pattern = f"_{paper_id}_"
    id_matches = [f for f in all_files if id_pattern in os.path.basename(f)]
    
    if id_matches:
        match = id_matches[0]
        print(f"✓ 通过ID匹配找到: {os.path.basename(match)}")
        return match, "ID匹配"
    
    # 处理这种特殊模式："云学名校联盟湖北省2025届高三下学期2月联考政治试卷及答案"
    if "云学名校联盟" in paper_name and "联考" in paper_name:
        # 提取关键信息：年份、月份、学科、地区
        features = {
            'year': str(paper_year),
            'subject': paper_subject,
            'region': paper_region,
            'month': None
        }
        
        # 尝试从名称中提取月份
        month_match = re.search(r'([1-9一二三四五六七八九十]{1,2})月', paper_name)
        if month_match:
            month_map = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', 
                         '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
            month_text = month_match.group(1)
            features['month'] = month_map.get(month_text, month_text)
        else:
            # 尝试匹配"上/下学期"（上学期通常对应1-2月，下学期对应3月）
            if '下学期' in paper_name:
                features['month'] = '3'  # 默认下学期是3月
            elif '上学期' in paper_name:
                features['month'] = '1'  # 默认上学期是1月
        
        # 权重评分系统
        best_match = None
        best_score = 0
        
        for file_path in all_files:
            file_basename = os.path.basename(file_path)
            file_features = extract_features(file_basename)
            
            # 初始分数
            score = 0
            
            # 年份匹配，权重最高
            if features['year'] == file_features['year']:
                score += 10
            
            # 学科匹配，权重次高
            if features['subject'] and features['subject'] == file_features['subject']:
                score += 8
            elif features['subject'] and features['subject'] in file_basename:
                score += 6
            
            # 地区匹配，也很重要
            if features['region'] and features['region'] == file_features['region']:
                score += 7
            elif features['region'] and features['region'] in file_basename:
                score += 5
            
            # 月份匹配
            if features['month'] and features['month'] == file_features['month']:
                score += 6
            
            # 文件名中是否包含关键信息
            if "联考" in file_basename:
                score += 4
            
            # 特定的名称模式匹配
            if "云学" in file_basename or "名校联盟" in file_basename:
                score += 5
            
            # 额外加分：如果是正确的扩展名类型（docx优先于pdf）
            if file_path.lower().endswith('.docx'):
                score += 2
            elif file_path.lower().endswith('.doc'):
                score += 1.5
            elif file_path.lower().endswith('.pdf'):
                score += 1
            
            # 如果得分足够高，认为是很好的匹配
            if score > best_score:
                best_score = score
                best_match = file_path
        
        # 如果评分超过阈值，认为找到了匹配
        if best_score >= 15:  # 设置一个合理的阈值
            print(f"✓ 通过特征评分匹配找到 (得分: {best_score}): {os.path.basename(best_match)}")
            return best_match, f"特征评分匹配 (得分: {best_score})"
    
    # 匹配策略2: 年份+科目+地区匹配
    year_str = str(paper_year)
    clean_subject = paper_subject.replace(" ", "").lower()
    clean_region = paper_region.replace(" ", "").lower() if paper_region else ""
    
    content_matches = []
    for file_path in all_files:
        file_basename = os.path.basename(file_path).lower()
        file_content = file_basename.replace(" ", "")
        
        # 检查文件是否包含年份+科目，可选地区
        matches_year_subject = year_str in file_content and clean_subject in file_content
        matches_region = not clean_region or clean_region in file_content
        
        if matches_year_subject and matches_region:
            # 给每个匹配项评分，优先选择更精确的匹配
            score = 0
            
            # 基本分数：年份+科目
            score += 10
            
            # 如果包含地区信息，加分
            if clean_region and clean_region in file_content:
                score += 5
            
            # 如果文件名长度更接近原始文件名，加分
            name_ratio = len(file_basename) / max(1, len(paper_name))
            if 0.5 <= name_ratio <= 1.5:  # 如果长度比例在合理范围内
                score += 3
            
            # 如果包含关键词，加分
            if "联考" in file_basename:
                score += 2
            
            # 特定命名模式加分
            if "云学" in file_basename or "名校联盟" in file_basename:
                score += 3
                
            content_matches.append((file_path, score))
    
    # 按得分降序排序
    if content_matches:
        content_matches.sort(key=lambda x: x[1], reverse=True)
        best_match, score = content_matches[0]
        print(f"✓ 通过年份+科目+地区匹配找到 (得分: {score}): {os.path.basename(best_match)}")
        return best_match, f"年份+科目+地区匹配 (得分: {score})"
    
    # 匹配策略3: 关键词提取匹配
    # 处理像"云学名校联盟湖北省2025届高三下学期2月联考政治试卷及答案"这样的名称
    # 提取关键部分："湖北省 2025 高三 2月 政治"
    
    key_parts_match = []
    for file_path in all_files:
        file_basename = os.path.basename(file_path).lower()
        
        # 分别检查各关键部分是否匹配
        matches = 0
        total_checks = 0
        
        # 检查年份
        if year_str:
            total_checks += 1
            if year_str in file_basename:
                matches += 1
        
        # 检查学科
        if paper_subject:
            total_checks += 1
            if paper_subject.lower() in file_basename:
                matches += 1
        
        # 检查地区
        if paper_region:
            total_checks += 1
            if paper_region.lower() in file_basename:
                matches += 1
        
        # 检查特定月份（从试卷名称中提取）
        month_match = re.search(r'([1-9一二三四五六七八九十]{1,2})月', paper_name)
        if month_match:
            month_text = month_match.group(0)
            total_checks += 1
            if month_text in paper_name and month_text in file_basename:
                matches += 1
        
        # 检查是否包含"联考"
        if "联考" in paper_name:
            total_checks += 1
            if "联考" in file_basename:
                matches += 1
                
        # 检查学期
        if "上学期" in paper_name:
            total_checks += 1
            if "上学期" in file_basename:
                matches += 1
        elif "下学期" in paper_name:
            total_checks += 1
            if "下学期" in file_basename:
                matches += 1
        
        # 计算匹配率
        match_rate = matches / max(1, total_checks)
        if match_rate >= 0.5:  # 如果匹配率>=50%
            key_parts_match.append((file_path, match_rate))
    
    if key_parts_match:
        key_parts_match.sort(key=lambda x: x[1], reverse=True)
        best_match, match_rate = key_parts_match[0]
        print(f"✓ 通过关键部分匹配找到 (匹配率: {match_rate:.2f}): {os.path.basename(best_match)}")
        return best_match, f"关键部分匹配 (匹配率: {match_rate:.2f})"
    
    # 匹配策略4: 名称相似度匹配（作为最后的备选）
    normalized_name = normalize_filename(paper_name)
    best_match = None
    best_score = 0.4  # 降低阈值，增加匹配几率
    
    for file_path in all_files:
        file_basename = os.path.basename(file_path)
        # 对文件名进行相同的规范化处理
        file_norm = normalize_filename(file_basename)
        
        # 如果规范化后的名称为空（所有关键词都被移除），使用原始名称进行匹配
        if not file_norm.strip():
            file_norm = file_basename.lower()
        
        similarity = string_similarity(normalized_name, file_norm)
        
        # 如果试卷科目在文件名中，增加相似度分数
        if paper_subject.lower() in file_basename.lower():
            similarity += 0.1  # 加10%的额外匹配度
        
        # 如果试卷年份在文件名中，增加相似度分数
        if year_str in file_basename:
            similarity += 0.1  # 加10%的额外匹配度
        
        if similarity > best_score:
            best_score = similarity
            best_match = file_path
    
    if best_match:
        print(f"✓ 通过名称相似度匹配找到 ({best_score:.2f}): {os.path.basename(best_match)}")
        return best_match, f"名称相似度匹配 ({best_score:.2f})"
    
    print(f"✗ 未找到匹配文件")
    return None, "未找到匹配"

def main():
    # 检查数据库是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库不存在: {DB_PATH}")
        return
    
    # 备份数据库
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{DB_PATH}.bak_{timestamp}"
    
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"已创建数据库备份: {backup_path}")
    except Exception as e:
        print(f"创建备份时出错: {e}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

    # 检查papers表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papers'")
    if not cursor.fetchone():
        print("错误: 数据库中不存在papers表")
        conn.close()
        return
    
    # 获取所有试卷记录
    cursor.execute("SELECT id, name, year, subject, region, file_path FROM papers")
papers = cursor.fetchall()
    print(f"数据库中有 {len(papers)} 条试卷记录")
    
    # 统计数据
    total_papers = len(papers)
    updated_papers = 0
    failed_papers = 0
    
    # 逐个处理试卷
    for paper in papers:
        paper_id, paper_name, paper_year, paper_subject, paper_region, current_path = paper
        
        # 查找匹配文件
        found_file, match_method = find_paper_file(paper_id, paper_name, paper_year, paper_subject, paper_region)
        
        if found_file:
            # 计算相对路径
            rel_path = os.path.relpath(found_file, PROJECT_ROOT)
            
            # 检查是否需要更新
            if rel_path != current_path:
                print(f"更新试卷 ID={paper_id} 的文件路径:")
                print(f"  - 原路径: {current_path}")
                print(f"  - 新路径: {rel_path}")
                print(f"  - 匹配方式: {match_method}")
                
                # 更新数据库
                try:
                    cursor.execute("UPDATE papers SET file_path = ? WHERE id = ?", (rel_path, paper_id))
                    updated_papers += 1
                except Exception as e:
                    print(f"更新数据库时出错: {e}")
                    failed_papers += 1
            else:
                print(f"试卷 ID={paper_id} 路径无需更新")
        else:
            failed_papers += 1
            print(f"❗ 试卷 ID={paper_id} '{paper_name}' 未找到匹配文件")

# 提交更改
conn.commit()
conn.close()
    
    # 打印统计信息
    print(f"\n===== 统计信息 =====")
    print(f"总试卷数: {total_papers}")
    print(f"已更新: {updated_papers}")
    print(f"失败: {failed_papers}")
    success_rate = (total_papers-failed_papers)/total_papers*100 if total_papers > 0 else 0
    print(f"成功率: {success_rate:.2f}%")
    
    print("\n任务完成！请重启应用以应用更改。")

if __name__ == "__main__":
    main()
