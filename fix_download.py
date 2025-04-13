#!/usr/bin/env python3
import re

# 新的下载函数代码
new_function = '''@app.route('/download_paper/<int:paper_id>')
def download_paper(paper_id):
    try:
        # 获取试卷信息
        paper = Paper.query.get_or_404(paper_id)
        file_path = paper.file_path
        
        # 提取文件名
        file_name = os.path.basename(file_path)
        
        # 可能的文件路径列表
        possible_paths = [
            # 原始路径
            file_path,
            # 当前项目根目录下的uploads/papers路径
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads/papers', file_name),
            # 尝试直接从项目根目录查找
            os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path),
        ]
        
        # 移除None项
        possible_paths = [p for p in possible_paths if p]
        
        # 记录尝试的路径
        print(f"尝试查找文件: {file_name}")
        for i, path in enumerate(possible_paths):
            print(f"路径{i+1}: {path}")
            if os.path.exists(path):
                print(f"文件找到于: {path}")
                return send_file(
                    path,
                    as_attachment=True,
                    download_name=paper.name + os.path.splitext(path)[1]
                )
        
        # 如果使用旧的文件命名格式但实际文件使用新格式，提取日期部分
        date_prefix = None
        if file_name.startswith('20'):
            date_prefix = file_name.split('_')[0] if '_' in file_name else file_name[:8]
            print(f"尝试使用日期前缀查找: {date_prefix}")
            
            # 在uploads/papers目录中查找所有以该日期开头的文件
            papers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads/papers')
            if os.path.exists(papers_dir):
                matches = []
                for f in os.listdir(papers_dir):
                    if f.startswith(date_prefix):
                        matches.append(os.path.join(papers_dir, f))
                
                if matches:
                    print(f"找到{len(matches)}个匹配文件")
                    # 使用第一个匹配文件
                    print(f"使用匹配文件: {matches[0]}")
                    return send_file(
                        matches[0],
                        as_attachment=True,
                        download_name=paper.name + os.path.splitext(matches[0])[1]
                    )
        
        # 如果文件名中包含特殊格式，尝试清理文件名后再次查找
        pattern = '_[0-9]+_'
        if re.search(pattern, file_name):
            print(f"尝试模糊匹配文件名: {file_name}")
            
            # 清理文件名中的序号部分，构建正则表达式
            parts = re.split(pattern, file_name, 1)
            if len(parts) == 2:
                prefix, suffix = parts
                file_pattern = f"{prefix}_\\d+_{suffix}"
                papers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads/papers')
                
                if os.path.exists(papers_dir):
                    print(f"在目录中搜索: {papers_dir}")
                    for f in os.listdir(papers_dir):
                        if re.match(file_pattern, f):
                            found_path = os.path.join(papers_dir, f)
                            print(f"模糊匹配找到文件: {found_path}")
                            return send_file(
                                found_path,
                                as_attachment=True,
                                download_name=paper.name + os.path.splitext(found_path)[1]
                            )
        
        # 如果所有尝试都失败，在整个上传目录中递归搜索
        print("尝试在整个上传目录中递归搜索...")
        upload_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        for root, dirs, files in os.walk(upload_root):
            for f in files:
                # 检查精确匹配
                if f == file_name:
                    found_path = os.path.join(root, f)
                    print(f"递归搜索找到精确匹配: {found_path}")
                    return send_file(
                        found_path,
                        as_attachment=True,
                        download_name=paper.name + os.path.splitext(found_path)[1]
                    )
                # 检查日期前缀匹配
                elif date_prefix and f.startswith(date_prefix):
                    found_path = os.path.join(root, f)
                    print(f"递归搜索找到日期前缀匹配: {found_path}")
                    return send_file(
                        found_path,
                        as_attachment=True,
                        download_name=paper.name + os.path.splitext(found_path)[1]
                    )
        
        # 如果所有尝试都失败，返回友好的错误页面
        print(f"错误：无法找到文件 {file_name} - 尝试路径: {', '.join(possible_paths)}")
        error_message = f"很抱歉，文件 '{paper.name}' 暂时无法下载。我们已记录此问题，请稍后再试或联系管理员。"
        
        return render_template('error.html', error=error_message, paper=paper), 404
    except Exception as e:
        print(f"下载文件时出错: {str(e)}")
        traceback.print_exc()
        error_message = "下载过程中发生错误，请稍后再试或联系管理员。"
        return render_template('error.html', error=error_message), 500'''

# 这段代码会在服务器上执行，修改app.py文件
server_code = f'''
import re

# 读取app.py文件
with open('app.py', 'r') as f:
    content = f.read()

# 替换download_paper函数
pattern = r'@app\\.route\\(\\\'/download_paper/<int:paper_id>\\\\'\\)[^@]*?def download_paper\\(paper_id\\):.*?(?=@app\\.route|$)'
replacement = """{new_function}\\n\\n"""
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回文件
with open('app.py', 'w') as f:
    f.write(new_content)

print('修改完成')
'''

with open('server_fix.py', 'w') as f:
    f.write(server_code)

print("修复脚本已创建，请将server_fix.py上传到服务器并执行。") 