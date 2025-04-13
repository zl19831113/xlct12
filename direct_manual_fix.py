#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接手动修复SQLAlchemy语法问题
"""

import paramiko
import time
import sys

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
REMOTE_PATH = "/var/www/question_bank/app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def fix_server_app():
    """直接在服务器上修复app.py代码"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")

        # 创建备份
        print("创建备份...")
        backup_cmd = f"cp {REMOTE_PATH} {REMOTE_PATH}.bak_$(date +%Y%m%d%H%M%S)"
        stdin, stdout, stderr = ssh.exec_command(backup_cmd)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print(f"创建备份失败: {stderr.read().decode('utf-8')}")
            return 1
            
        # 修复1: 替换不符合SQLAlchemy 2.0的所有case语法
        print("修复SQLAlchemy语法...")
        
        # 修复所有case相关的语法问题
        fix_commands = [
            # 获取原始文件的副本用于对比
            f"cat {REMOTE_PATH} > /tmp/app.py.original",
            
            # 用sed修复第一个常见错误模式 - 单一条件
            "sed -i 's/db\\.case(\\[(\\([^)]*\\), [0-9])\\], else_=[0-9])/db.case(\\1, else_=0)/g' " + REMOTE_PATH,
            
            # 修复第二个常见错误模式 - 多条件错误格式
            """sed -i 's/db\\.case(\\[\\n\\s*\\(([^)]*)\\),\\n\\s*\\(([^)]*)\\)\\n\\s*\\], else_=)/db.case(\\1, \\2, else_=0)/g' """ + REMOTE_PATH,
            
            # 手动修复其他已知错误位置
            f"""sed -i '1970,1980c\\
                db.case(\\
                    (Paper.name.like(\\"%下学期%\\"), 2),\\
                    (Paper.name.like(\\"%上学期%\\"), 1),\\
                    else_=0\\
                ).desc(),' {REMOTE_PATH}""",
            
            f"""sed -i '2109,2119c\\
                db.case(\\
                    (Paper.name.like(\\"%3月%\\"), 3),\\
                    (Paper.name.like(\\"%2月%\\"), 2),\\
                    (Paper.name.like(\\"%1月%\\"), 1),\\
                    else_=0\\
                ).desc(),' {REMOTE_PATH}""",
            
            # 使用diff检查修改
            f"diff -u /tmp/app.py.original {REMOTE_PATH} || true"
        ]
        
        # 执行修复命令
        for cmd in fix_commands:
            print(f"执行: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            # 如果是最后一个diff命令，打印差异
            if "diff -u" in cmd:
                diff_output = stdout.read().decode('utf-8')
                if diff_output:
                    print("文件差异:")
                    print(diff_output[:500] + "..." if len(diff_output) > 500 else diff_output)
                else:
                    print("没有检测到文件差异")
            
            if exit_status != 0 and "diff" not in cmd:
                error = stderr.read().decode('utf-8')
                if error:
                    print(f"命令执行失败: {error}")
        
        # 验证语法
        print("验证Python语法...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 -m py_compile {REMOTE_PATH}")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            error = stderr.read().decode('utf-8')
            print(f"语法检查失败: {error}")
            return 1
        else:
            print("语法检查通过！")
        
        # 重启服务
        print("重启服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart question_bank")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            error = stderr.read().decode('utf-8')
            print(f"重启服务失败: {error}")
        
        print("等待服务启动...")
        time.sleep(5)
        
        # 检查服务状态
        stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
        status_output = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status_output:
            print("服务已成功启动！")
        else:
            print("服务未能成功启动。日志信息:")
            print(status_output)
            
            # 获取更详细的错误信息
            stdin, stdout, stderr = ssh.exec_command("journalctl -u question_bank --since '30 seconds ago' | tail -n 15")
            log_output = stdout.read().decode('utf-8')
            print(log_output)
            
            # 尝试使用最简单的方法重启服务
            print("尝试使用直接方法重启服务...")
            stdin, stdout, stderr = ssh.exec_command("cd /var/www/question_bank && python3 app.py")
            error_output = stderr.read().decode('utf-8')
            
            if error_output:
                print("直接启动遇到错误:")
                print(error_output)
            
        # 关闭连接
        ssh.close()
        
    except Exception as e:
        print(f"发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # 检查参数
    try:
        import paramiko
    except ImportError:
        print("需要安装paramiko库")
        print("请运行: pip3 install paramiko")
        sys.exit(1)
    
    sys.exit(fix_server_app())
