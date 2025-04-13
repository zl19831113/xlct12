import os
import re
from flask import jsonify, send_file

def smart_download(paper, app):
    """智能下载函数，处理各种文件名格式不匹配的情况"""
    try:
        file_path = paper.file_path
        
        # 记录原始信息
        app.logger.info('尝试下载文件: ' + file_path)
        
        # 检查原始路径
        if os.path.isfile(file_path):
            app.logger.info('找到原始文件: ' + file_path)
            return send_file(file_path, as_attachment=True)
        
        # 提取文件名
        file_name = os.path.basename(file_path)
        
        # 尝试在uploads/papers目录中查找
        papers_dir = os.path.join(app.root_path, 'uploads', 'papers')
        alt_path = os.path.join(papers_dir, file_name)
        if os.path.isfile(alt_path):
            app.logger.info('在uploads/papers中找到文件: ' + alt_path)
            return send_file(alt_path, as_attachment=True)
        
        # 尝试处理时间戳格式差异（添加下划线）
        if file_name.startswith('20') and '_' not in file_name[:15]:
            # 修复: 在第8位和第14位添加下划线
            new_name = file_name[:8] + '_' + file_name[8:14] + '_' + file_name[14:]
            new_path = os.path.join(papers_dir, new_name)
            app.logger.info('尝试查找格式化名称: ' + new_path)
            if os.path.isfile(new_path):
                app.logger.info('找到带下划线的文件: ' + new_path)
                return send_file(new_path, as_attachment=True)
        
        # 根据前缀寻找匹配的文件
        if file_name.startswith('20'):
            prefix = file_name[:8]  # 取前8位作为日期前缀 (20250226)
            app.logger.info('使用前缀搜索文件: ' + prefix)
            
            for f in os.listdir(papers_dir):
                if f.startswith(prefix):
                    found_path = os.path.join(papers_dir, f)
                    app.logger.info('找到匹配的文件: ' + found_path)
                    return send_file(found_path, as_attachment=True)
        
        # 最后尝试模糊匹配
        try:
            base_name = os.path.splitext(file_name)[0]  # 不含扩展名
            pattern = base_name.split('-')[0]  # 取'-'前的部分
            pattern = re.sub(r'[_]', '', pattern)  # 移除所有下划线
            
            app.logger.info('使用模糊匹配模式: ' + pattern)
            
            for f in os.listdir(papers_dir):
                # 移除文件名中的下划线进行比较
                f_clean = re.sub(r'[_]', '', f)
                if pattern in f_clean:
                    found_path = os.path.join(papers_dir, f)
                    app.logger.info('找到模糊匹配文件: ' + found_path)
                    return send_file(found_path, as_attachment=True)
        except Exception as e:
            app.logger.error('模糊匹配时出错: ' + str(e))
        
        # 文件未找到
        app.logger.error('未找到文件: ' + file_name)
        return jsonify({'error': '未找到文件 "' + os.path.splitext(file_name)[0] + '"'}), 404
        
    except Exception as e:
        app.logger.error('下载文件时出错: ' + str(e))
        return jsonify({'error': '下载失败: ' + str(e)}), 500 