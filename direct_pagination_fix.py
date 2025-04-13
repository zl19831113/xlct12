#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接修改papers.html中的分页链接，使用JavaScript函数而不是直接URL
"""

import os
import re
import sys

def fix_pagination_links(html_path):
    """直接修改分页链接"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建备份
        backup_path = f"{html_path}.bak_direct"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已创建备份: {backup_path}")
        
        # 查找并替换上一页链接
        prev_link_pattern = r'<a href="\{\{ url_for\(\'papers_list\', page=page-1, .*?\) \}\}" class="pagination-button">上一页</a>'
        new_prev_link = '<a href="javascript:void(0)" onclick="navigateWithAllFilters({{ page-1 }})" class="pagination-button" data-page="{{ page-1 }}">上一页</a>'
        
        html_content = re.sub(prev_link_pattern, new_prev_link, html_content)
        print("已替换上一页链接")
        
        # 查找并替换下一页链接
        next_link_pattern = r'<a href="\{\{ url_for\(\'papers_list\', page=page\+1, .*?\) \}\}" class="pagination-button">下一页</a>'
        new_next_link = '<a href="javascript:void(0)" onclick="navigateWithAllFilters({{ page+1 }})" class="pagination-button" data-page="{{ page+1 }}">下一页</a>'
        
        html_content = re.sub(next_link_pattern, new_next_link, html_content)
        print("已替换下一页链接")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已成功修改分页链接: {html_path}")
        return True
    except Exception as e:
        print(f"修改分页链接失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 direct_pagination_fix.py <html_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(html_path):
        print(f"错误: 找不到文件 {html_path}")
        sys.exit(1)
    
    # 修复分页链接
    if fix_pagination_links(html_path):
        print("分页链接修复成功")
    else:
        print("分页链接修复失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
