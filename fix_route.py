@app.route('/fix/<int:paper_id>')
def download_fix(paper_id):
    try:
        # 获取paper
        paper = Paper.query.filter_by(id=paper_id).first()
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
            
        # 提取文件名
        file_name = os.path.basename(paper.file_path)
        app.logger.info('尝试下载文件: ' + file_name + ', 路径: ' + paper.file_path)
        
        # 检查原始路径
        file_path = paper.file_path
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True)
        
        # 尝试在uploads/papers目录中查找
        papers_dir = os.path.join(app.root_path, 'uploads', 'papers')
        alt_path = os.path.join(papers_dir, file_name)
        if os.path.isfile(alt_path):
            app.logger.info('在uploads/papers中找到文件: ' + alt_path)
            return send_file(alt_path, as_attachment=True)
            
        # 尝试处理时间戳格式差异（例如添加下划线）
        if file_name.startswith('20') and '_' not in file_name[:15]:
            # 在第8和第14位置添加下划线
            new_name = file_name[:8] + '_' + file_name[8:14] + '_' + file_name[14:]
            new_path = os.path.join(papers_dir, new_name)
            if os.path.isfile(new_path):
                app.logger.info('找到带下划线的文件: ' + new_path)
                return send_file(new_path, as_attachment=True)
                
        # 尝试找到所有匹配的文件
        prefix = file_name.split('.')[0][:8]  # 提取前8位作为前缀
        app.logger.info('搜索前缀: ' + prefix + ' 的文件')
        
        for f in os.listdir(papers_dir):
            if f.startswith(prefix):
                found_path = os.path.join(papers_dir, f)
                app.logger.info('找到匹配的文件: ' + found_path)
                return send_file(found_path, as_attachment=True)
                
        # 如果以上都失败，返回404
        app.logger.error('未找到文件: ' + file_name)
        return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        app.logger.error('下载文件时出错: ' + str(e))
        return jsonify({'error': str(e)}), 500 