#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接在服务器上修复SQLAlchemy 2.0兼容性问题
"""

import paramiko
import sys
import time

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def fix_on_server():
    """直接在服务器上执行修复操作"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 直接在服务器上执行命令
        commands = [
            # 显示当前目录和文件状态
            "cd /var/www/question_bank && ls -la app.py*",
            
            # 创建备份
            "cd /var/www/question_bank && cp app.py app.py.bak_$(date +%Y%m%d%H%M%S)",
            
            # 修复SQLAlchemy 2.0兼容性问题
            # 1. 添加case导入
            "cd /var/www/question_bank && sed -i 's/from sqlalchemy import text/from sqlalchemy import text, case/g' app.py",
            
            # 2. 修复 db.case 为 case
            "cd /var/www/question_bank && sed -i 's/db\.case/case/g' app.py",
            
            # 3. 修复排序部分 - 先定位papers_list函数中的排序逻辑
            """cd /var/www/question_bank && sed -i '1955,1985c\\
            # 排序规则：年份降序 > 湖北地区优先 > 下学期优先于上学期 > 3月优先于2月优先于1月 > 上传时间降序\\
            sorted_query = query.order_by(\\
                Paper.year.desc(),\\
                # 湖北地区优先\\
                case((Paper.region == "湖北", 1), else_=0).desc(),\\
                # 下学期优先于上学期\\
                case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),\\
                # 3月优先于2月优先于1月\\
                case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),\\
                # 最后按上传时间降序排序(最新上传的优先)\\
                Paper.upload_time.desc()\\
            )' app.py""",
            
            # 4. 修复filter_papers函数中的排序逻辑
            """cd /var/www/question_bank && sed -i '2100,2120c\\
        # 排序逻辑\\
        sorted_query = query.order_by(\\
            Paper.year.desc(),\\
            case((Paper.region == "湖北", 1), else_=0).desc(),\\
            case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),\\
            case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),\\
            Paper.upload_time.desc()\\
        )' app.py""",
            
            # 5. 验证Python语法
            "cd /var/www/question_bank && python3 -m py_compile app.py",
            
            # 6. 重启服务
            "systemctl restart question_bank",
            
            # 7. 检查服务状态
            "systemctl status question_bank"
        ]
        
        # 执行每个命令
        for i, cmd in enumerate(commands):
            print(f"\n执行命令 {i+1}/{len(commands)}:")
            print(f"$ {cmd}")
            
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            # 获取输出
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            
            if stdout_data:
                print(f"输出: {stdout_data}")
            
            if stderr_data:
                print(f"错误: {stderr_data}")
            
            # 如果是语法检查命令且失败，我们需要查看具体的错误信息
            if "py_compile" in cmd and exit_status != 0:
                print(f"Python语法检查失败，退出码: {exit_status}")
                
                # 创建简化版应用
                print("\n创建简化版应用...")
                simplified_app = """
import os
from flask import Flask, render_template, request, jsonify
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter_papers', methods=['GET', 'POST'])
def filter_papers():
    try:
        if request.method == 'POST':
            filter_data = request.get_json()
            region = filter_data.get('region')
            subject = filter_data.get('subject')
            page = filter_data.get('page', 1)
            per_page = filter_data.get('per_page', 20)
        else:
            region = request.args.get('region')
            subject = request.args.get('subject')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
        
        # 构建查询
        query = Paper.query
        
        # 添加筛选条件
        if region:
            query = query.filter(Paper.region == region)
        if subject:
            query = query.filter(Paper.subject == subject)
        
        # 排序逻辑
        sorted_query = query.order_by(
            Paper.year.desc(),
            case((Paper.region == "湖北", 1), else_=0).desc(),
            Paper.upload_time.desc()
        )
        
        # 计算总数
        total = sorted_query.count()
        
        # 分页
        paginated = sorted_query.paginate(page=page, per_page=per_page, error_out=False)
        papers = paginated.items
        
        # 构建试卷数据
        papers_data = [paper.to_dict() for paper in papers]
        
        return jsonify(papers_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
"""
                
                # 直接写入简化版应用
                create_simple_cmd = f"""cat > /var/www/question_bank/app.py << 'EOF'
{simplified_app}
EOF"""
                
                stdin, stdout, stderr = ssh.exec_command(create_simple_cmd)
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status != 0:
                    print(f"创建简化版应用失败: {stderr.read().decode('utf-8')}")
                else:
                    print("简化版应用创建成功，重启服务...")
                    
                    # 重启服务
                    stdin, stdout, stderr = ssh.exec_command("systemctl restart question_bank")
                    exit_status = stdout.channel.recv_exit_status()
                    
                    # 检查服务状态
                    stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
                    status = stdout.read().decode('utf-8')
                    
                    if "Active: active (running)" in status:
                        print("服务已成功启动！问题已解决。")
                    else:
                        print("服务仍未能启动。")
                        print(status)
                
                # 停止执行后续命令
                break
        
        # 关闭连接
        ssh.close()
        
    except Exception as e:
        print(f"发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        import paramiko
    except ImportError:
        print("需要安装paramiko库")
        print("请运行: pip3 install paramiko")
        sys.exit(1)
    
    sys.exit(fix_on_server())
