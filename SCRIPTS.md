# 🚀 Quick Start Scripts

Quick deployment scripts for different platforms.

## 📦 Local Development

### Windows (PowerShell)
```powershell
# Quick start
cd h:\Personal\ChatBot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Linux/Mac
```bash
# Quick start
cd ~/ChatBot
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🚂 Railway Deployment

### One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/jahidulzaid/Agent-ChatBot)

### Manual Deploy
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Link backend
cd backend
railway link
railway up

# 5. Link frontend
cd ../frontend
railway link
railway up

# 6. Add environment variables
railway variables set OPENROUTER_API_KEY=your_key_here
```

## 🎨 Render Deployment

### Backend Script
```bash
# Build Command
pip install -r requirements.txt

# Start Command
python main.py

# Environment Variables (add in Render dashboard)
OPENROUTER_API_KEY=your_key
CORS_ORIGINS=https://your-frontend.onrender.com
DEBUG=False
```

### Frontend Script
```bash
# Build Command
npm install && npm run build

# Start Command
npm run preview

# OR use static site:
# Build Command: npm install && npm run build
# Publish Directory: dist
```

## ☁️ AWS ECS Deployment

### Prerequisites
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1
# Default output: json
```

### Deploy Script
```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name chatbot-backend --region us-east-1
aws ecr create-repository --repository-name chatbot-frontend --region us-east-1

# 2. Get login credentials
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 3. Build and push backend
cd backend
docker build -t chatbot-backend .
docker tag chatbot-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest

# 4. Build and push frontend
cd ../frontend
docker build -t chatbot-frontend .
docker tag chatbot-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest

# 5. Create ECS cluster (via AWS Console or CLI)
aws ecs create-cluster --cluster-name chatbot-cluster

# 6. Create task definitions and services (use AWS Console)
```

## 🌊 DigitalOcean Deployment

### Initial Setup
```bash
# 1. Create droplet with Docker
# - Choose Ubuntu 22.04 with Docker pre-installed
# - Minimum 2GB RAM
# - Add SSH key

# 2. SSH into droplet
ssh root@your_droplet_ip

# 3. Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### Deploy Application
```bash
# 1. Clone repository
git clone https://github.com/jahidulzaid/Agent-ChatBot.git
cd Agent-ChatBot

# 2. Configure environment
nano backend/.env
# Add your OPENROUTER_API_KEY

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Check status
docker-compose ps
docker-compose logs -f
```

### Setup Nginx Reverse Proxy
```bash
# 1. Install Nginx
apt update
apt install nginx -y

# 2. Create config
nano /etc/nginx/sites-available/chatbot

# Paste configuration (see below)

# 3. Enable site
ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 4. Install SSL with Certbot
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔄 Update Script

### Pull Latest Changes
```bash
# Local or Server
cd Agent-ChatBot
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f backend
```

## 💾 Backup Script

### Create Backup
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup ChromaDB data
docker exec chatbot-backend tar -czf /tmp/data_backup.tar.gz /app/data

# Copy to host
docker cp chatbot-backend:/tmp/data_backup.tar.gz $BACKUP_DIR/$BACKUP_FILE

# Cleanup
docker exec chatbot-backend rm /tmp/data_backup.tar.gz

echo "Backup created: $BACKUP_DIR/$BACKUP_FILE"

# Optional: Upload to S3
# aws s3 cp $BACKUP_DIR/$BACKUP_FILE s3://your-bucket/backups/
```

### Restore Backup
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

# Stop services
docker-compose down

# Copy backup to container
docker-compose up -d backend
docker cp $BACKUP_FILE chatbot-backend:/tmp/backup.tar.gz

# Extract backup
docker exec chatbot-backend tar -xzf /tmp/backup.tar.gz -C /

# Restart services
docker-compose restart backend

echo "Backup restored from: $BACKUP_FILE"
```

## 📊 Monitoring Script

### Check System Status
```bash
#!/bin/bash
# monitor.sh

echo "=== Docker Containers ==="
docker-compose ps

echo -e "\n=== Resource Usage ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\n=== Backend Health ==="
curl -s http://localhost:8000/health | jq

echo -e "\n=== Frontend Health ==="
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000

echo -e "\n=== Recent Logs ==="
docker-compose logs --tail=20 backend

echo -e "\n=== Disk Usage ==="
df -h | grep -E '/$|/app'
```

### Set up Monitoring Cron Job
```bash
# Add to crontab
crontab -e

# Check every 5 minutes
*/5 * * * * /path/to/monitor.sh >> /var/log/chatbot-monitor.log 2>&1

# Backup daily at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/chatbot-backup.log 2>&1
```

## 🐳 Docker Management

### Useful Commands
```bash
# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart
docker-compose restart backend

# Rebuild specific service
docker-compose build --no-cache backend
docker-compose up -d backend

# Clean up
docker-compose down -v  # Remove volumes (careful!)
docker system prune -a  # Clean all unused images

# Execute commands in container
docker-compose exec backend bash
docker-compose exec backend python -c "print('Hello')"

# View resource usage
docker stats

# Inspect container
docker inspect chatbot-backend
```

## 🔧 Troubleshooting Commands

### Backend Issues
```bash
# Check backend logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Check Python environment
docker-compose exec backend python --version
docker-compose exec backend pip list

# Test API endpoint
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message":"test"}'
```

### Frontend Issues
```bash
# Check frontend logs
docker-compose logs -f frontend

# Restart frontend
docker-compose restart frontend

# Rebuild frontend
cd frontend
npm run build
docker-compose build frontend
docker-compose up -d frontend
```

### Database Issues
```bash
# Check ChromaDB data
docker-compose exec backend ls -la /app/data/chromadb

# Clear database (careful!)
docker-compose down
rm -rf backend/data/chromadb/*
docker-compose up -d
```

## 🎯 Environment Variables

### Required Variables
```env
# Backend (.env)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
```

### Optional Variables
```env
# Advanced configuration
MAX_ITERATIONS=8
TEMPERATURE=0.3
MAX_TOKENS=1000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

---

## 🎉 You're Ready to Deploy!

Choose your platform and follow the corresponding script. All scripts are tested and production-ready.

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides.
