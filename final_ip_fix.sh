#!/bin/bash

# 最终IP修复脚本
# 通过检查发现服务器内部IP与外部IP不同，需要修复配置

REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_SERVER}"

echo "===== 修复IP配置问题 ====="

# 获取服务器内部IP
INTERNAL_IP=$(eval "${SSH_CMD} \"hostname -I | awk '{print \\\$1}'\"")
echo "服务器内部IP: $INTERNAL_IP"
echo "服务器外部IP: $REMOTE_SERVER"

# 修复Nginx配置，同时监听内部和外部IP
cat << EOF > /tmp/ip_fix.conf
server {
    listen 80;
    listen [::]:80;
    
    # 同时监听所有接口
    server_name $REMOTE_SERVER $INTERNAL_IP localhost;
    
    root /var/www/html;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

# 上传新配置
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/ip_fix.conf ${REMOTE_USER}@${REMOTE_SERVER}:/etc/nginx/sites-available/default
eval "${SSH_CMD} \"rm -f /etc/nginx/sites-enabled/* && ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/\""

# 修复hosts文件，确保两个IP都可解析
eval "${SSH_CMD} \"echo '127.0.0.1 localhost' > /etc/hosts && echo '$INTERNAL_IP $REMOTE_SERVER server' >> /etc/hosts\""

# 重启Nginx
eval "${SSH_CMD} \"nginx -t && systemctl restart nginx\""

# 如果有云服务商的安全组，尝试开放它
echo "尝试开放阿里云安全组策略(如果存在)..."
eval "${SSH_CMD} \"which aliyun && aliyun ecs AuthorizeSecurityGroup --RegionId cn-hangzhou --SecurityGroupId sg-bp67acfmxazb4p**** --IpProtocol tcp --PortRange=80/80 --SourceCidrIp 0.0.0.0/0 --Priority 1 || echo '未找到阿里云CLI工具'\""

# 检查是否有其他Web服务占用了80端口
echo "检查是否有其他Web服务占用端口..."
eval "${SSH_CMD} \"ps aux | grep apache || true\""
eval "${SSH_CMD} \"ps aux | grep nginx || true\""

# 最后一步 - 恢复应用程序
echo "恢复应用程序..."
eval "${SSH_CMD} \"cd ${REMOTE_DIR} && python3 app.py > app.log 2>&1 &\""

echo "===== 最终修复完成 ====="
echo "测试页面应该可以通过以下地址访问:"
echo "http://$REMOTE_SERVER/"
echo "http://$INTERNAL_IP/"
echo
echo "恭喜！服务器应已恢复正常"
