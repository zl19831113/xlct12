#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复app.py中的download_paper函数
创建时间: 2025-03-29
"""

import os
import re
import sys
import shutil
from datetime import datetime
import time

# 颜色输出
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'  # 无颜色

def print_color(message, color=None):
    """打印彩色文本"""
    if color:
        print(f"{color}{message}{NC}")
    else:
        print(message)

def get_fixed_function():
    """返回修复后的函数代码"""
    # 注意：确保开头的缩进是正确的
    function_code = '''
@app.route('/download_paper/<int:paper_id>')
def download_paper(paper_id):
    try:
        # 获取试卷信息
        paper = Paper.query.get_or_404(paper_id)
        original_file_path = paper.file_path
        file_name = os.path.basename(original_file_path) if original_file_path else ""
        
        print(f"尝试下载试卷: ID={paper_id}, 名称='{paper.name}', 路径='{original_file_path}'")
        
        # 获取项目根目录
        project_root = os.path.dirname(os.path.abspath(__file__))
        upload_folder = app.config.get('UPLOAD_FOLDER') or os.path.join(project_root, 'uploads', 'papers')
        tmp_file_path = os.path.join(project_root, 'static', 'tmp_paper.txt')
        
        # 1. 直接从uploads目录根部查找 - 这是我们放置文件的地方
        direct_upload_path = os.path.join(project_root, 'uploads', file_name)
        if file_name and os.path.exists(direct_upload_path) and os.path.isfile(direct_upload_path):
            print(f"✓ 在uploads根目录找到文件: {direct_upload_path}")
            _, file_ext = os.path.splitext(direct_upload_path)
            download_filename = f"{paper.name}{file_ext}"
            
            # 更新数据库中的路径，方便未来查找
            rel_path = os.path.relpath(direct_upload_path, project_root)
            try:
                paper.file_path = rel_path
                db.session.commit()
                print(f"已更新数据库路径: {rel_path}")
            except Exception as e:
                print(f"更新数据库路径失败: {e}")
                
            return send_file(
                direct_upload_path,
                as_attachment=True,
                download_name=download_filename
            )
        
        # 2. 深度搜索uploads目录
        uploads_root = os.path.join(project_root, 'uploads')
        if os.path.exists(uploads_root) and os.path.isdir(uploads_root) and file_name:
            print("尝试在uploads目录中深度搜索文件...")
            
            # 先尝试精确匹配
            for root, _, files in os.walk(uploads_root):
                if file_name in files:
                    exact_path = os.path.join(root, file_name)
                    print(f"✓ 在深度搜索中找到精确匹配: {exact_path}")
                    
                    # 更新数据库
                    rel_path = os.path.relpath(exact_path, project_root)
                    try:
                        paper.file_path = rel_path
                        db.session.commit()
                        print(f"已更新数据库路径: {rel_path}")
                    except Exception as e:
                        print(f"更新数据库路径失败: {e}")
                    
                    # 返回文件
                    _, file_ext = os.path.splitext(exact_path)
                    download_filename = f"{paper.name}{file_ext}"
                    return send_file(
                        exact_path,
                        as_attachment=True,
                        download_name=download_filename
                    )
            
            # 如果精确匹配失败，尝试部分匹配
            base_name = os.path.splitext(file_name)[0]
            if base_name:
                # 移除前缀数字和下划线，提高匹配率
                clean_base = re.sub(r'^\d+_\d+_\d+_', '', base_name)
                
                if clean_base and len(clean_base) > 3:  # 确保有足够的文本进行匹配
                    for root, _, files in os.walk(uploads_root):
                        for found_file in files:
                            if clean_base.lower() in found_file.lower():
                                partial_path = os.path.join(root, found_file)
                                print(f"✓ 在深度搜索中找到部分匹配: {partial_path}")
                                
                                # 更新数据库
                                rel_path = os.path.relpath(partial_path, project_root)
                                try:
                                    paper.file_path = rel_path
                                    db.session.commit()
                                    print(f"已更新数据库路径: {rel_path}")
                                except Exception as e:
                                    print(f"更新数据库路径失败: {e}")
                                
                                # 返回文件
                                _, file_ext = os.path.splitext(partial_path)
                                download_filename = f"{paper.name}{file_ext}"
                                return send_file(
                                    partial_path,
                                    as_attachment=True,
                                    download_name=download_filename
                                )
        
        # 如果所有尝试都失败，创建占位符文件
        print(f"❗ 所有尝试都失败，使用占位符文件")
        
        # 确保tmp目录存在
        os.makedirs(os.path.dirname(tmp_file_path), exist_ok=True)
        
        # 创建一个简单的文本文件
        with open(tmp_file_path, 'w', encoding='utf-8') as f:
            f.write(f"试卷: {paper.name}\\n")
            f.write(f"地区: {paper.region}\\n")
            f.write(f"科目: {paper.subject}\\n")
            f.write(f"学段: {paper.stage}\\n")
            f.write(f"来源: {paper.source}\\n")
            f.write(f"年份: {paper.year}\\n")
            f.write("\\n注意: 无法找到此试卷文件。请联系管理员。")
        
        # 确定合适的扩展名
        _, original_ext = os.path.splitext(original_file_path) if original_file_path else ('.txt',)
        if not original_ext:
            original_ext = '.txt'
            
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"{paper.name}{original_ext}"
        )
        
    except Exception as e:
        print(f"下载试卷时出错: {e}")
        return jsonify({"error": "下载试卷时出错，请稍后再试或联系管理员", "details": str(e)}), 500
'''
    return function_code.strip()

def fix_app_code():
    """修复app.py中的代码"""
    # 获取项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_dir, 'app.py')
    
    # 检查文件是否存在
    if not os.path.exists(app_path):
        print_color(f"错误: app.py文件不存在: {app_path}", RED)
        return False
    
    # 备份app.py
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    backup_path = f"{app_path}.bak.{timestamp}"
    shutil.copy2(app_path, backup_path)
    print_color(f"已创建备份: {backup_path}", BLUE)
    
    # 读取app.py内容
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定位并替换download_paper函数
    pattern = r'@app\.route\([\'"]/download_paper/.*?def\s+download_paper\([^)]*\):.*?(?=@app\.route|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print_color("错误: 无法在app.py中找到download_paper函数", RED)
        return False
    
    # 获取新函数代码
    new_function = get_fixed_function()
    
    # 替换函数
    updated_content = content.replace(match.group(0), new_function)
    
    # 确保没有模块导入缺失
    if 're' not in content and 'import re' not in updated_content:
        # 查找最后一个import语句
        import_match = re.search(r'^import.*?$|^from.*?import.*?$', updated_content, re.MULTILINE)
        if import_match:
            last_import = import_match.group(0)
            updated_content = updated_content.replace(last_import, f"{last_import}\nimport re")
        else:
            # 在文件开头添加
            updated_content = f"import re\n{updated_content}"
    
    # 写回文件
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print_color("✓ app.py修复成功!", GREEN)
    return True

def main():
    """主函数"""
    print_color("=" * 80, GREEN)
    print_color(" 修复app.py中的download_paper函数 ", BOLD + GREEN)
    print_color("=" * 80, GREEN)
    
    start_time = time.time()
    success = fix_app_code()
    end_time = time.time()
    
    print_color(f"修复耗时: {end_time - start_time:.2f}秒", BLUE)
    
    if success:
        print_color("修复完成! 现在您可以测试下载功能了。", BOLD + GREEN)
        print_color("请使用以下命令启动应用:", YELLOW)
        print_color("  python3 app.py", BLUE)
    else:
        print_color("修复失败，请手动检查app.py文件。", RED)
    
    print_color("=" * 80, GREEN)

if __name__ == "__main__":
    main()
