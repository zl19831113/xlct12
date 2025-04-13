#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复papers.html页面的分页筛选问题
创建日期: 2025-04-02
"""

import os
import re
import sys

# 服务器上papers.html的路径
PAPERS_HTML_PATH = "/var/www/question_bank/templates/papers.html"
# 本地备份路径
BACKUP_PATH = "/var/www/question_bank/templates/papers.html.bak"

def create_backup(file_path, backup_path):
    """创建备份文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
        return content
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)

def fix_pagination_with_filters(content):
    """修复分页筛选问题"""
    # 1. 修复changePage函数，确保它正确处理筛选条件
    changepage_pattern = r'(function changePage\(direction\) \{.*?currentPage \+= direction;.*?displayPapers\(\);.*?updatePagination\(\);.*?\})'
    
    # 检查是否找到匹配
    match = re.search(changepage_pattern, content, re.DOTALL)
    if not match:
        print("无法找到changePage函数")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 新代码：确保分页时保留筛选条件
    new_code = """function changePage(direction) {
            // 检查当前是否在搜索或筛选模式
            const urlParams = new URLSearchParams(window.location.search);
            const hasFilters = urlParams.has('keyword') || 
                              urlParams.has('region') || 
                              urlParams.has('subject') || 
                              urlParams.has('stage') || 
                              urlParams.has('source_type') || 
                              urlParams.has('year');
            
            // 获取当前页码
            let nextPage = parseInt(urlParams.get('page') || '1') + direction;
            if (nextPage < 1) nextPage = 1;
            
            // 无论是否有筛选条件，都使用navigateWithFilters确保保留筛选参数
            navigateWithFilters(nextPage);
        }"""
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已修复changePage函数")
    
    # 2. 修复goToPage函数，确保它正确处理筛选条件
    gotopage_pattern = r'(function goToPage\(pageNum\) \{.*?window\.location\.href = newUrl;.*?\})'
    
    # 检查是否找到匹配
    match = re.search(gotopage_pattern, content, re.DOTALL)
    if not match:
        print("无法找到goToPage函数")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 新代码：简化并使用navigateWithFilters
    new_code = """function goToPage(pageNum) {
            // 直接使用navigateWithFilters函数确保保留所有筛选条件
            navigateWithFilters(pageNum);
        }"""
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已修复goToPage函数")
    
    # 3. 增强navigateWithFilters函数，确保它收集所有筛选条件
    navigate_pattern = r'(function navigateWithFilters\(pageNum\) \{.*?window\.location\.href = newUrl;.*?\})'
    
    # 检查是否找到匹配
    match = re.search(navigate_pattern, content, re.DOTALL)
    if not match:
        print("无法找到navigateWithFilters函数")
        return content
    
    # 原始代码段
    original_code = match.group(1)
    
    # 新代码：增强版navigateWithFilters
    new_code = """function navigateWithFilters(pageNum) {
            console.log("正在跳转到页面", pageNum, "并保留所有筛选条件");
            
            // 获取当前的URL参数
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('page', pageNum);
            
            // 保留所有可能的筛选参数
            const filtersToKeep = ['region', 'subject', 'stage', 'source', 'source_type', 'year', 'keyword'];
            filtersToKeep.forEach(filter => {
                const value = urlParams.get(filter);
                if (value) {
                    console.log(`保留URL中的筛选参数: ${filter}=${value}`);
                }
            });
            
            // 添加当前选择的筛选条件（可能是通过UI选择但尚未提交的）
            for (const key in selectedFilters) {
                if (selectedFilters[key]) {
                    urlParams.set(key, selectedFilters[key]);
                    console.log(`添加已选择的筛选条件: ${key}=${selectedFilters[key]}`);
                }
            }
            
            // 检查搜索输入框的值
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput.value.trim()) {
                urlParams.set('keyword', searchInput.value.trim());
                console.log(`添加搜索关键词: keyword=${searchInput.value.trim()}`);
            }
            
            // 获取当前激活的筛选标签
            const filterTags = document.querySelectorAll('.filter-tag');
            filterTags.forEach(tag => {
                const filterType = tag.getAttribute('data-type');
                const filterValue = tag.getAttribute('data-value');
                if (filterType && filterValue) {
                    urlParams.set(filterType, filterValue);
                    console.log(`从筛选标签添加: ${filterType}=${filterValue}`);
                }
            });
            
            // 形成新URL并跳转
            const newUrl = `/papers?${urlParams.toString()}`;
            console.log(`跳转到新URL: ${newUrl}`);
            window.location.href = newUrl;
        }"""
    
    # 替换代码
    content = content.replace(original_code, new_code)
    print("已增强navigateWithFilters函数")
    
    return content

def main():
    """主函数"""
    # 检查文件是否存在
    if not os.path.exists(PAPERS_HTML_PATH):
        print(f"错误: 找不到文件 {PAPERS_HTML_PATH}")
        sys.exit(1)
    
    # 创建备份
    content = create_backup(PAPERS_HTML_PATH, BACKUP_PATH)
    
    # 修复分页筛选问题
    content = fix_pagination_with_filters(content)
    
    # 写回文件
    try:
        with open(PAPERS_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复完成，已更新 {PAPERS_HTML_PATH}")
    except Exception as e:
        print(f"写入文件失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
