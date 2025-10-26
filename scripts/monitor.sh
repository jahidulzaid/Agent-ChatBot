#!/bin/bash
# Monitoring script for Agentic RAG Chatbot

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Agentic RAG Chatbot - System Status    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker Compose is running
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose not found${NC}"
    exit 1
fi

# Container Status
echo -e "${YELLOW}=== Container Status ===${NC}"
docker-compose ps
echo ""

# Resource Usage
echo -e "${YELLOW}=== Resource Usage ===${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

# Backend Health Check
echo -e "${YELLOW}=== Backend Health ===${NC}"
BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
    echo "$BACKEND_HEALTH" | jq '.' 2>/dev/null || echo "$BACKEND_HEALTH"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
fi
echo ""

# Frontend Health Check
echo -e "${YELLOW}=== Frontend Health ===${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is healthy (HTTP $FRONTEND_STATUS)${NC}"
else
    echo -e "${RED}✗ Frontend returned HTTP $FRONTEND_STATUS${NC}"
fi
echo ""

# Recent Backend Logs
echo -e "${YELLOW}=== Recent Backend Logs (last 10 lines) ===${NC}"
docker-compose logs --tail=10 backend 2>/dev/null || echo "No logs available"
echo ""

# Disk Usage
echo -e "${YELLOW}=== Disk Usage ===${NC}"
df -h | grep -E '^Filesystem|/$' || df -h | head -2
echo ""

# Data Directory Size
echo -e "${YELLOW}=== Data Directory Size ===${NC}"
if [ -d "./backend/data" ]; then
    du -sh ./backend/data/* 2>/dev/null || echo "No data yet"
else
    echo "Data directory not found"
fi
echo ""

# Network Connectivity
echo -e "${YELLOW}=== Network Connectivity ===${NC}"
BACKEND_PORT=$(docker-compose port backend 8000 2>/dev/null | cut -d: -f2)
FRONTEND_PORT=$(docker-compose port frontend 3000 2>/dev/null | cut -d: -f2)
echo "Backend Port: ${BACKEND_PORT:-not exposed}"
echo "Frontend Port: ${FRONTEND_PORT:-not exposed}"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              System Summary                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

ISSUES=0

# Check containers
RUNNING_CONTAINERS=$(docker-compose ps --services --filter "status=running" | wc -l)
TOTAL_CONTAINERS=$(docker-compose ps --services | wc -l)

if [ "$RUNNING_CONTAINERS" -eq "$TOTAL_CONTAINERS" ]; then
    echo -e "${GREEN}✓ All containers running ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)${NC}"
else
    echo -e "${RED}✗ Some containers are down ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)${NC}"
    ((ISSUES++))
fi

# Check backend health
if [ $? -eq 0 ] && echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    ((ISSUES++))
fi

# Check frontend
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
    ((ISSUES++))
fi

echo ""
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 All systems operational!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Found $ISSUES issue(s)${NC}"
    echo -e "${YELLOW}Run 'docker-compose logs -f' for detailed logs${NC}"
    exit 1
fi
