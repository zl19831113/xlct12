#!/bin/bash

# 设置变量
TIMESTAMP=$(date +%Y%m%d%H%M%S)

echo "====== 开始本地诊断 502 Bad Gateway 错误 (${TIMESTAMP}) ======"

# 1. 检查本地网络连接性
echo "===== 检查网络连接 ====="
curl -I http://120.26.12.100 > network_check.txt 2>&1
echo "网络连接检查已保存到 network_check.txt"

# 2. 检查本地 app.py 是否有语法错误
echo "===== 检查 app.py 语法 ====="
python -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "app.py 语法正确"
else
    echo "app.py 存在语法错误，请修复"
fi

# 3. 检查本地启动是否正常
echo "===== 尝试本地启动 Flask 应用 ====="
FLASK_APP=app.py FLASK_ENV=development python -m flask run > local_flask.log 2>&1 &
LOCAL_FLASK_PID=$!
sleep 5
kill $LOCAL_FLASK_PID 2>/dev/null
echo "本地启动日志已保存到 local_flask.log"

# 4. 检查依赖版本
echo "===== 检查依赖版本 ====="
pip freeze | grep -E 'flask|werkzeug|gunicorn|sqlalchemy' > local_dependencies.txt
echo "本地依赖版本已保存到 local_dependencies.txt"

# 5. 检查 gunicorn_config.py (如果存在)
if [ -f "gunicorn_config.py" ]; then
    echo "===== 本地 gunicorn 配置 ====="
    cat gunicorn_config.py > local_gunicorn_config.txt
    echo "gunicorn配置已保存到 local_gunicorn_config.txt"
fi

# 6. 尝试本地 gunicorn 启动
echo "===== 尝试本地 gunicorn 启动 ====="
if command -v gunicorn &> /dev/null; then
    gunicorn app:app --log-level debug > local_gunicorn.log 2>&1 &
    GUNICORN_PID=$!
    sleep 5
    kill $GUNICORN_PID 2>/dev/null
    echo "gunicorn启动日志已保存到 local_gunicorn.log"
else
    echo "本地未安装 gunicorn，跳过此测试"
fi

# 7. 分析最近修改的文件
echo "===== 分析最近修改的文件 ====="
find . -name "*.py" -o -name "*.html" -type f -mtime -1 | sort > recently_modified_files.txt
echo "最近修改的文件已保存到 recently_modified_files.txt"

# 8. 建议修复步骤
echo "===== 建议修复步骤 ====="
cat << EOF > fix_suggestions.txt
502 Bad Gateway 错误修复建议：

1. 检查部署脚本是否成功执行：
   - 查看 update_server.sh 是否正确运行
   - 检查 gunicorn 是否成功启动

2. 检查依赖兼容性：
   - 尝试运行 fix_dependencies.sh 脚本
   - 确保 Flask==2.0.1 和 flask_sqlalchemy==2.5.1

3. 检查 gunicorn 配置：
   - 确保 gunicorn 绑定的 IP 和端口正确
   - 确保 nginx 配置正确代理到 gunicorn

4. 检查应用错误：
   - 检查服务器日志: /var/www/question_bank/logs/error.log
   - 检查 nginx 错误日志: /var/log/nginx/error.log

5. 修复步骤：
   - 运行 fix_dependencies.sh 修复依赖
   - 确保服务器上 app.py 没有语法错误
   - 重启 gunicorn 和 nginx
EOF

echo "修复建议已保存到 fix_suggestions.txt"

echo "====== 本地诊断完成 (${TIMESTAMP}) ======"
echo "请检查生成的日志文件，并按照 fix_suggestions.txt 中的建议进行修复" 