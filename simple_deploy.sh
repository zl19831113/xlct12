#!/bin/bash

# Simple deployment script - Skip only upload folder
# Created: 2025-03-28

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
LOCAL_DIR="/Users/sl19831113/Desktop/未命名文件夹/zujuanwang75"
REMOTE_SERVER="120.26.12.100"
REMOTE_USER="root" 
REMOTE_DIR="/var/www/question_bank"

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      SIMPLE DEPLOY - SKIP UPLOAD FOLDER          ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "Local path: ${LOCAL_DIR}"
echo -e "Remote path: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# Compress compression for faster transfer and exclude only upload folder
echo -e "${YELLOW}Uploading files (skipping upload folder)...${NC}"
rsync -avz --compress --progress \
  --exclude="upload" \
  --exclude="upload/*" \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  --exclude=".git" \
  --exclude=".DS_Store" \
  --exclude="deploy_*.sh" \
  "${LOCAL_DIR}/" "${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/"

if [ $? -ne 0 ]; then
    echo -e "${RED}Upload failed. Check your connection and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}       Deployment completed successfully!         ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "All files except upload folder have been transferred."
echo -e ""
echo -e "To restart the server application, run:"
echo -e "  ssh ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart gunicorn\""
