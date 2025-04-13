#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复服务器上的SQLAlchemy语法问题 - 简单直接的方法
"""

import paramiko
import sys
import time

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
APP_PATH = "/var/www/question_bank/app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def quick_fix():
    """直接在服务器上修复问题"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 创建简单直接的修复脚本
        fix_script = """#!/bin/bash
# 备份当前文件
cp {path} {path}.bak_$(date +%Y%m%d%H%M%S)

# 直接用sed修复文件 - 替换db.case为case并修复语法
sed -i 's/from sqlalchemy import text/from sqlalchemy import text, case/g' {path}
sed -i 's/db.case(/case(/g' {path}

# 修复filter_papers函数中的排序逻辑 - 使用双引号避免转义问题
sed -i '2104,2118c\\
        # 排序逻辑\\
        sorted_query = query.order_by(\\
            Paper.year.desc(),\\
            case((Paper.region == "湖北", 1), else_=0).desc(),\\
            case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),\\
            case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),\\
            Paper.upload_time.desc()\\
        )' {path}

# 修复papers_list函数中的排序逻辑
sed -i '1965,1985c\\
                Paper.year.desc(),\\
                # 湖北地区优先\\
                case((Paper.region == "湖北", 1), else_=0).desc(),\\
                # 下学期优先于上学期\\
                case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),\\
                # 3月优先于2月优先于1月\\
                case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),\\
                # 最后按上传时间降序排序(最新上传的优先)\\
                Paper.upload_time.desc()' {path}

# 验证Python语法
python3 -m py_compile {path}

# 如果语法检查通过，重启服务
if [ $? -eq 0 ]; then
    echo "语法检查通过，重启服务..."
    systemctl restart question_bank
    sleep 3
    systemctl status question_bank
else
    echo "语法检查失败，未重启服务"
    exit 1
fi
""".format(path=APP_PATH)
        
        # 在服务器上创建修复脚本
        fix_script_path = "/tmp/fix_app.sh"
        sftp = ssh.open_sftp()
        with sftp.open(fix_script_path, 'w') as f:
            f.write(fix_script)
        sftp.close()
        
        # 赋予执行权限并运行脚本
        print("创建修复脚本并执行...")
        stdin, stdout, stderr = ssh.exec_command(f"chmod +x {fix_script_path} && {fix_script_path}")
        
        # 获取输出
        stdout_str = stdout.read().decode('utf-8')
        stderr_str = stderr.read().decode('utf-8')
        exit_status = stdout.channel.recv_exit_status()
        
        if stdout_str:
            print("输出:")
            print(stdout_str)
        
        if stderr_str:
            print("错误:")
            print(stderr_str)
        
        # 确认服务状态
        print("检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
        status = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status:
            print("服务已成功启动！问题已解决。")
        else:
            print("服务未能成功启动。检查Nginx状态...")
            stdin, stdout, stderr = ssh.exec_command("systemctl status nginx")
            nginx_status = stdout.read().decode('utf-8')
            
            if "Active: active (running)" in nginx_status:
                print("Nginx正在运行。问题可能是Flask应用本身。")
            else:
                print("尝试重启Nginx...")
                stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status != 0:
                    print(f"重启Nginx失败: {stderr.read().decode('utf-8')}")
                else:
                    print("Nginx已重启")
        
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
    
    sys.exit(quick_fix())
