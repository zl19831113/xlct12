#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复papers.html中的筛选按钮点击事件
"""

import os
import sys

def fix_filter_buttons(html_path):
    """修复筛选按钮点击事件"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 创建备份
        backup_path = f"{html_path}.bak_buttons"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已创建备份: {backup_path}")
        
        # 检查是否存在showFilter函数
        if "function showFilter(" not in html_content:
            print("错误: 找不到showFilter函数")
            return False
        
        # 查找筛选按钮定义部分
        filter_buttons_section = """    <div class="filter-buttons">
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="region">地区</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="subject">科目</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="stage">学段</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="source_type">来源类型</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="source">来源</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="year">年份</button>
        </div>
    </div>"""
        
        # 新的筛选按钮定义，添加onclick属性
        new_filter_buttons_section = """    <div class="filter-buttons">
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="region" onclick="showFilter('region')">地区</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="subject" onclick="showFilter('subject')">科目</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="stage" onclick="showFilter('stage')">学段</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="source_type" onclick="showFilter('source_type')">来源类型</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="source" onclick="showFilter('source')">来源</button>
        </div>
        <div class="filter-btn-container">
            <button class="filter-btn" data-filter-type="year" onclick="showFilter('year')">年份</button>
        </div>
    </div>"""
        
        # 替换筛选按钮定义
        if filter_buttons_section in html_content:
            html_content = html_content.replace(filter_buttons_section, new_filter_buttons_section)
            print("已替换筛选按钮定义")
        else:
            print("警告: 找不到筛选按钮定义部分，尝试使用正则表达式")
            import re
            pattern = r'<div class="filter-buttons">.*?</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>'
            html_content = re.sub(pattern, new_filter_buttons_section, html_content, flags=re.DOTALL)
            print("已使用正则表达式替换筛选按钮定义")
        
        # 移除可能导致冲突的事件绑定代码
        event_binding_code = """            // 初始化筛选按钮点击事件 - 直接在HTML元素上绑定点击事件
            document.querySelectorAll('.filter-btn[data-filter-type]').forEach(btn => {
                const filterType = btn.getAttribute('data-filter-type');
                btn.onclick = function() {
                    showFilter(filterType);
                };
            });"""
        
        if event_binding_code in html_content:
            html_content = html_content.replace(event_binding_code, "            // 筛选按钮点击事件已直接在HTML元素上绑定")
            print("已移除冲突的事件绑定代码")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"已成功修复筛选按钮: {html_path}")
        return True
    except Exception as e:
        print(f"修复筛选按钮失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 fix_filter_buttons.py <html_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(html_path):
        print(f"错误: 找不到文件 {html_path}")
        sys.exit(1)
    
    # 修复筛选按钮
    if fix_filter_buttons(html_path):
        print("筛选按钮修复成功")
    else:
        print("筛选按钮修复失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
