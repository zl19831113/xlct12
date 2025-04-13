#!/bin/bash

# 修复Nginx配置脚本
# 创建于: 2025-04-01

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 配置
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root"
REMOTE_PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"

# 检查sshpass是否已安装
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}正在安装sshpass工具...${NC}"
    brew install sshpass
    if [ $? -ne 0 ]; then
        echo -e "${RED}无法安装sshpass，将使用普通SSH连接，需要手动输入密码${NC}"
        SSH_CMD="ssh"
    else
        SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
    fi
else
    SSH_CMD="sshpass -p \"${REMOTE_PASSWORD}\" ssh"
fi

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}     修复Nginx配置路径问题     ${NC}"
echo -e "${YELLOW}==================================================${NC}"

# 检查Nginx配置文件位置
echo -e "${YELLOW}查找Nginx站点配置文件...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"find /etc/nginx -name '*.conf' -type f | xargs grep -l zujuanwang\""

# 备份现有配置
echo -e "${YELLOW}备份现有Nginx配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cp /etc/nginx/sites-enabled/* /etc/nginx/sites-enabled/backup_\$(date +%Y%m%d%H%M%S).conf 2>/dev/null || cp /etc/nginx/conf.d/* /etc/nginx/conf.d/backup_\$(date +%Y%m%d%H%M%S).conf 2>/dev/null\""

# 创建新的配置文件内容
echo -e "${YELLOW}创建更新的Nginx配置...${NC}"
cat << EOF > /tmp/updated_nginx.conf
server {
    listen 80;
    server_name 120.26.12.100;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 禁用代理缓存
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }

    location /static {
        alias /var/www/question_bank/static;
        
        # 添加缓存控制头，禁用浏览器缓存
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        expires -1;
    }

    location /uploads {
        alias /var/www/question_bank/static/uploads;
    }

    # 添加全局缓存控制
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";

    client_max_body_size 50M;
}
EOF

# 上传新的配置文件到服务器
echo -e "${YELLOW}上传新的Nginx配置到服务器...${NC}"
sshpass -p "${REMOTE_PASSWORD}" scp /tmp/updated_nginx.conf ${REMOTE_USER}@${REMOTE_SERVER}:/tmp/updated_nginx.conf

# 替换服务器上的配置文件
echo -e "${YELLOW}更新服务器上的Nginx配置...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cp /tmp/updated_nginx.conf /etc/nginx/sites-enabled/default 2>/dev/null || cp /tmp/updated_nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null\""

# 检查Nginx配置语法
echo -e "${YELLOW}检查Nginx配置语法...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"nginx -t\""

# 重启Nginx
echo -e "${YELLOW}重启Nginx服务...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart nginx\""

# 检查目录权限
echo -e "${YELLOW}检查目录权限...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ls -la ${REMOTE_DIR}/static\""

# 查看Gunicorn配置并手动启动
echo -e "${YELLOW}启动应用程序...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"cd ${REMOTE_DIR} && pkill -f 'gunicorn' && cd ${REMOTE_DIR} && nohup python3 -m gunicorn -w 4 -b 127.0.0.1:5000 app:app > app.log 2>&1 &\""

# 检查进程
echo -e "${YELLOW}验证应用程序是否启动...${NC}"
eval "${SSH_CMD} ${REMOTE_USER}@${REMOTE_SERVER} \"ps aux | grep -i 'gunicorn\\|python' | grep -v grep\""

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       Nginx配置修复完成!                       ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "请现在尝试访问网站：http://${REMOTE_SERVER}/"
echo -e "如果网站仍然无法访问，请查看：${YELLOW}http://${REMOTE_SERVER}/static/${NC} 测试静态文件访问"
