#!/bin/bash

cat << 'EOT' > /tmp/override_download.py

# 重写download_paper函数，使其调用download_new
@app.route('/download_paper/<int:paper_id>')
def download_paper(paper_id):
    return download_new(paper_id)
EOT

cd /var/www/question_bank
cp -f app.py app.py.bak_$(date +%Y%m%d_%H%M%S)
# 寻找并删除原始download_paper函数
grep -n "@app.route('/download_paper" app.py | head -1 | cut -d ":" -f 1 > /tmp/start_line
if [ -s /tmp/start_line ]; then
    start_line=$(cat /tmp/start_line)
    end_pattern="    except Exception"
    end_line=$(tail -n +$start_line app.py | grep -n "$end_pattern" | head -1 | cut -d ":" -f 1)
    if [ -n "$end_line" ]; then
        end_line=$((start_line + end_line - 1))
        sed -i "${start_line},${end_line}d" app.py
    fi
fi
# 添加新的download_paper函数
cat /tmp/override_download.py >> app.py 