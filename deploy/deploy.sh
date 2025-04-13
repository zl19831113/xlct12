#!/bin/bash

# Set variables
SERVER_IP="120.26.12.100"
SERVER_USER="root"
SERVER_PASSWORD="85497652Sl."
SERVER_PATH="/var/www/zujuanwang"
LOCAL_PATH=$(pwd)

# Display message
echo "Beginning deployment to $SERVER_USER@$SERVER_IP:$SERVER_PATH"

# Create a temporary script to run on the remote server
cat > deploy/remote_setup.sh << 'EOL'
#!/bin/bash

# Check if directory exists, if not create it
if [ ! -d "/var/www/zujuanwang" ]; then
    mkdir -p /var/www/zujuanwang
    echo "Created directory: /var/www/zujuanwang"
fi

# Update package lists and install dependencies
apt-get update
apt-get install -y python3-pip python3-venv nginx

# Create a virtual environment if it doesn't exist
if [ ! -d "/var/www/zujuanwang/venv" ]; then
    python3 -m venv /var/www/zujuanwang/venv
    echo "Created new virtual environment"
fi

# Activate virtual environment and install requirements
source /var/www/zujuanwang/venv/bin/activate
pip install --upgrade pip
pip install -r /var/www/zujuanwang/requirements.txt

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
EOL

# Give execute permission to remote_setup.sh
chmod +x deploy/remote_setup.sh

# Check if sshpass is installed, if not try to install it
if ! command -v sshpass &> /dev/null; then
    echo "sshpass is not installed. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install sshpass
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y sshpass
    else
        echo "Could not install sshpass automatically. Please install it manually."
        exit 1
    fi
fi

# Use sshpass or manual alternative for rsync
if command -v sshpass &> /dev/null; then
    # Create an exclude file for rsync
    echo "venv/" > deploy/rsync_exclude.txt
    echo "__pycache__/" >> deploy/rsync_exclude.txt
    echo ".DS_Store" >> deploy/rsync_exclude.txt
    
    # Synchronize the project files with rsync
    sshpass -p "$SERVER_PASSWORD" rsync -avz --exclude-from=deploy/rsync_exclude.txt --delete "$LOCAL_PATH/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/"
    
    # Execute the remote setup script
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "bash $SERVER_PATH/deploy/remote_setup.sh"
else
    echo "sshpass is not available. You'll need to manually enter the password."
    echo "Synchronizing project files..."
    rsync -avz --exclude-from=deploy/rsync_exclude.txt --delete "$LOCAL_PATH/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/"
    
    echo "Executing remote setup script..."
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "bash $SERVER_PATH/deploy/remote_setup.sh"
fi

echo "Deployment process completed." 