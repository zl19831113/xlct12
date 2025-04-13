#!/bin/bash
# 修复app.py中的缩进错误

ssh root@120.26.12.100 << 'EOF'
echo "===== 开始修复缩进错误 ====="

# 1. 停止服务
echo "停止服务..."
systemctl stop question_bank

# 2. 备份app.py
APP_PATH="/var/www/question_bank/app.py"
BACKUP_PATH="${APP_PATH}.bak_$(date +%Y%m%d%H%M%S)"
cp $APP_PATH $BACKUP_PATH
echo "已创建app.py备份: $BACKUP_PATH"

# 3. 检查并修复第2053行附近的缩进错误
echo "修复缩进错误..."
sed -n '2050,2060p' $APP_PATH

# 使用Python来修复缩进错误
python3 << 'PYTHON_SCRIPT'
import re

# 读取文件
with open('/var/www/question_bank/app.py', 'r') as f:
    lines = f.readlines()

# 查找并修复缩进错误
fixed_lines = []
in_function = False
current_indent = ""
prev_indent = ""

for i, line in enumerate(lines):
    # 检查是否是函数定义
    if re.match(r'^@app\.route|^def\s+', line):
        in_function = True
        current_indent = ""
    
    # 检查缩进
    if in_function:
        # 获取当前行的缩进
        indent_match = re.match(r'^(\s*)', line)
        if indent_match:
            current_indent = indent_match.group(1)
        
        # 检查try语句的缩进
        if "try:" in line and i > 0:
            prev_line = lines[i-1].rstrip()
            prev_indent_match = re.match(r'^(\s*)', lines[i-1])
            if prev_indent_match:
                prev_indent = prev_indent_match.group(1)
            
            # 如果try的缩进比前一行多，但前一行不是if/for/while/def等需要缩进的语句
            if len(current_indent) > len(prev_indent) and not prev_line.endswith(":"):
                # 修复缩进，使用前一行的缩进
                line = prev_indent + line.lstrip()
                print(f"修复第{i+1}行的缩进: {line.rstrip()}")
    
    fixed_lines.append(line)

# 写回文件
with open('/var/www/question_bank/app.py', 'w') as f:
    f.writelines(fixed_lines)

print("缩进修复完成")
PYTHON_SCRIPT

# 4. 检查修复后的代码
echo "检查修复后的代码..."
sed -n '2050,2060p' $APP_PATH

# 5. 启动服务
echo "启动服务..."
systemctl start question_bank

# 6. 检查服务状态
echo "检查服务状态..."
systemctl status question_bank | head -20

# 7. 等待服务启动
echo "等待服务启动..."
sleep 3

# 8. 测试筛选功能
echo "测试筛选功能..."
curl -s -X POST http://localhost:5001/filter_papers \
  -H "Content-Type: application/json" \
  -d '{"region":"湖北","page":1,"per_page":5}' | head -20

echo "===== 缩进错误修复完成 ====="
EOF
