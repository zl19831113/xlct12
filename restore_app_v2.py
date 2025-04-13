#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复app.py到最后一个已知正常的备份，然后手动修复SQLAlchemy兼容性问题
"""

import paramiko
import sys
import time
import re

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
REMOTE_PATH = "/var/www/question_bank/app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def restore_and_fix():
    """恢复备份，然后修复SQLAlchemy 2.0兼容性问题"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 先查找可用备份
        print("检查可用备份...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/question_bank/app.py.bak_*")
        backups_output = stdout.read().decode('utf-8').strip()
        
        if not backups_output:
            print("未找到备份文件")
            return 1
            
        backups = backups_output.split('\n')
        
        if backups and len(backups) > 0:
            print(f"发现 {len(backups)} 个备份文件:")
            backup_paths = []
            
            for i, backup_line in enumerate(backups):
                # 提取文件路径
                match = re.search(r'(/var/www/question_bank/app\.py\.bak_[0-9]+)', backup_line)
                if match:
                    backup_path = match.group(1)
                    backup_paths.append(backup_path)
                    print(f"{i+1}. {backup_path}")
            
            if not backup_paths:
                print("无法提取备份文件路径")
                return 1
                
            # 选择最早的备份文件（假设最早的更稳定）
            selected_backup = backup_paths[0]
            print(f"选择使用备份: {selected_backup}")
            
            # 恢复备份
            print(f"恢复备份到 {REMOTE_PATH}...")
            stdin, stdout, stderr = ssh.exec_command(f"cp {selected_backup} {REMOTE_PATH}")
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status != 0:
                print(f"恢复备份失败: {stderr.read().decode('utf-8')}")
                return 1
        else:
            print("未找到备份文件")
            return 1
        
        # 修改app.py中的SQLAlchemy case语法，使其与2.0版本兼容
        print("修复SQLAlchemy case语法...")
        
        update_commands = [
            # 导入case函数
            r"sed -i '1,50s/from sqlalchemy import text/from sqlalchemy import text, case/' " + REMOTE_PATH,
            
            # 替换所有db.case为case
            r"sed -i 's/db\.case(/case(/g' " + REMOTE_PATH,
            
            # 替换 case([(condition, value)], else_=0) 格式为 case((condition, value), else_=0)
            r"sed -i 's/case(\[\(([^)]*), \([0-9]\+\)\)], else_=\([0-9]\+\))/case((\1, \2), else_=\3)/g' " + REMOTE_PATH,
            
            # 在papers_list函数中手动修复第一个排序语句
            """sed -i '/[#] 排序规则：年份降序/,/[#] 最后按上传时间降序排序/c\\
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
            )' """ + REMOTE_PATH,
            
            # 在filter_papers函数中手动修复排序语句
            """sed -i '/sorted_query = query.order_by(/,/Paper.upload_time.desc()/c\\
            sorted_query = query.order_by(\\
                Paper.year.desc(),\\
                case((Paper.region == "湖北", 1), else_=0).desc(),\\
                case((Paper.name.like("%下学期%"), 2), (Paper.name.like("%上学期%"), 1), else_=0).desc(),\\
                case((Paper.name.like("%3月%"), 3), (Paper.name.like("%2月%"), 2), (Paper.name.like("%1月%"), 1), else_=0).desc(),\\
                Paper.upload_time.desc()\\
            )' """ + REMOTE_PATH
        ]
        
        for cmd in update_commands:
            print(f"执行更新命令...")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            error = stderr.read().decode('utf-8')
            
            if exit_status != 0 and error:
                print(f"命令执行失败: {error}")
        
        # 验证语法
        print("验证Python语法...")
        stdin, stdout, stderr = ssh.exec_command(f"cd /var/www/question_bank && python3 -m py_compile {REMOTE_PATH}")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            error = stderr.read().decode('utf-8')
            print(f"语法检查失败: {error}")
            
            # 显示具体错误
            stdin, stdout, stderr = ssh.exec_command(f"cd /var/www/question_bank && python3 -c 'import py_compile; py_compile.compile(\"{REMOTE_PATH}\")'")
            error = stderr.read().decode('utf-8')
            if error:
                print(f"编译错误详情: {error}")
            return 1
        else:
            print("Python语法检查通过！")
        
        # 重启服务
        print("重启服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart question_bank")
        exit_status = stdout.channel.recv_exit_status()
        error = stderr.read().decode('utf-8')
        
        if exit_status != 0 and error:
            print(f"重启服务失败: {error}")
        
        # 等待服务启动
        print("等待服务启动...")
        time.sleep(5)
        
        # 检查服务状态
        stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
        status = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status:
            print("服务已成功启动！问题已解决。")
        else:
            print("服务未能成功启动，查看日志...")
            stdin, stdout, stderr = ssh.exec_command("journalctl -u question_bank --since '30 seconds ago' | tail -n 20")
            log = stdout.read().decode('utf-8')
            print(log)
            
            # 尝试直接运行应用程序
            print("\n尝试直接运行应用程序来查看具体错误...")
            stdin, stdout, stderr = ssh.exec_command("cd /var/www/question_bank && python3 -c 'import app'")
            error = stderr.read().decode('utf-8')
            if error:
                print(f"导入错误:\n{error}")
        
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
    
    sys.exit(restore_and_fix())
