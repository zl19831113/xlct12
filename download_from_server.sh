#!/bin/bash

# Script to download app.py from the server
# Created on: 2025-04-02

SERVER="120.26.12.100"
USER="root"
PASSWORD="85497652Sl."
REMOTE_DIR="/var/www/question_bank"
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang76"

# Create a backup of the local app.py if it exists
if [ -f "$LOCAL_DIR/app.py" ]; then
    TIMESTAMP=$(date +"%Y%m%d%H%M%S")
    cp "$LOCAL_DIR/app.py" "$LOCAL_DIR/app.py.bak_$TIMESTAMP"
    echo "Created backup of local app.py to app.py.bak_$TIMESTAMP"
fi

# Download app.py from the server
echo "Downloading app.py from server..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$USER@$SERVER:$REMOTE_DIR/app.py" "$LOCAL_DIR/app.py"

if [ $? -eq 0 ]; then
    echo "Successfully downloaded app.py from server"
    echo "You can now run the app with: python3 app.py"
else
    echo "Failed to download app.py from server"
    echo "Make sure sshpass is installed. If not, install it with: brew install hudochenkov/sshpass/sshpass"
fi

# Check if xlct12.db exists locally, if not, download it
if [ ! -f "$LOCAL_DIR/xlct12.db" ]; then
    echo "xlct12.db not found locally. Downloading from server..."
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$USER@$SERVER:$REMOTE_DIR/xlct12.db" "$LOCAL_DIR/xlct12.db"
    
    if [ $? -eq 0 ]; then
        echo "Successfully downloaded xlct12.db from server"
    else
        echo "Failed to download xlct12.db from server"
    fi
fi

echo "Done!"
