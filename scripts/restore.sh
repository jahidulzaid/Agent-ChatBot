#!/bin/bash
# Restore script for Agentic RAG Chatbot

set -e

# Configuration
CONTAINER_NAME="chatbot-backend"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: ./restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/chatbot_backup_*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will replace all current data!${NC}"
echo -e "Backup file: $BACKUP_FILE"
echo -n "Continue? (yes/no): "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

echo -e "${GREEN}Starting restore process...${NC}"

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
docker-compose down

# Start backend container
echo -e "${YELLOW}Starting backend container...${NC}"
docker-compose up -d backend

# Wait for container to be ready
sleep 5

# Copy backup to container
echo -e "${YELLOW}Copying backup to container...${NC}"
docker cp $BACKUP_FILE $CONTAINER_NAME:/tmp/backup.tar.gz

# Extract backup
echo -e "${YELLOW}Extracting backup...${NC}"
docker exec $CONTAINER_NAME tar -xzf /tmp/backup.tar.gz -C / 2>/dev/null || true

# Cleanup temporary file
docker exec $CONTAINER_NAME rm /tmp/backup.tar.gz

# Restart all services
echo -e "${YELLOW}Restarting all services...${NC}"
docker-compose restart

# Wait for services to be ready
sleep 10

# Check health
echo -e "${YELLOW}Checking service health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health || echo "failed")

if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Restore completed successfully!${NC}"
    echo -e "  Services are healthy and running"
else
    echo -e "${RED}⚠️  Restore completed but health check failed${NC}"
    echo -e "  Please check logs: docker-compose logs -f"
fi
