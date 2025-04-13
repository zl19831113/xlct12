#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复papers.html中的筛选功能，确保选择筛选条件后能正确导航到筛选结果页面
"""

import os
import re
import sys

def fix_filter_function(html_path):
    """修复筛选功能"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建备份
        backup_path = f"{html_path}.bak_filter"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已创建备份: {backup_path}")
        
        # 查找并替换applyFilters函数
        apply_filters_pattern = r'function applyFilters\(\) \{[\s\S]*?fetchFilteredPapers\(\);[\s\S]*?\}'
        
        # 新的applyFilters函数 - 直接使用服务器端筛选
        new_apply_filters = '''function applyFilters() {
            // 构建带有筛选条件的URL
            const urlParams = new URLSearchParams();
            urlParams.set('page', '1'); // 重置到第一页
            
            // 添加所有非空筛选条件
            for (const key in selectedFilters) {
                if (selectedFilters[key]) {
                    urlParams.set(key, selectedFilters[key]);
                }
            }
            
            // 跳转到筛选后的URL
            window.location.href = `/papers?${urlParams.toString()}`;
        }'''
        
        # 替换函数
        html_content = re.sub(apply_filters_pattern, new_apply_filters, html_content)
        print("已替换applyFilters函数")
        
        # 修复筛选选项点击事件
        filter_option_pattern = r'label\.addEventListener\(\'click\', function\(\) \{[\s\S]*?closeFilter\(\);[\s\S]*?updateFilterTags\(\);[\s\S]*?\}\);'
        
        # 新的筛选选项点击事件
        new_filter_option = '''label.addEventListener('click', function() {
                    // 如果重复点击同一选项，则取消选择
                    if (selectedFilters[filterType] === option) {
                        selectedFilters[filterType] = null;
                    } else {
                        selectedFilters[filterType] = option;
                    }
                    
                    // 关闭模态框
                    closeFilter();
                    
                    // 直接应用筛选
                    applyFilters();
                });'''
        
        # 替换筛选选项点击事件
        html_content = re.sub(filter_option_pattern, new_filter_option, html_content)
        print("已替换筛选选项点击事件")
        
        # 修复搜索功能
        search_function_pattern = r'function performSearch\(\) \{[\s\S]*?window\.location\.href = `/papers\?\$\{urlParams\.toString\(\)\}`;[\s\S]*?\}'
        
        # 新的搜索函数
        new_search_function = '''function performSearch() {
            const keyword = document.getElementById('searchInput').value.trim();
            
            if (!keyword) {
                alert('请输入搜索关键词');
                return;
            }
            
            // 更新selectedFilters
            selectedFilters.keyword = keyword;
            
            // 应用筛选
            applyFilters();
        }'''
        
        # 替换搜索函数
        html_content = re.sub(search_function_pattern, new_search_function, html_content)
        print("已替换搜索函数")
        
        # 添加navigateWithAllFilters函数
        if 'function navigateWithAllFilters(' not in html_content:
            navigate_function = '''
        // 带有所有筛选条件的页面导航函数
        function navigateWithAllFilters(pageNum) {
            // 构建URL参数
            const urlParams = new URLSearchParams(window.location.search);
            
            // 更新页码
            urlParams.set('page', pageNum);
            
            // 跳转到新页面
            window.location.href = `/papers?${urlParams.toString()}`;
        }
        '''
            
            # 在</script>标签前插入
            html_content = html_content.replace('</script>\n</body>', navigate_function + '\n</script>\n</body>')
            print("已添加navigateWithAllFilters函数")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已成功修复筛选功能: {html_path}")
        return True
    except Exception as e:
        print(f"修复筛选功能失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 fix_filter_navigation.py <html_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(html_path):
        print(f"错误: 找不到文件 {html_path}")
        sys.exit(1)
    
    # 修复筛选功能
    if fix_filter_function(html_path):
        print("筛选功能修复成功")
    else:
        print("筛选功能修复失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
