#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全重置服务器应用程序 - 彻底解决SQLAlchemy兼容性问题
"""

import paramiko
import sys
import time
from datetime import datetime

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
APP_PATH = "/var/www/question_bank/app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def fix_server_app():
    """完全重置并修复服务器应用"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 1. 创建一个简单但完整的应用程序
        simple_app = '''
import os
import re
import time
import traceback
import json
from io import BytesIO
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case, text

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/xlct12.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    stage = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.String(20), default='地区联考')
    year = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    upload_time = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region,
            'subject': self.subject,
            'stage': self.stage,
            'source': self.source,
            'source_type': self.source_type,
            'year': self.year,
            'file_path': self.file_path
        }

class SU(db.Model):
    __tablename__ = 'su'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    unit = db.Column(db.String(50))
    lesson = db.Column(db.String(50))
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    question_type = db.Column(db.String(20))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/papers')
def papers_list():
    try:
        # 获取筛选参数
        region = request.args.get('region')
        subject = request.args.get('subject')
        stage = request.args.get('stage')
        source_type = request.args.get('source_type')
        source = request.args.get('source')
        year = request.args.get('year')
        keyword = request.args.get('keyword')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        papers_query = Paper.query
        
        # 添加筛选条件
        if region:
            papers_query = papers_query.filter(Paper.region == region)
        if subject:
            papers_query = papers_query.filter(Paper.subject == subject)
        if stage:
            papers_query = papers_query.filter(Paper.stage == stage)
        if source_type:
            papers_query = papers_query.filter(Paper.source_type == source_type)
        if source:
            papers_query = papers_query.filter(Paper.source == source)
        if year:
            try:
                if isinstance(year, str) and year.isdigit():
                    papers_query = papers_query.filter(Paper.year == int(year))
                elif isinstance(year, (int, float)):
                    papers_query = papers_query.filter(Paper.year == int(year))
            except (ValueError, TypeError) as e:
                print(f"年份转换错误: {e}")
        if keyword:
            papers_query = papers_query.filter(Paper.name.like(f'%{keyword}%'))
        
        try:
            # 排序规则：年份降序 > 湖北地区优先 > 下学期优先于上学期 > 3月优先于2月优先于1月 > 上传时间降序
            sorted_query = papers_query.order_by(
                Paper.year.desc(),
                # 湖北地区优先
                case((Paper.region == "湖北", 1), else_=0).desc(),
                # 下学期优先于上学期
                case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),
                # 3月优先于2月优先于1月
                case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),
                # 最后按上传时间降序排序(最新上传的优先)
                Paper.upload_time.desc()
            )
            
            # 获取总试卷数
            total_papers = sorted_query.count()
            
            # 实现分页
            paginated_papers = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
            papers = paginated_papers.items
            
        except Exception as query_error:
            print(f"排序查询失败: {str(query_error)}")
            traceback.print_exc()
            # 使用简单查询作为备选
            sorted_query = papers_query.order_by(Paper.year.desc())
            total_papers = sorted_query.count()
            paginated_papers = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
            papers = paginated_papers.items
        
        try:
            # 获取所有地区、学科、学段、来源类型和来源
            regions = db.session.query(Paper.region).distinct().all()
            subjects = db.session.query(Paper.subject).distinct().all()
            stages = db.session.query(Paper.stage).distinct().all()
            source_types = db.session.query(Paper.source_type).distinct().all()
            sources = db.session.query(Paper.source).distinct().all()
        except Exception as filter_error:
            print(f"获取筛选选项失败: {str(filter_error)}")
            traceback.print_exc()
            # 提供空列表作为备选
            regions = []
            subjects = []
            stages = []
            source_types = []
            sources = []
        
        # 准备渲染模板
        return render_template('papers.html', 
                             papers=papers, 
                             regions=regions, 
                             subjects=subjects, 
                             stages=stages, 
                             source_types=source_types, 
                             sources=sources, 
                             active_page='papers',
                             pagination=paginated_papers,
                             per_page=per_page,
                             page=page,
                             total=total_papers,
                             # 传递当前的筛选参数到模板
                             current_filters={
                                 'region': region,
                                 'subject': subject,
                                 'stage': stage,
                                 'source_type': source_type,
                                 'source': source,
                                 'year': year,
                                 'keyword': keyword
                             })
    except Exception as e:
        print(f"获取试卷列表失败: {str(e)}")
        traceback.print_exc()
        return render_template('papers.html', papers=[], error=str(e))

@app.route('/filter_papers', methods=['GET', 'POST'])
def filter_papers():
    try:
        if request.method == 'POST':
            # 从POST请求JSON中获取筛选参数
            filter_data = request.get_json()
            region = filter_data.get('region')
            subject = filter_data.get('subject')
            stage = filter_data.get('stage')
            source_type = filter_data.get('source_type')
            source = filter_data.get('source')
            year = filter_data.get('year')
            keyword = filter_data.get('keyword')
            page = filter_data.get('page', 1)
            per_page = filter_data.get('per_page', 20)
        else:  # GET请求
            # 从URL参数获取筛选条件
            region = request.args.get('region')
            subject = request.args.get('subject')
            stage = request.args.get('stage')
            source_type = request.args.get('source_type')
            source = request.args.get('source')
            year = request.args.get('year')
            keyword = request.args.get('keyword')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = Paper.query
        
        # 添加筛选条件
        if region:
            query = query.filter(Paper.region == region)
        if subject:
            query = query.filter(Paper.subject == subject)
        if stage:
            query = query.filter(Paper.stage == stage)
        if source_type:
            query = query.filter(Paper.source_type == source_type)
        if source:
            query = query.filter(Paper.source == source)
        if year:
            try:
                if isinstance(year, str) and year.isdigit():
                    query = query.filter(Paper.year == int(year))
                elif isinstance(year, (int, float)):
                    query = query.filter(Paper.year == int(year))
            except (ValueError, TypeError) as e:
                print(f"年份转换错误: {e}")
        if keyword:
            query = query.filter(Paper.name.like(f'%{keyword}%'))
            
        # 排序逻辑
        sorted_query = query.order_by(
            Paper.year.desc(),
            case((Paper.region == "湖北", 1), else_=0).desc(),
            case(
                (Paper.name.like("%下学期%"), 2),
                (Paper.name.like("%上学期%"), 1),
                else_=0
            ).desc(),
            case(
                (Paper.name.like("%3月%"), 3),
                (Paper.name.like("%2月%"), 2),
                (Paper.name.like("%1月%"), 1),
                else_=0
            ).desc(),
            Paper.upload_time.desc()
        )
        
        # 计算总数
        total = sorted_query.count()
        
        # 分页
        paginated = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
        papers = paginated.items
        
        # 构建试卷数据
        papers_data = []
        for paper in papers:
            try:
                if hasattr(paper, 'to_dict'):
                    papers_data.append(paper.to_dict())
                else:
                    # 手动构建字典
                    papers_data.append({
                        'id': paper.id,
                        'name': paper.name,
                        'region': paper.region,
                        'subject': paper.subject,
                        'stage': paper.stage,
                        'source_type': paper.source_type,
                        'source': paper.source,
                        'year': paper.year
                    })
            except Exception as paper_error:
                print(f"处理试卷数据时出错: {paper_error}")
        
        return jsonify(papers_data)
    except Exception as e:
        print(f"筛选试卷出错: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/search')
def search():
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return render_template('search_results.html', 
                                  results=[], 
                                  query='', 
                                  count=0, 
                                  active_page='search')
        
        # 优化搜索性能：使用更精确的查询条件，避免过度使用通配符
        # 如果查询词很短，使用前缀匹配而不是全文匹配
        if len(query) <= 3:
            # 短查询使用前缀匹配
            questions = SU.query.filter(
                (SU.question.like(f'{query}%')) | 
                (SU.subject == query) |
                (SU.lesson == query)
            ).limit(50).all()
        else:
            # 较长查询使用包含匹配，但避免在所有字段上都使用
            questions = SU.query.filter(
                (SU.question.like(f'%{query}%')) | 
                (SU.answer.like(f'%{query}%')) |
                (SU.subject.like(f'%{query}%')) |
                (SU.lesson.like(f'%{query}%')) |
                (SU.unit.like(f'%{query}%'))
            ).limit(30).all()  # 减少结果数量以提高性能
        
        # 格式化结果
        results = []
        for q in questions:
            try:
                # 确保所有值都是基本类型且有效，避免序列化错误
                # 提取题目的前100个字符作为预览，确保无空值
                question_text = str(q.question or '')
                preview = question_text[:100] + '...' if len(question_text) > 100 else question_text
                
                # 将所有字段强制转换为基本类型，确保可序列化
                result_item = {
                    'id': int(q.id) if q.id is not None else 0,
                    'subject': str(q.subject or ''),
                    'unit': str(q.unit or ''),
                    'lesson': str(q.lesson or ''),
                    'preview': preview,  # 保留预览字段以兼容当前逻辑
                    'question': str(q.question or ''),  # 返回完整题目
                    'question_type': str(q.question_type or '')
                }
                
                # 确保没有undefined或特殊类型的字段
                for key, value in list(result_item.items()):
                    if value is None or type(value).__name__ not in ['str', 'int', 'float', 'bool', 'list', 'dict']:
                        result_item[key] = ''
                        
                results.append(result_item)
            except Exception as item_error:
                print(f"处理搜索结果项时出错: {str(item_error)}")
                # 跳过有问题的项，继续处理其他结果
        
        return render_template('search_results.html', 
                              results=results, 
                              query=query, 
                              count=len(results),
                              active_page='search')
                              
    except Exception as e:
        # 记录错误并返回友好的错误页面
        print(f"搜索时出错: {str(e)}")
        traceback.print_exc()
        return render_template('search_results.html',
                             results=[], 
                             query=query if 'query' in locals() else '', 
                             count=0,
                             error="搜索时出现错误，请稍后再试或修改搜索词。",
                             active_page='search')

@app.route('/download/<int:paper_id>')
def download_paper(paper_id):
    try:
        # 查找试卷
        paper = Paper.query.get_or_404(paper_id)
        
        # 获取文件路径
        file_path = paper.file_path
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            # 尝试查找替代路径
            base_name = os.path.basename(file_path)
            alt_path = os.path.join('/var/www/question_bank/papers', base_name)
            
            if os.path.exists(alt_path):
                file_path = alt_path
            else:
                # 尝试使用下划线替换连字符
                base_name_alt = base_name.replace('-', '_')
                alt_path = os.path.join('/var/www/question_bank/papers', base_name_alt)
                
                if os.path.exists(alt_path):
                    file_path = alt_path
                else:
                    return "文件不存在", 404
        
        # 获取文件名
        filename = os.path.basename(file_path)
        
        # 发送文件
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"下载试卷出错: {str(e)}")
        traceback.print_exc()
        return f"下载失败: {str(e)}", 500

@app.route('/logo.png')
def serve_logo():
    return send_file('logo.png')

@app.route('/fix_pagination.js')
def serve_fix_pagination_js():
    try:
        # 更改缓存控制标头，防止浏览器缓存旧版本
        response = send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'fix_pagination.js')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"提供修复脚本时出错: {str(e)}")
        # 如果文件找不到，提供一个内联的基本修复脚本
        js_content = """
        // 基本分页修复脚本
        document.addEventListener('DOMContentLoaded', function() {
            console.log("运行应急修复脚本");
            // 防止空元素错误
            ['paginationControls', 'prevPage', 'nextPage', 'pageInfo'].forEach(id => {
                if (!document.getElementById(id)) {
                    console.log('创建缺失元素:' + id);
                    const el = document.createElement('div');
                    el.id = id;
                    el.style.display = 'none';
                    document.body.appendChild(el);
                }
            });
        });
        """
        response = app.response_class(response=js_content, status=200, mimetype='application/javascript')
        return response

# 初始化数据库
def init_db():
    db.create_all()
    print("数据库表结构已初始化")

def upgrade_db():
    with app.app_context():
        # 检查是否需要添加 source_type 字段
        try:
            # 尝试查询以检查字段是否存在
            Paper.query.with_entities(Paper.source_type).first()
            print("source_type 字段已存在")
        except Exception as e:
            if 'no such column' in str(e).lower():
                # 字段不存在，需要添加
                try:
                    # 使用原生SQL添加字段
                    db.session.execute(text("ALTER TABLE papers ADD COLUMN source_type VARCHAR(20) DEFAULT '地区联考'"))
                    db.session.commit()
                    
                    # 根据来源名称智能判断来源类型并更新
                    papers = Paper.query.all()
                    for paper in papers:
                        # 如果来源中包含"中学"、"附属"、"大学"等关键词，则设为名校调考
                        if any(keyword in paper.source for keyword in ['中学', '附属', '大学', '一中', '二中', '三中', '四中', '五中', '六中', '七中', '八中', '九中', '十中']):
                            paper.source_type = '名校调考'
                        else:
                            paper.source_type = '地区联考'
                    
                    db.session.commit()
                    print("成功添加 source_type 字段并智能更新现有数据")
                except Exception as add_error:
                    db.session.rollback()
                    print(f"添加 source_type 字段失败: {str(add_error)}")

# Flask 3.x不再支持before_first_request
def check_db_tables():
    try:
        with app.app_context():
            # 检查是否需要创建表
            inspector = db.inspect(db.engine)
            if not inspector.has_table('papers'):
                init_db()
                print("数据库表格已创建")
            else:
                print("数据库表格已存在")
                
            # 升级数据库结构
            upgrade_db()
    except Exception as e:
        print(f"数据库检查/创建时出错: {str(e)}")

# 在应用启动时初始化数据库
with app.app_context():
    check_db_tables()

# 主程序入口
if __name__ == '__main__':
    try:
        print("正在尝试启动在端口 5001...")
        app.debug = True  # 启用调试模式以获取更详细的错误信息
        app.run(host='0.0.0.0', port=5001)
    except OSError:
        print("端口 5001 被占用，尝试下一个...")
        app.debug = True  # 启用调试模式以获取更详细的错误信息
        app.run(host='0.0.0.0', port=8080)
'''
        
        # 2. 创建备份
        print("创建备份...")
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_cmd = f"cp {APP_PATH} {APP_PATH}.bak_{current_time}"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print(f"已创建备份: {APP_PATH}.bak_{current_time}")
        else:
            stderr_output = stderr.read().decode('utf-8')
            print(f"备份失败: {stderr_output}")
            # 继续执行，因为可能文件不存在
        
        # 3. 写入新应用
        print("写入新应用...")
        # 使用 cat 命令写入文件
        write_cmd = f'''cat > {APP_PATH} << 'EOF'
{simple_app}
EOF'''
        stdin, stdout, stderr = ssh.exec_command(write_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            stderr_output = stderr.read().decode('utf-8')
            print(f"写入应用失败: {stderr_output}")
            return 1
        
        # 4. 设置执行权限
        print("设置执行权限...")
        chmod_cmd = f"chmod +x {APP_PATH}"
        stdin, stdout, stderr = ssh.exec_command(chmod_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        # 5. 检查语法
        print("检查Python语法...")
        check_cmd = f"python3 -m py_compile {APP_PATH}"
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            stderr_output = stderr.read().decode('utf-8')
            print(f"语法检查失败: {stderr_output}")
            return 1
        
        print("语法检查通过！")
        
        # 6. 重启服务
        print("重启服务...")
        restart_cmd = "systemctl restart question_bank"
        stdin, stdout, stderr = ssh.exec_command(restart_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        # 7. 检查服务状态
        print("检查服务状态...")
        status_cmd = "systemctl status question_bank"
        stdin, stdout, stderr = ssh.exec_command(status_cmd)
        status = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status:
            print("服务已成功启动！问题已解决。")
        else:
            print("服务未能成功启动，查看日志...")
            log_cmd = "journalctl -u question_bank -n 30 --no-pager"
            stdin, stdout, stderr = ssh.exec_command(log_cmd)
            logs = stdout.read().decode('utf-8')
            print(logs)
            
            # 检查Nginx状态
            print("检查Nginx状态...")
            nginx_cmd = "systemctl status nginx"
            stdin, stdout, stderr = ssh.exec_command(nginx_cmd)
            nginx_status = stdout.read().decode('utf-8')
            
            if "Active: active (running)" in nginx_status:
                print("Nginx正在运行。")
            else:
                print("Nginx未运行。")
                print(nginx_status)
        
        # 关闭连接
        ssh.close()
        
    except Exception as e:
        print(f"发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        import paramiko
        from datetime import datetime
    except ImportError:
        print("需要安装paramiko库")
        print("请运行: pip3 install paramiko")
        sys.exit(1)
    
    sys.exit(fix_server_app())
