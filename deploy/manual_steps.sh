#!/bin/bash
# This file contains the manual steps to deploy the application.
# Execute each command one by one.

# 1. Create the directory on the server
ssh root@120.26.12.100 "mkdir -p /var/www/zujuanwang"

# 2. Copy the archive to the server
scp /tmp/zujuanwang_deploy/zujuanwang.tar.gz root@120.26.12.100:/var/www/zujuanwang/

# 3. Connect to the server
ssh root@120.26.12.100

# 4. Once logged in to the server, run these commands:
cd /var/www/zujuanwang
tar -xzf zujuanwang.tar.gz
rm zujuanwang.tar.gz  # Optional

# 5. Install dependencies
apt-get update
apt-get install -y python3-pip python3-venv nginx

# 6. Set up Python environment
python3 -m venv /var/www/zujuanwang/venv
source /var/www/zujuanwang/venv/bin/activate
pip install --upgrade pip
pip install -r /var/www/zujuanwang/requirements.txt

# 7. Set up Nginx
cp /var/www/zujuanwang/nginx.conf /etc/nginx/sites-available/zujuanwang
ln -sf /etc/nginx/sites-available/zujuanwang /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 8. Set up systemd service
cp /var/www/zujuanwang/zujuanwang.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable zujuanwang
systemctl start zujuanwang

# 9. Create uploads directory
mkdir -p /var/www/zujuanwang/uploads
chmod 755 /var/www/zujuanwang/uploads

# 10. Verify the application is running
systemctl status zujuanwang 