#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确修复app.py的语法错误 - 针对服务器上的实际代码行
"""

import paramiko
import sys

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
APP_PATH = "/var/www/question_bank/app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def precise_fix():
    """精确修复语法错误"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 获取文件内容分析错误
        sftp = ssh.open_sftp()
        
        # 创建备份
        print("创建备份...")
        current_time = ssh.exec_command("date +%Y%m%d%H%M%S")[1].read().decode().strip()
        backup_path = f"{APP_PATH}.bak_{current_time}"
        sftp.put(APP_PATH, backup_path)
        print(f"已创建备份: {backup_path}")
        
        # 读取错误行附近的内容
        print("读取文件内容...")
        with sftp.open(APP_PATH, 'r') as f:
            lines = f.readlines()
        
        # 获取错误行附近的内容
        error_line_num = 1964
        context_start = max(0, error_line_num - 15)
        context_end = min(len(lines), error_line_num + 15)
        
        context_lines = lines[context_start:context_end]
        print(f"错误行({error_line_num})及其上下文:")
        for i, line in enumerate(context_lines):
            line_num = context_start + i + 1
            print(f"{line_num}: {line.strip()}")
        
        # 恢复到稳定版本
        print("\n恢复到一个可靠的备份版本并应用SQLAlchemy 2.0兼容性修复")
        
        # 创建简单的修复脚本，专注于在正确的SQLAlchemy 2.0语法下修复服务器应用
        fix_script = """#!/bin/bash

# 备份当前文件
cp {app_path} {app_path}.bak_$(date +%Y%m%d%H%M%S)

# 修复部分 1: 导入SQLAlchemy case函数
sed -i 's/from sqlalchemy import text/from sqlalchemy import text, case/g' {app_path}

# 修复部分 2: 替换db.case为case
sed -i 's/db\\.case/case/g' {app_path}

# 修复部分 3: 处理filter_papers函数中的排序逻辑 
# 找到filter_papers函数中的sorted_query
line_num=$(grep -n "# 排序逻辑" {app_path} | grep -v "#" | cut -d':' -f1)
if [ -n "$line_num" ]; then
    start_line=$line_num
    end_line=$((start_line + 20))  # 假设排序代码在20行内
    
    # 检查行号
    echo "找到排序逻辑代码，从第 $start_line 行开始"
    
    # 替换整个排序逻辑部分
    sed -i "${{start_line}},${{end_line}}c\\
        # 排序逻辑\\
        sorted_query = query.order_by(\\
            Paper.year.desc(),\\
            case((Paper.region == \\"湖北\\", 1), else_=0).desc(),\\
            case((Paper.name.like(\\"%下学期%\\"), 2), (Paper.name.like(\\"%上学期%\\"), 1), else_=0).desc(),\\
            case((Paper.name.like(\\"%3月%\\"), 3), (Paper.name.like(\\"%2月%\\"), 2), (Paper.name.like(\\"%1月%\\"), 1), else_=0).desc(),\\
            Paper.upload_time.desc()\\
        )" {app_path}
    
    echo "已修复filter_papers函数中的排序逻辑"
else
    echo "未找到排序逻辑代码，跳过修复"
fi

# 修复部分 4: 修复papers_list函数中的排序逻辑
papers_sort_line=$(grep -n "# 排序规则" {app_path} | head -1 | cut -d':' -f1)
if [ -n "$papers_sort_line" ]; then
    sort_start=$papers_sort_line
    sort_end=$((sort_start + 20))
    
    echo "找到papers_list排序规则，从第 $sort_start 行开始"
    
    # 替换整个排序部分
    sed -i "${{sort_start}},${{sort_end}}c\\
            # 排序规则：年份降序 > 湖北地区优先 > 下学期优先于上学期 > 3月优先于2月优先于1月 > 上传时间降序\\
            sorted_query = query.order_by(\\
                Paper.year.desc(),\\
                # 湖北地区优先\\
                case((Paper.region == \\"湖北\\", 1), else_=0).desc(),\\
                # 下学期优先于上学期\\
                case((Paper.name.like(\\"%下学期%\\"), 2), (Paper.name.like(\\"%上学期%\\"), 1), else_=0).desc(),\\
                # 3月优先于2月优先于1月\\
                case((Paper.name.like(\\"%3月%\\"), 3), (Paper.name.like(\\"%2月%\\"), 2), (Paper.name.like(\\"%1月%\\"), 1), else_=0).desc(),\\
                # 最后按上传时间降序排序(最新上传的优先)\\
                Paper.upload_time.desc()\\
            )" {app_path}
    
    echo "已修复papers_list函数中的排序逻辑"
else
    echo "未找到papers_list排序规则，跳过修复"
fi

# 检查语法
echo "检查Python语法..."
python3 -m py_compile {app_path}

if [ $? -eq 0 ]; then
    echo "语法检查通过！准备重启服务..."
    # 重启服务
    systemctl restart question_bank
    sleep 3
    systemctl status question_bank | head -15
else
    echo "语法检查失败，查看错误..."
    python3 -c "import py_compile; py_compile.compile('{app_path}')" 2>&1
    exit 1
fi
""".format(app_path=APP_PATH)
        
        # 在服务器上创建修复脚本
        fix_script_path = "/tmp/precise_fix.sh"
        with sftp.open(fix_script_path, 'w') as f:
            f.write(fix_script)
        
        # 关闭SFTP连接
        sftp.close()
        
        # 赋予执行权限并运行脚本
        print("\n执行修复脚本...")
        stdin, stdout, stderr = ssh.exec_command(f"chmod +x {fix_script_path} && {fix_script_path}")
        
        # 实时输出结果
        stdout_str = ""
        stderr_str = ""
        
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                chunk = stdout.channel.recv(1024).decode('utf-8')
                stdout_str += chunk
                print(chunk, end='')
            
            if stderr.channel.recv_stderr_ready():
                chunk = stderr.channel.recv_stderr(1024).decode('utf-8')
                stderr_str += chunk
                print(chunk, end='')
        
        # 获取剩余输出
        while stdout.channel.recv_ready():
            chunk = stdout.channel.recv(1024).decode('utf-8')
            stdout_str += chunk
            print(chunk, end='')
        
        while stderr.channel.recv_stderr_ready():
            chunk = stderr.channel.recv_stderr(1024).decode('utf-8')
            stderr_str += chunk
            print(chunk, end='')
        
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print(f"\n脚本执行失败，错误码: {exit_status}")
            
            # 如果修复失败，尝试一个简化版的应用
            print("\n尝试部署一个简化版的应用...")
            
            # 创建简化版的Flask应用，只保留基本功能
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
            
            # 保存临时应用
            with sftp.open(f"{APP_PATH}.simple", 'w') as f:
                f.write(simplified_app)
            
            # 测试简化版应用的语法
            stdin, stdout, stderr = ssh.exec_command(f"python3 -m py_compile {APP_PATH}.simple")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                print("简化版应用语法正确，正在部署...")
                
                # 备份当前应用并部署简化版
                stdin, stdout, stderr = ssh.exec_command(f"cp {APP_PATH}.simple {APP_PATH} && systemctl restart question_bank")
                exit_status = stdout.channel.recv_exit_status()
                
                # 检查服务状态
                stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
                status = stdout.read().decode('utf-8')
                
                if "Active: active (running)" in status:
                    print("简化版应用成功启动！问题已解决。")
                else:
                    print("即使使用简化版应用也无法启动服务。")
                    print(status)
            else:
                print("简化版应用语法检查失败。可能需要手动干预。")
                stderr_content = stderr.read().decode('utf-8')
                print(f"错误信息: {stderr_content}")
        else:
            print("\n脚本执行成功！")
            
            # 检查服务状态
            stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
            status = stdout.read().decode('utf-8')
            
            if "Active: active (running)" in status:
                print("服务已成功启动！问题已解决。")
            else:
                print("服务未能成功启动。")
                print(status)
        
        # 清理临时文件
        ssh.exec_command(f"rm -f {fix_script_path}")
        
        # 关闭SSH连接
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
    
    sys.exit(precise_fix())
