#!/bin/bash

# Set variables
SERVER_IP="120.26.12.100"
SERVER_USER="root"
SERVER_PASSWORD="85497652Sl."
SERVER_PATH="/var/www/zujuanwang"
LOCAL_PATH=$(pwd)

# Display message
echo "Beginning deployment to $SERVER_USER@$SERVER_IP:$SERVER_PATH"

# Create a temporary directory for deployment files
TEMP_DIR="deploy/temp"
mkdir -p "$TEMP_DIR"

# Create the remote setup script
cat > "$TEMP_DIR/remote_setup.sh" << 'EOL'
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

chmod +x "$TEMP_DIR/remote_setup.sh"

# Create an Archive of the Project
echo "Creating archive of the project..."
tar -czf "$TEMP_DIR/zujuanwang.tar.gz" --exclude="venv" --exclude="__pycache__" --exclude=".DS_Store" --exclude="deploy/temp" -C "$LOCAL_PATH" .

# SSH command with password
echo "Deploying to server..."
echo "Note: You will be prompted for the server password multiple times"

# Create SSH_ASKPASS script to provide password
cat > "$TEMP_DIR/ssh_askpass.sh" << EOL
#!/bin/bash
echo "$SERVER_PASSWORD"
EOL
chmod +x "$TEMP_DIR/ssh_askpass.sh"

# Use SSH_ASKPASS for non-interactive password input
export SSH_ASKPASS="$TEMP_DIR/ssh_askpass.sh"
export DISPLAY=:0

# Create directory on remote server if it doesn't exist
echo "Creating remote directory..."
setsid -w ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "mkdir -p $SERVER_PATH"

# Copy archive to remote server
echo "Copying files to server..."
setsid -w scp -o StrictHostKeyChecking=no "$TEMP_DIR/zujuanwang.tar.gz" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/"
setsid -w scp -o StrictHostKeyChecking=no "$TEMP_DIR/remote_setup.sh" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/"

# Extract archive and run setup script on server
echo "Extracting files and setting up server..."
setsid -w ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "cd $SERVER_PATH && tar -xzf zujuanwang.tar.gz && bash remote_setup.sh"

# Clean up temporary files
rm -rf "$TEMP_DIR"

echo "Deployment process completed."
echo "Note: If you encountered password prompts that didn't work, you may need to use the manual method."
echo "Manual deployment steps:"
echo "1. scp -r ./* $SERVER_USER@$SERVER_IP:$SERVER_PATH/"
echo "2. ssh $SERVER_USER@$SERVER_IP"
echo "3. cd $SERVER_PATH && bash deploy/remote_setup.sh" 