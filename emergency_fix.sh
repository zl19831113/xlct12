#!/bin/bash

# 紧急修复 - 绝对最小化配置重启
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 紧急修复 ====="

# 安装所有可能需要的Python包
eval "${SSH_CMD} \"apt-get update && apt-get install -y python3-flask python3-sqlalchemy python3-docx python3-pillow python3-werkzeug python3-wtforms python3-tqdm && pip3 install --break-system-packages flask-sqlalchemy flask-wtf\""

# 检查app.py中是否设置了正确的端口
cat << EOF > /tmp/check_port.py
#!/usr/bin/env python3
import re

with open('app.py', 'r') as f:
    content = f.read()

# 检查端口配置
port_search = re.search(r'app\.run\(.*?port\s*=\s*(\d+)', content)
if port_search:
    port = port_search.group(1)
    print(f"应用使用端口: {port}")
else:
    print("未找到端口设置，正在修改app.py...")
    with open('app.py', 'a') as f:
        f.write("\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000, debug=True)\n")
    print("已添加默认端口5000")
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/check_port.py ${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/check_port.py
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && chmod +x check_port.py && python3 check_port.py\""

# 创建应急Nginx配置
cat << EOF > /tmp/emergency.conf
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /static {
        alias /var/www/question_bank/static;
    }
}
EOF

sshpass -p "${REMOTE_PASSWORD}" scp /tmp/emergency.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/ && systemctl restart nginx\""

# 杀掉所有Python进程并启动
eval "${SSH_CMD} \"pkill -f python || true; cd ${REMOTE_DIR} && nohup python3 app.py > emergency.log 2>&1 &\""

# 10秒内检查日志
echo "正在检查应用日志..."
sleep 5
eval "${SSH_CMD} \"tail -n 20 ${REMOTE_DIR}/emergency.log\""
