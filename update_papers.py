#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import sqlite3
import shutil
from datetime import datetime
import logging
from tqdm import tqdm

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_papers.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, 'instance', 'questions.db')
# Zujuanwang上传目录
UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'zujuanwang', 'uploads')
# 系统uploads目录
SYSTEM_UPLOADS_DIR = os.path.join(PROJECT_ROOT, 'uploads')
# 系统papers目录
PAPERS_DIR = os.path.join(SYSTEM_UPLOADS_DIR, 'papers')

# 确保目录存在
for dir_path in [SYSTEM_UPLOADS_DIR, PAPERS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# 要匹配的湖北系列试卷
target_papers = [
    {
        "name": "湖北省云学名校联盟2025届高三下学期2月联考试题 英语 PDF版含解析（含听力）",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省云学名校联盟",
        "year": 2025,
        "keywords": ["湖北", "云学", "名校联盟", "高三", "下学期", "2月", "联考", "英语", "听力"]
    },
    {
        "name": "湖北省云学名校联盟2025届高三下学期2月联考试题 日语 PDF版含答案（含听力）",
        "region": "湖北",
        "subject": "英语",  # 系统中分类为英语
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省云学名校联盟",
        "year": 2025,
        "keywords": ["湖北", "云学", "名校联盟", "高三", "下学期", "2月", "联考", "日语", "听力"]
    },
    {
        "name": "湖北省圆创高中名校联盟2025届高三下学期2月第三次联合测评试题 英语 PDF版含解析（含听力）",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省圆创高中名校联盟",
        "year": 2025,
        "keywords": ["湖北", "圆创", "高中", "名校联盟", "高三", "下学期", "2月", "联合测评", "英语", "听力"]
    },
    {
        "name": "湖北省圆创高中名校联盟2025届高三下学期2月第三次联合测评试题 日语 PDF版含答案（含听力）",
        "region": "湖北",
        "subject": "英语",  # 系统中分类为英语
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省圆创高中名校联盟",
        "year": 2025,
        "keywords": ["湖北", "圆创", "高中", "名校联盟", "高三", "下学期", "2月", "联合测评", "日语", "听力"]
    },
    {
        "name": "湖北省新八校协作体2025届高三下学期2月联考试题 英语 PDF版含解析（含听力）",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省新八校协作体",
        "year": 2025,
        "keywords": ["湖北", "新八校", "协作体", "高三", "下学期", "2月", "联考", "英语", "听力"]
    },
    {
        "name": "湖北省新八校协作体2025届高三下学期2月联考试题 日语 PDF版含答案（含听力）",
        "region": "湖北",
        "subject": "英语",  # 系统中分类为英语
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省新八校协作体",
        "year": 2025,
        "keywords": ["湖北", "新八校", "协作体", "高三", "下学期", "2月", "联考", "日语", "听力"]
    },
    {
        "name": "湖北省腾云联盟2025届高三上学期12月联考（一模）英语试卷含听力 Word版含答案",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省腾云联盟",
        "year": 2025,
        "keywords": ["湖北", "腾云联盟", "高三", "上学期", "12月", "联考", "一模", "英语", "听力"]
    },
    {
        "name": "湖北省武汉市江岸区2024-2025学年高三上学期1月期末考试 英语 PDF版含答案（含听力）",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省部分重点中学",
        "year": 2025,
        "keywords": ["湖北", "武汉市", "江岸区", "高三", "上学期", "1月", "期末考试", "英语", "听力"]
    },
    {
        "name": "湖北省重点高中智学联盟2025届高三上学期8月联考试题 英语 PDF版含解析（可编辑 含听力）",
        "region": "湖北",
        "subject": "英语",
        "stage": "高中",
        "source_type": "地区联考",
        "source": "湖北省重点高中智学联盟",
        "year": 2025,
        "keywords": ["湖北", "重点高中", "智学联盟", "高三", "上学期", "8月", "联考", "英语", "听力"]
    }
]

def search_file_with_score(paper_info, file_extension=None):
    """
    使用评分系统寻找最匹配的文件
    
    Args:
        paper_info: 试卷信息字典
        file_extension: 可选的文件扩展名筛选
        
    Returns:
        最匹配的文件路径
    """
    # 收集所有可能的试卷文件
    all_files = []
    for root, _, files in os.walk(UPLOADS_DIR):
        for file in files:
            # 根据文件扩展名筛选
            if file_extension:
                if file.lower().endswith(file_extension.lower()):
                    all_files.append(os.path.join(root, file))
            else:
                if file.lower().endswith(('.pdf', '.doc', '.docx', '.zip', '.rar')):
                    all_files.append(os.path.join(root, file))
    
    logger.info(f"找到 {len(all_files)} 个候选文件")
    
    # 提取试卷关键信息
    keywords = paper_info.get("keywords", [])
    year = str(paper_info.get("year", ""))
    subject = paper_info.get("subject", "").lower()
    
    # 评分系统找最匹配的文件
    best_match = None
    best_score = 0
    
    for file_path in all_files:
        file_basename = os.path.basename(file_path).lower()
        file_path_lower = file_path.lower()
        
        # 初始分数
        score = 0
        
        # 基础匹配项
        if year in file_basename:
            score += 10  # 年份很重要
        
        if subject in file_basename:
            score += 8   # 科目也很重要
        
        # 关键词匹配
        for keyword in keywords:
            if keyword.lower() in file_basename or keyword.lower() in file_path_lower:
                score += 3
        
        # 文件大小评分（假设有效文件>10KB）
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024:  # 大于10KB
            score += 5
        elif file_size < 1024:  # 小于1KB可能是占位文件
            score -= 10
        
        # 如果得分足够高
        if score > best_score:
            best_score = score
            best_match = file_path
    
    if best_match and best_score >= 15:
        logger.info(f"找到匹配文件 (得分: {best_score}): {best_match}")
        return best_match
    
    return None

def db_execute(query, params=(), fetch=False):
    """执行数据库查询"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        logger.error(f"数据库操作失败: {e}")
        result = None
    finally:
        conn.close()
    return result

def paper_exists(paper_name):
    """检查试卷是否已存在于数据库中"""
    query = "SELECT id FROM papers WHERE name = ?"
    result = db_execute(query, (paper_name,), fetch=True)
    return bool(result)

def add_paper_to_db(paper_info, file_path):
    """添加试卷到数据库"""
    # 计算相对路径
    rel_path = os.path.relpath(file_path, PROJECT_ROOT)
    
    # 检查试卷是否已存在
    if paper_exists(paper_info["name"]):
        logger.info(f"试卷已存在: {paper_info['name']}")
        # 更新文件路径
        query = "UPDATE papers SET file_path = ? WHERE name = ?"
        db_execute(query, (rel_path, paper_info["name"]))
        logger.info(f"已更新试卷文件路径: {rel_path}")
        return False
    
    # 添加新试卷
    query = """
    INSERT INTO papers (name, region, subject, stage, source, source_type, year, file_path, upload_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        paper_info["name"],
        paper_info["region"],
        paper_info["subject"],
        paper_info["stage"],
        paper_info["source"],
        paper_info["source_type"],
        paper_info["year"],
        rel_path,
        datetime.now()
    )
    paper_id = db_execute(query, params)
    logger.info(f"新增试卷: ID={paper_id}, 名称={paper_info['name']}")
    return True

def create_dummy_file(paper_info, extension=".pdf"):
    """为未找到的试卷创建一个占位文件，以便后续更新"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_dummy_{paper_info['name']}{extension}"
    file_name = re.sub(r'[^\w\-_.]', '_', file_name)  # 清理文件名
    file_path = os.path.join(PAPERS_DIR, file_name)
    
    # 创建一个空文件
    with open(file_path, 'w') as f:
        f.write(f"占位文件: {paper_info['name']}\n创建时间: {datetime.now()}")
    
    logger.info(f"创建占位文件: {file_path}")
    return file_path

def main():
    """主函数"""
    logger.info("开始更新试卷数据...")
    
    # 检查上传目录是否存在
    if not os.path.exists(UPLOADS_DIR):
        logger.error(f"上传目录不存在: {UPLOADS_DIR}")
        return
    
    # 检查数据库是否存在
    if not os.path.exists(DB_PATH):
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return
    
    # 处理每份试卷
    added_count = 0
    updated_count = 0
    dummy_count = 0
    
    for paper_info in tqdm(target_papers, desc="处理试卷"):
        logger.info(f"处理试卷: {paper_info['name']}")
        
        # 尝试找到匹配的文件
        matched_file = search_file_with_score(paper_info)
        
        if matched_file:
            # 复制文件到系统papers目录
            file_ext = os.path.splitext(matched_file)[1]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{paper_info['year']}_{paper_info['subject']}{file_ext}"
            new_file_path = os.path.join(PAPERS_DIR, new_filename)
            
            try:
                shutil.copy2(matched_file, new_file_path)
                logger.info(f"已复制文件: {matched_file} -> {new_file_path}")
                
                # 添加到数据库
                is_new = add_paper_to_db(paper_info, new_file_path)
                if is_new:
                    added_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                logger.error(f"复制文件失败: {e}")
        else:
            logger.warning(f"未找到匹配的文件: {paper_info['name']}")
            
            # 创建占位文件
            dummy_file = create_dummy_file(paper_info, ".pdf")
            add_paper_to_db(paper_info, dummy_file)
            dummy_count += 1
    
    # 打印统计信息
    logger.info("=" * 50)
    logger.info(f"更新完成！新增试卷: {added_count}, 更新试卷: {updated_count}, 创建占位文件: {dummy_count}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
