#!/bin/bash

# Fast deployment script - Only uploads essential files
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

# Files to skip (large data files that don't need updating)
SKIP_LARGE_FILES=(
    "instance/questions.db"
    "instance/questions.db-journal"
    "*.pyc"
    "__pycache__"
    ".git"
    ".DS_Store"
    "backup_*"
    "deploy_*.sh"
)

# Recent modifications only - files changed within last X days
RECENT_DAYS=7

echo -e "${YELLOW}==================================================${NC}"
echo -e "${YELLOW}      FAST DEPLOY - RECENT CHANGES ONLY           ${NC}"
echo -e "${YELLOW}==================================================${NC}"
echo -e "Local path: ${LOCAL_DIR}"
echo -e "Remote path: ${REMOTE_SERVER}:${REMOTE_DIR}"
echo -e "Only sending files changed in the last ${RECENT_DAYS} days"
echo -e "${YELLOW}--------------------------------------------------${NC}"

# Create exclusion pattern for rsync
EXCLUDE_OPTIONS=""
for pattern in "${SKIP_LARGE_FILES[@]}"; do
    EXCLUDE_OPTIONS="${EXCLUDE_OPTIONS} --exclude='${pattern}'"
done

# Option 1: Create a compressed archive of only changed files
echo -e "${YELLOW}[Option 1] Creating compressed archive of recent changes...${NC}"
TEMP_ARCHIVE="/tmp/zujuanwang_changes.tar.gz"

# Find only recently modified files
find "${LOCAL_DIR}" -type f -mtime -${RECENT_DAYS} | grep -v -E "$(echo "${SKIP_LARGE_FILES[@]}" | tr ' ' '|')" > /tmp/changed_files.txt

# Count files to transfer
FILE_COUNT=$(wc -l < /tmp/changed_files.txt)
echo -e "Found ${FILE_COUNT} recently modified files to transfer"

# Create archive with only those files
echo -e "Creating compressed archive..."
tar -czf "${TEMP_ARCHIVE}" -T /tmp/changed_files.txt --transform="s|${LOCAL_DIR}|.|"

# Upload the archive
echo -e "${YELLOW}Uploading compressed archive (much faster)...${NC}"
scp "${TEMP_ARCHIVE}" "${REMOTE_USER}@${REMOTE_SERVER}:/tmp/"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error uploading archive. Check connection and try again.${NC}"
    exit 1
fi

# Extract on server
echo -e "${YELLOW}Extracting files on server...${NC}"
ssh "${REMOTE_USER}@${REMOTE_SERVER}" "cd ${REMOTE_DIR} && tar -xzf /tmp/zujuanwang_changes.tar.gz && rm /tmp/zujuanwang_changes.tar.gz"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error extracting files on server.${NC}"
    exit 1
fi

# Clean up
rm "${TEMP_ARCHIVE}" /tmp/changed_files.txt

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}     Fast deployment completed successfully!      ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "Only modified files were transferred to save time."
echo -e "If you need to restart the application, run:"
echo -e "  ssh ${REMOTE_USER}@${REMOTE_SERVER} \"systemctl restart gunicorn\""

echo -e "${YELLOW}--------------------------------------------------${NC}"
echo -e "If this doesn't work, try Option 2 in the script:"
echo -e "Uncomment and run the manual rsync command below:"
echo -e "rsync -avz --compress --progress ${EXCLUDE_OPTIONS} \"${LOCAL_DIR}/\" \"${REMOTE_USER}@${REMOTE_SERVER}:${REMOTE_DIR}/\""
