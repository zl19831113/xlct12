#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门修复app.py中的语法错误
"""

import re
import sys
import paramiko
import time

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
PATH = "/var/www/question_bank/app.py"

# 替换掉的错误模式
error_pattern = r'db\.case\(\s*\(Paper\.name\.like\(\'%下学期%\'\), 2\),\s*\(Paper\.name\.like\(\'%上学期%\'\), 1\)\s*\], else_=\)\.desc\(\),'
correct_replacement = "db.case(\n                    (Paper.name.like('%下学期%'), 2),\n                    (Paper.name.like('%上学期%'), 1),\n                    else_=0\n                ).desc(),"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def fix_and_restart():
    """修复语法错误并重启服务"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 创建一个SFTP客户端
        sftp = ssh.open_sftp()
        
        # 读取当前文件
        with sftp.open(PATH, 'r') as f:
            content = f.read().decode('utf-8')
        
        print("已获取源文件内容")
        
        # 进行修复
        new_content = re.sub(error_pattern, correct_replacement, content)
        
        if new_content == content:
            print("警告：未找到匹配的错误模式，请检查正则表达式")
            
            # 直接搜索有问题的行
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "], else_=).desc()," in line:
                    print(f"在第 {i+1} 行找到问题: {line}")
                    # 更精确地替换这个特定行
                    lines[i-2:i+1] = [
                        "                db.case(",
                        "                    (Paper.name.like('%下学期%'), 2),",
                        "                    (Paper.name.like('%上学期%'), 1),",
                        "                    else_=0",
                        "                ).desc(),"
                    ]
                    new_content = '\n'.join(lines)
                    print("已修复特定行的问题")
                    break
        else:
            print("成功找到并修复错误模式")
        
        # 写回修复后的文件
        with sftp.open(PATH, 'w') as f:
            f.write(new_content.encode('utf-8'))
        
        print("已写入修复后的文件")
        
        # 重启服务
        print("正在重启服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart question_bank")
        stdout.channel.recv_exit_status()
        
        print("服务已重启，等待启动...")
        time.sleep(5)
        
        # 检查服务状态
        stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
        status = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status:
            print("服务已成功启动！")
        else:
            print(f"服务状态: {status}")
            print("服务可能未正确启动，请检查日志")
        
        # 关闭连接
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"发生错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # 尝试导入paramiko
    try:
        import paramiko
    except ImportError:
        print("需要安装paramiko库")
        print("运行: pip install paramiko")
        sys.exit(1)
    
    sys.exit(fix_and_restart())
