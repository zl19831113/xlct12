#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import subprocess
import time
import sys

def restart_flask_server():
    """重启Flask服务器并清理缓存"""
    print("开始重启Flask服务器...")
    
    # 尝试查找并终止现有的Flask进程
    try:
        print("查找现有Flask进程...")
        # 使用ps命令查找包含"python"和"app.py"的进程
        ps_output = subprocess.check_output(["ps", "aux"]).decode()
        
        # 查找所有匹配的进程ID
        flask_pids = []
        for line in ps_output.split('\n'):
            if 'python' in line and 'app.py' in line and 'grep' not in line:
                print(f"找到Flask进程: {line}")
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    flask_pids.append(pid)
        
        # 终止找到的进程
        if flask_pids:
            for pid in flask_pids:
                print(f"终止进程 PID: {pid}")
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"成功终止进程 PID: {pid}")
                except Exception as e:
                    print(f"终止进程 {pid} 时出错: {e}")
            
            # 等待进程彻底终止
            time.sleep(2)
        else:
            print("未找到正在运行的Flask进程")
    
    except Exception as e:
        print(f"查找或终止进程时出错: {e}")
    
    # 清理缓存文件
    try:
        print("清理缓存文件...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dirs = [
            os.path.join(base_dir, "__pycache__"),
            os.path.join(base_dir, "static", "__pycache__")
        ]
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                for cache_file in os.listdir(cache_dir):
                    cache_path = os.path.join(cache_dir, cache_file)
                    try:
                        if os.path.isfile(cache_path):
                            os.remove(cache_path)
                            print(f"删除缓存文件: {cache_path}")
                    except Exception as e:
                        print(f"删除缓存文件出错: {e}")
    
    except Exception as e:
        print(f"清理缓存时出错: {e}")
    
    # 重新启动Flask服务器
    try:
        print("重新启动Flask服务器...")
        flask_command = ["python", "app.py"]
        process = subprocess.Popen(
            flask_command, 
            cwd=base_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            start_new_session=True
        )
        
        # 等待几秒钟检查服务器是否成功启动
        time.sleep(3)
        
        if process.poll() is None:
            # 进程仍在运行，说明启动成功
            print(f"Flask服务器已成功重启，PID: {process.pid}")
            print("请刷新浏览器以查看更新后的内容")
            return True
        else:
            # 进程已终止，启动失败
            stdout, stderr = process.communicate()
            print(f"Flask服务器启动失败")
            print(f"标准输出: {stdout.decode() if stdout else ''}")
            print(f"错误输出: {stderr.decode() if stderr else ''}")
            return False
            
    except Exception as e:
        print(f"重启服务器时出错: {e}")
        return False

if __name__ == "__main__":
    print("=== 重启Flask服务器和清理缓存 ===")
    
    # 询问用户确认
    print("\n注意: 此操作将终止当前运行的服务器并重启。您当前的工作可能会丢失。")
    response = input("是否继续? (y/n): ")
    
    if response.lower() == 'y':
        success = restart_flask_server()
        if success:
            print("\n服务器重启成功")
            print("请完全刷新浏览器(按Cmd+Shift+R或Ctrl+F5)以清除浏览器缓存")
        else:
            print("\n服务器重启失败，请手动重启")
    else:
        print("操作已取消")
