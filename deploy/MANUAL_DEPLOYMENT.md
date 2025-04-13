# Manual Deployment Guide

This guide provides step-by-step instructions for manually deploying the zujuanwang application to a server.

## Server Information
- Server IP: 120.26.12.100
- Username: root
- Password: 85497652Sl.
- Target Path: /var/www/zujuanwang

## Prerequisites
Before proceeding, ensure you have SSH access to the server.

## Deployment Steps

### 1. Create a local archive of the project

```bash
# From your local project directory
tar -czf zujuanwang.tar.gz --exclude="venv" --exclude="__pycache__" --exclude=".DS_Store" --exclude="deploy/temp" .
```

### 2. Copy the archive to the server

```bash
# Create the target directory on the server
ssh root@120.26.12.100 "mkdir -p /var/www/zujuanwang"

# Copy the archive
scp zujuanwang.tar.gz root@120.26.12.100:/var/www/zujuanwang/
```

### 3. Extract the archive on the server

```bash
ssh root@120.26.12.100
cd /var/www/zujuanwang
tar -xzf zujuanwang.tar.gz
rm zujuanwang.tar.gz  # Optional cleanup
```

### 4. Install dependencies on the server

```bash
# Update package lists
apt-get update

# Install Python, pip, virtual environment, and Nginx
apt-get install -y python3-pip python3-venv nginx
```

### 5. Set up Python environment

```bash
# Create and activate virtual environment
python3 -m venv /var/www/zujuanwang/venv
source /var/www/zujuanwang/venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r /var/www/zujuanwang/requirements.txt
```

### 6. Set up Nginx

```bash
# Copy the Nginx configuration
cp /var/www/zujuanwang/nginx.conf /etc/nginx/sites-available/zujuanwang

# Create symbolic link and remove default site if needed
ln -sf /etc/nginx/sites-available/zujuanwang /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx
```

### 7. Set up systemd service

```bash
# Copy the service file
cp /var/www/zujuanwang/zujuanwang.service /etc/systemd/system/

# Reload daemon, enable and start service
systemctl daemon-reload
systemctl enable zujuanwang
systemctl start zujuanwang
```

### 8. Create uploads directory

```bash
mkdir -p /var/www/zujuanwang/uploads
chmod 755 /var/www/zujuanwang/uploads
```

### 9. Verify the deployment

Check if the application is running:
```bash
systemctl status zujuanwang
```

Check Nginx status:
```bash
systemctl status nginx
```

Check logs for any errors:
```bash
journalctl -u zujuanwang -n 50
```

### 10. Access the application

The application should now be accessible at: http://120.26.12.100

## Troubleshooting

### If the service fails to start
Check the logs:
```bash
journalctl -u zujuanwang -e
```

### If Nginx returns a 502 Bad Gateway
The Flask application might not be running. Check:
```bash
ps aux | grep gunicorn
```

### If static files or uploads don't load
Check Nginx configuration and permissions:
```bash
nginx -t
ls -la /var/www/zujuanwang/static
ls -la /var/www/zujuanwang/uploads
```

### If there are database issues
Check if the SQLite database exists and has proper permissions:
```bash
ls -la /var/www/zujuanwang/questions.db
chmod 644 /var/www/zujuanwang/questions.db
```

## Updating the Application

To update the application after making changes:

1. Transfer the updated files to the server 
2. Restart the service: `systemctl restart zujuanwang` 