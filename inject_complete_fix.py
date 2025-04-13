#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将完整的修复脚本注入到HTML文件中
"""

import os
import sys

def inject_script(html_path, script_path):
    """将脚本注入到HTML文件中"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建脚本标签
        script_tag = f'<script>\n// 完整的分页和筛选修复脚本\n{script_content}\n</script>'
        
        # 检查脚本是否已存在
        if script_content[:20] in html_content:
            print(f"修复脚本已存在于{html_path}")
            return html_content
        
        # 在</body>前插入脚本
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{script_tag}\n</body>')
            print(f"已将完整修复脚本注入到{html_path}")
        else:
            # 如果没有</body>标签，则在文件末尾添加
            html_content += f'\n{script_tag}\n'
            print(f"已将完整修复脚本添加到{html_path}末尾")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content
    except Exception as e:
        print(f"注入脚本到{html_path}失败: {e}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 inject_complete_fix.py <html_path> <script_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    script_path = sys.argv[2]
    
    # 检查文件是否存在
    for path in [html_path, script_path]:
        if not os.path.exists(path):
            print(f"错误: 找不到文件 {path}")
            sys.exit(1)
    
    # 创建备份
    backup_path = f"{html_path}.bak_complete"
    try:
        with open(html_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 注入脚本
    inject_script(html_path, script_path)

if __name__ == "__main__":
    main()
