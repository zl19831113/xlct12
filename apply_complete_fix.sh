#!/bin/bash

# 应用完整的分页和筛选修复脚本
# 创建日期: 2025-04-02

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 本地路径
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"

echo "===== 开始应用完整的分页和筛选修复 ====="

# ===== 第1步：注入完整的修复脚本到papers.html ====="
echo "1. 注入完整的修复脚本到papers.html..."

# 创建注入脚本
cat > $LOCAL_DIR/inject_complete_fix.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将完整的修复脚本注入到HTML文件中
"""

import os
import sys

def inject_script(html_path, script_path):
    """将脚本注入到HTML文件中"""
    try:
        # 读取HTML文件
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 读取脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 创建脚本标签
        script_tag = f'<script>\n// 完整的分页和筛选修复脚本\n{script_content}\n</script>'
        
        # 检查脚本是否已存在
        if script_content[:20] in html_content:
            print(f"修复脚本已存在于{html_path}")
            return html_content
        
        # 在</body>前插入脚本
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{script_tag}\n</body>')
            print(f"已将完整修复脚本注入到{html_path}")
        else:
            # 如果没有</body>标签，则在文件末尾添加
            html_content += f'\n{script_tag}\n'
            print(f"已将完整修复脚本添加到{html_path}末尾")
        
        # 写回文件
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_content
    except Exception as e:
        print(f"注入脚本到{html_path}失败: {e}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 inject_complete_fix.py <html_path> <script_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    script_path = sys.argv[2]
    
    # 检查文件是否存在
    for path in [html_path, script_path]:
        if not os.path.exists(path):
            print(f"错误: 找不到文件 {path}")
            sys.exit(1)
    
    # 创建备份
    backup_path = f"{html_path}.bak_complete"
    try:
        with open(html_path, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(backup_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"已创建备份: {backup_path}")
    except Exception as e:
        print(f"创建备份失败: {e}")
        sys.exit(1)
    
    # 注入脚本
    inject_script(html_path, script_path)

if __name__ == "__main__":
    main()
EOF

# 注入修复脚本到本地HTML文件
echo "   注入修复脚本到本地HTML文件..."
python3 $LOCAL_DIR/inject_complete_fix.py $LOCAL_DIR/templates/papers.html $LOCAL_DIR/complete_pagination_fix.js

# 上传修复脚本到服务器
echo "2. 上传修复脚本到服务器..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/complete_pagination_fix.js $USER@$SERVER:$REMOTE_DIR/
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no $LOCAL_DIR/inject_complete_fix.py $USER@$SERVER:$REMOTE_DIR/

# 在服务器上执行注入
echo "3. 在服务器上执行注入..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_DIR && python3 inject_complete_fix.py $REMOTE_DIR/templates/papers.html $REMOTE_DIR/complete_pagination_fix.js"

# 重启服务
echo "4. 重启服务..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl restart zujuanwang.service"

# 检查服务状态
echo "5. 检查服务状态..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER "systemctl status zujuanwang.service | head -n 20"

echo "===== 修复完成 ====="
echo "请访问网站检查分页和筛选功能是否正常工作。"
