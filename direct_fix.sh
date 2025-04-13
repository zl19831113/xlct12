#!/bin/bash
# 直接修复app.py中的语法错误

ssh root@120.26.12.100 << 'EOF'
# 备份文件
cp /var/www/question_bank/app.py /var/www/question_bank/app.py.bak_$(date +%s)

# 直接修复filter_papers函数
sed -i '/^@app.route.*filter_papers/,/^def filter_papers/c\@app.route("/filter_papers", methods=["GET", "POST"])\ndef filter_papers():' /var/www/question_bank/app.py

# 重启服务
systemctl restart question_bank
systemctl restart nginx

# 检查服务状态
sleep 2
systemctl status question_bank | head -5
EOF
