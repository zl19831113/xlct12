#!/bin/bash

# 深度诊断脚本 - 获取详细日志和错误信息
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 开始深度诊断 ====="

# 检查服务器基本情况
echo "1. 检查服务器基本状态..."
eval "${SSH_CMD} \"uptime && free -h && df -h\""

# 检查网络端口和服务状态
echo "2. 检查网络端口和服务状态..."
eval "${SSH_CMD} \"ss -tuln && systemctl status nginx\""

# 检查Nginx状态和配置
echo "3. 检查Nginx配置..."
eval "${SSH_CMD} \"nginx -t && cat /etc/nginx/sites-enabled/*\""

# 检查应用是否在运行
echo "4. 检查Python进程..."
eval "${SSH_CMD} \"ps aux | grep python\""

# 修改应用程序启动方式为最简单方法
echo "5. 创建极简Flask应用用于测试..."
cat << 'EOF' > /tmp/test_app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>测试服务器正常工作</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/test_app.py ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/test_app.py

# 先杀掉所有旧进程
eval "${SSH_CMD} \"pkill -9 -f python || true\""
sleep 2

# 启动测试应用
echo "6. 启动测试应用..."
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && nohup python3 test_app.py > test_app.log 2>&1 &\""
sleep 3

# 创建新的Nginx配置指向测试应用
cat << EOF > /tmp/test_nginx.conf
server {
    listen 80 default_server;
    server_name _;
    
    access_log /var/log/nginx/test_access.log;
    error_log /var/log/nginx/test_error.log;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/test_nginx.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/ && systemctl restart nginx\""

# 检查防火墙状态
echo "7. 检查防火墙状态..."
eval "${SSH_CMD} \"ufw status || iptables -L || firewall-cmd --list-all || echo '未找到防火墙软件'\""

# 尝试从服务器内部访问测试应用
echo "8. 从服务器内部测试应用..."
eval "${SSH_CMD} \"curl -v http://localhost:8080/\""

# 检查端口8080是否被监听
echo "9. 验证端口8080是否正常监听..."
eval "${SSH_CMD} \"netstat -tuln | grep 8080\""

# 显示日志内容
echo "10. 测试应用日志..."
eval "${SSH_CMD} \"cat ${REMOTE_DIR}/test_app.log\""

echo "11. Nginx访问日志..."
eval "${SSH_CMD} \"tail -n 20 /var/log/nginx/access.log\""

echo "12. Nginx错误日志..."
eval "${SSH_CMD} \"tail -n 20 /var/log/nginx/error.log\""

echo "===== 诊断完成 ====="
echo "请立即访问测试页面: http://120.26.12.100/"
echo "如果测试页面显示，则说明Nginx和网络配置正常，问题出在原应用程序"
echo "如果测试页面无法显示，则可能是服务器网络或防火墙问题"
