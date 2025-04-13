#!/usr/bin/env python3
import re
import os
import shutil
from datetime import datetime

# 备份原始文件
app_path = '/var/www/question_bank/app.py'
backup_path = f'/var/www/question_bank/app.py.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy2(app_path, backup_path)

# 读取原始文件
with open(app_path, 'r') as f:
    content = f.read()

# 读取新的download_paper函数
with open('/tmp/download_function.py', 'r') as f:
    new_function = f.read()

# 定义正则表达式匹配@app.route('/download_paper/...')开始的函数
pattern = r'@app\.route\(\'\/download_paper\/.*?\'\).*?def download_paper\(.*?\).*?(?=@app\.route|\Z)'
flags = re.DOTALL  # 使.也匹配换行符

# 替换函数
if re.search(pattern, content, flags):
    modified_content = re.sub(pattern, new_function, content, flags=flags)
else:
    # 如果没有找到函数，则在文件末尾添加
    modified_content = content + '\n\n' + new_function

# 写回修改后的内容
with open(app_path, 'w') as f:
    f.write(modified_content)

print("更新完成：app.py 中的 download_paper 函数已更新") 