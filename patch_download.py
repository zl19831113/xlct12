@app.route('/download_paper/<int:paper_id>')
def download_paper(paper_id):
    try:
        # 获取paper
        paper = Paper.query.get_or_404(paper_id)
        
        # 导入智能下载模块
        import smart_download
        return smart_download.smart_download(paper, app)
        
    except Exception as e:
        app.logger.error('下载文件时出错: ' + str(e))
        return jsonify({'error': '下载失败: ' + str(e)}), 500 