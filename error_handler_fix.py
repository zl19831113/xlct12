#!/usr/bin/env python3
# 向应用添加全局错误处理
import sys

app_py_path = "app.py"

# 要添加的错误处理代码
error_handler_code = '''
# 全局错误处理
@app.errorhandler(500)
def internal_server_error(e):
    """处理500错误，记录详细日志并显示友好的错误页面"""
    error_traceback = traceback.format_exc()
    print(f"============= 500服务器错误 =============")
    print(f"时间: {datetime.now().isoformat()}")
    print(f"错误: {str(e)}")
    print(f"详细信息: {error_traceback}")
    print(f"请求路径: {request.path}")
    print(f"用户代理: {request.user_agent}")
    print(f"============= 错误结束 =============")
    
    # 对于音频播放相关的错误，返回特定的错误页面
    if '/audio_player/' in request.path or '/get_audio_by_paper/' in request.path:
        return render_template('audio_error.html', 
                               error="服务器遇到内部错误，无法完成请求。",
                               paper_id=request.path.split('/')[-1] if len(request.path.split('/')) > 2 else "未知",
                               traceback_info=f"{str(e)}")
    
    # 一般错误页面
    return render_template('error.html', error="服务器遇到内部错误，无法完成请求。"), 500

# 自定义404处理
@app.errorhandler(404)
def page_not_found(e):
    """处理404错误，显示友好的页面"""
    print(f"404错误: 找不到路径 {request.path}")
    return render_template('error.html', error="请求的页面不存在。"), 404
'''

try:
    # 读取现有app.py文件
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经添加了错误处理
    if '@app.errorhandler(500)' in content:
        print("错误处理代码已存在，无需修改")
        sys.exit(0)
    
    # 查找合适的插入点 - 在if __name__ == '__main__'之前
    if 'if __name__ == \'__main__\'' in content:
        # 在main前插入
        position = content.find('if __name__ == \'__main__\'')
        new_content = content[:position] + error_handler_code + '\n\n' + content[position:]
    else:
        # 如果找不到main，就添加到文件末尾
        new_content = content + '\n\n' + error_handler_code
    
    # 写回文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("成功添加错误处理代码")
except Exception as e:
    print(f"修改文件时出错: {str(e)}")
    sys.exit(1)
