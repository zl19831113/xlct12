@app.route('/simple/<int:paper_id>')
def download_simple(paper_id):
    try:
        paper = Paper.query.filter_by(id=paper_id).first()
        if not paper:
            return jsonify({"error": "Paper not found"}), 404
        
        papers_dir = os.path.join(app.root_path, "uploads", "papers")
        file_name = os.path.basename(paper.file_path)
        
        # 检查是否需要添加下划线
        if file_name.startswith("20") and "_" not in file_name[:15]:
            new_name = file_name[:8] + "_" + file_name[8:14] + "_" + file_name[14:]
            new_path = os.path.join(papers_dir, new_name)
            if os.path.isfile(new_path):
                return send_file(new_path, as_attachment=True)
        
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 