#!/bin/bash

# Set variables
SERVER_IP="120.26.12.100"
SERVER_USER="root"
SERVER_PASSWORD="85497652Sl."
SERVER_PATH="/var/www/zujuanwang"
LOCAL_PATH=$(pwd)

# Check if expect is installed
if ! command -v expect &> /dev/null; then
    echo "The 'expect' command is not installed. Please install it or use one of the other deployment scripts."
    echo "On macOS: brew install expect"
    echo "On Ubuntu/Debian: sudo apt-get install expect"
    exit 1
fi

# Create expect script for deployment
cat > deploy/deploy_with_expect.exp << EOL
#!/usr/bin/expect -f

# Set timeout
set timeout 600

# Variables
set server "$SERVER_IP"
set username "$SERVER_USER"
set password "$SERVER_PASSWORD"
set remote_path "$SERVER_PATH"

# Create remote directory
spawn ssh -o StrictHostKeyChecking=no \$username@\$server "mkdir -p \$remote_path"
expect "password:"
send "\$password\r"
expect eof

# Create temporary directory on remote server
spawn ssh -o StrictHostKeyChecking=no \$username@\$server "mkdir -p /tmp/zujuanwang_deploy"
expect "password:"
send "\$password\r"
expect eof

# Copy files to remote server
puts "Copying project files to server..."
spawn scp -r * \$username@\$server:/tmp/zujuanwang_deploy/
expect "password:"
send "\$password\r"
expect eof

# Move files to destination and set up
puts "Setting up application on server..."
spawn ssh -o StrictHostKeyChecking=no \$username@\$server
expect "password:"
send "\$password\r"
expect "\\\$"
send "cp -r /tmp/zujuanwang_deploy/* \$remote_path/\r"
expect "\\\$"
send "rm -rf /tmp/zujuanwang_deploy\r"
expect "\\\$"

# Create setup script on server
send "cat > /tmp/setup.sh << 'EOSCRIPT'\r"
send "#!/bin/bash\r"
send "# Update package lists and install dependencies\r"
send "apt-get update\r"
send "apt-get install -y python3-pip python3-venv nginx\r"
send "\r"
send "# Create a virtual environment if it doesn't exist\r"
send "if [ ! -d \"\$remote_path/venv\" ]; then\r"
send "    python3 -m venv \$remote_path/venv\r"
send "    echo \"Created new virtual environment\"\r"
send "fi\r"
send "\r"
send "# Activate virtual environment and install requirements\r"
send "source \$remote_path/venv/bin/activate\r"
send "pip install --upgrade pip\r"
send "pip install -r \$remote_path/requirements.txt\r"
send "\r"
send "# Set up Nginx configuration\r"
send "cp \$remote_path/nginx.conf /etc/nginx/sites-available/zujuanwang\r"
send "ln -sf /etc/nginx/sites-available/zujuanwang /etc/nginx/sites-enabled/\r"
send "rm -f /etc/nginx/sites-enabled/default\r"
send "\r"
send "# Set up systemd service\r"
send "cp \$remote_path/zujuanwang.service /etc/systemd/system/\r"
send "\r"
send "# Create uploads directory if it doesn't exist\r"
send "mkdir -p \$remote_path/uploads\r"
send "chmod 755 \$remote_path/uploads\r"
send "\r"
send "# Reload systemd, enable and start services\r"
send "systemctl daemon-reload\r"
send "systemctl enable zujuanwang\r"
send "systemctl restart zujuanwang\r"
send "systemctl restart nginx\r"
send "\r"
send "echo \"Deployment completed successfully!\"\r"
send "echo \"Application should be running at http://$SERVER_IP\"\r"
send "EOSCRIPT\r"
expect "\\\$"

# Run setup script
send "chmod +x /tmp/setup.sh\r"
expect "\\\$"
send "bash /tmp/setup.sh\r"
expect "\\\$"
send "rm /tmp/setup.sh\r"
expect "\\\$"
send "exit\r"
expect eof

puts "Deployment completed successfully!"
EOL

# Make the expect script executable
chmod +x deploy/deploy_with_expect.exp

# Run the expect script
echo "Starting deployment with expect..."
./deploy/deploy_with_expect.exp

echo "Deployment process completed." 