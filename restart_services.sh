#!/bin/bash

# 服务器信息
SERVER="120.26.12.100"
USER="root"
PASS="85497652Sl."

echo "正在重启服务..."

# 在服务器上执行重启操作
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "\
    systemctl restart nginx && \
    echo '服务重启完成'"

echo "所有操作已完成！" 