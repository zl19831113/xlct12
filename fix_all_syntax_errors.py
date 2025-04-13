#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面修复app.py中的所有语法错误
"""

import paramiko
import time
import re
import sys
import os

# 服务器信息
SERVER = "120.26.12.100"
USERNAME = "root"
REMOTE_PATH = "/var/www/question_bank/app.py"
LOCAL_PATH = "app.py"

def get_server_password():
    """获取服务器密码"""
    import getpass
    return getpass.getpass(f"请输入{USERNAME}@{SERVER}的密码: ")

def manually_fix_app_py():
    """下载app.py，手动修复所有语法错误，然后上传回去"""
    try:
        # 获取密码
        password = get_server_password()
        
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=password)
        print(f"已连接到服务器 {SERVER}")
        
        # 创建SFTP客户端
        sftp = ssh.open_sftp()
        
        # 下载远程文件到本地
        print(f"正在下载 {REMOTE_PATH} 到本地...")
        sftp.get(REMOTE_PATH, LOCAL_PATH)
        
        # 读取文件内容
        with open(LOCAL_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份原始文件
        with open(f"{LOCAL_PATH}.before_fix", 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"已创建备份文件: {LOCAL_PATH}.before_fix")
        
        # 修复语法错误 - 查找所有 db.case( 开头并且包含 ], else_=) 的代码块
        fix_count = 0
        
        # 使用正则表达式查找和替换错误模式
        pattern = r'db\.case\(\s*\([^)]+\),\s*\([^)]+\)\s*\],\s*else_=\)'
        
        def fix_match(match):
            nonlocal fix_count
            text = match.group(0)
            # 解析出两个条件语句
            conditions = re.findall(r'\([^)]+\)', text)
            if len(conditions) >= 2:
                fix_count += 1
                # 构建正确的语法
                return f"db.case({conditions[0]}, {conditions[1]}, else_=0)"
            return text
        
        new_content = re.sub(pattern, fix_match, content)
        
        # 如果没有找到匹配项，尝试逐行扫描和修复
        if fix_count == 0:
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i]
                if 'db.case(' in line and not line.strip().endswith(','):
                    # 查找这个case语句的结束位置
                    start = i
                    bracket_count = line.count('(') - line.count(')')
                    j = i + 1
                    block = [line]
                    
                    # 继续读取直到括号平衡
                    while j < len(lines) and bracket_count > 0:
                        block.append(lines[j])
                        bracket_count += lines[j].count('(') - lines[j].count(')')
                        j += 1
                    
                    # 形成完整的代码块
                    block_text = '\n'.join(block)
                    
                    # 检查是否包含错误模式
                    if '], else_=)' in block_text:
                        fix_count += 1
                        print(f"在第 {start+1}-{j} 行找到错误代码块")
                        
                        # 尝试修复这个代码块
                        if '(Paper.name.like' in block_text or '(Paper.region' in block_text:
                            # 提取条件部分
                            conditions = re.findall(r'\([^)]+\)', block_text)
                            if len(conditions) >= 2:
                                # 根据条件构建新的代码块
                                indent = re.match(r'^\s*', lines[start]).group(0)
                                new_block = [
                                    f"{indent}db.case(",
                                    f"{indent}    {conditions[0]},",
                                    f"{indent}    {conditions[1]},",
                                    f"{indent}    else_=0",
                                    f"{indent}).desc(),"
                                ]
                                
                                # 替换原始代码块
                                lines[start:j] = new_block
                                i = start + len(new_block) - 1
                    i += 1
                else:
                    i += 1
            
            # 重建文件内容
            new_content = '\n'.join(lines)
        
        print(f"已修复 {fix_count} 处语法错误")
        
        # 写入修复后的文件
        with open(LOCAL_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 上传修复后的文件到服务器
        print(f"正在上传修复后的文件到 {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        
        # 重启服务
        print("正在重启服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart question_bank")
        stdout.channel.recv_exit_status()
        
        print("服务已重启，等待启动...")
        time.sleep(5)
        
        # 检查服务状态
        stdin, stdout, stderr = ssh.exec_command("systemctl status question_bank")
        exit_status = stdout.channel.recv_exit_status()
        status_output = stdout.read().decode('utf-8')
        
        if "Active: active (running)" in status_output:
            print("服务已成功启动！")
        else:
            print("服务可能未正确启动，检查错误信息...")
            print(status_output)
            
            # 如果服务未启动，检查服务日志
            print("获取最新日志...")
            stdin, stdout, stderr = ssh.exec_command("journalctl -u question_bank --since '30 seconds ago' | tail -n 20")
            log_output = stdout.read().decode('utf-8')
            print(log_output)
        
        # 关闭连接
        sftp.close()
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
    
    sys.exit(manually_fix_app_py())
