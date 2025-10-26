#!/bin/bash
# Backup script for Agentic RAG Chatbot

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="chatbot_backup_$DATE.tar.gz"
CONTAINER_NAME="chatbot-backend"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backup process...${NC}"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Check if container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${RED}Error: Container $CONTAINER_NAME is not running${NC}"
    exit 1
fi

# Backup ChromaDB data
echo -e "${YELLOW}Backing up ChromaDB data...${NC}"
docker exec $CONTAINER_NAME tar -czf /tmp/data_backup.tar.gz /app/data 2>/dev/null || true

# Copy to host
echo -e "${YELLOW}Copying backup to host...${NC}"
docker cp $CONTAINER_NAME:/tmp/data_backup.tar.gz $BACKUP_DIR/$BACKUP_FILE

# Cleanup temporary file in container
docker exec $CONTAINER_NAME rm /tmp/data_backup.tar.gz

# Get backup size
BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)

echo -e "${GREEN}✓ Backup created successfully!${NC}"
echo -e "  File: $BACKUP_DIR/$BACKUP_FILE"
echo -e "  Size: $BACKUP_SIZE"

# Optional: Keep only last 7 backups
echo -e "${YELLOW}Cleaning old backups (keeping last 7)...${NC}"
cd $BACKUP_DIR
ls -t chatbot_backup_*.tar.gz | tail -n +8 | xargs -r rm
cd ..

# Optional: Upload to S3 (uncomment if using AWS)
# echo -e "${YELLOW}Uploading to S3...${NC}"
# aws s3 cp $BACKUP_DIR/$BACKUP_FILE s3://your-bucket/backups/ --storage-class STANDARD_IA

echo -e "${GREEN}Backup process completed!${NC}"
