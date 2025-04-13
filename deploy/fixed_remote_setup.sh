#!/bin/bash

# Check if directory exists, if not create it
if [ ! -d "/var/www/zujuanwang" ]; then
    mkdir -p /var/www/zujuanwang
    echo "Created directory: /var/www/zujuanwang"
fi

# Update package lists and install dependencies
apt-get update
apt-get install -y python3-pip python3-venv python3-full nginx

# Make sure the venv directory is removed to create a fresh one
rm -rf /var/www/zujuanwang/venv

# Create a fresh virtual environment
python3 -m venv /var/www/zujuanwang/venv
echo "Created new virtual environment"

# Activate virtual environment and install requirements
/var/www/zujuanwang/venv/bin/pip install --upgrade pip
/var/www/zujuanwang/venv/bin/pip install -r /var/www/zujuanwang/requirements.txt

# Set up Nginx configuration
cp /var/www/zujuanwang/nginx.conf /etc/nginx/sites-available/zujuanwang
ln -sf /etc/nginx/sites-available/zujuanwang /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Set up systemd service
cp /var/www/zujuanwang/zujuanwang.service /etc/systemd/system/

# Create uploads directory if it doesn't exist
mkdir -p /var/www/zujuanwang/uploads
chmod 755 /var/www/zujuanwang/uploads

# Reload systemd, enable and start services
systemctl daemon-reload
systemctl enable zujuanwang
systemctl restart zujuanwang
systemctl restart nginx

echo "Deployment completed successfully!"
echo "Application should be running at http://$SERVER_IP"
