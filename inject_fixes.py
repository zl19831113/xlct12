#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将修复脚本注入到HTML文件中
"""

import os
import sys

def inject_script(html_path, script_path, script_type):
    """将脚本注入到HTML文件中"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建脚本标签
        script_tag = f'<script>\n// {script_type}修复脚本\n{script_content}\n</script>'
        
        # 检查脚本是否已存在
        if script_content[:20] in html_content:
            print(f"{script_type}脚本已存在于{html_path}")
            return html_content
        
        # 在</body>前插入脚本
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{script_tag}\n</body>')
            print(f"已将{script_type}脚本注入到{html_path}")
        else:
            # 如果没有</body>标签，则在文件末尾添加
            html_content += f'\n{script_tag}\n'
            print(f"已将{script_type}脚本添加到{html_path}末尾")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content
    except Exception as e:
        print(f"注入{script_type}脚本到{html_path}失败: {e}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 4:
        print("用法: python3 inject_fixes.py <html_path> <localStorage_script_path> <pagination_script_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    localStorage_script_path = sys.argv[2]
    pagination_script_path = sys.argv[3]
    
    # 检查文件是否存在
    for path in [html_path, localStorage_script_path, pagination_script_path]:
        if not os.path.exists(path):
            print(f"错误: 找不到文件 {path}")
            sys.exit(1)
    
    # 创建备份
    backup_path = f"{html_path}.bak"
    try:
        with open(html_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 确定HTML文件类型
    filename = os.path.basename(html_path)
    if filename == 'client.html':
        # 只注入localStorage修复
        inject_script(html_path, localStorage_script_path, 'localStorage')
    elif filename == 'papers.html':
        # 只注入分页修复
        inject_script(html_path, pagination_script_path, '分页')
    else:
        print(f"未知的HTML文件类型: {filename}")

if __name__ == "__main__":
    main()
