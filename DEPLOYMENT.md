# 🚀 Deployment Guide - Agentic RAG Chatbot

Complete guide for deploying your chatbot to production with Docker, cloud platforms, and CI/CD.

## 📋 Table of Contents

1. [Local Docker Setup](#local-docker-setup)
2. [Production Deployment Options](#production-deployment-options)
3. [Platform-Specific Guides](#platform-specific-guides)
4. [CI/CD Setup](#cicd-setup)
5. [Domain & SSL Configuration](#domain--ssl-configuration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🐳 Local Docker Setup

### Prerequisites
- Docker Desktop installed
- Docker Compose installed
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jahidulzaid/Agent-ChatBot.git
   cd Agent-ChatBot
   ```

2. **Configure environment variables**
   ```bash
   # Copy example env file
   cp .env.example backend/.env
   
   # Edit with your API key
   nano backend/.env  # or use your preferred editor
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Build images
   docker-compose build
   
   # Start services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Stop services**
   ```bash
   docker-compose down
   
   # Stop and remove volumes (caution: deletes data)
   docker-compose down -v
   ```

### Docker Commands Reference

```bash
# Rebuild after code changes
docker-compose build --no-cache

# View running containers
docker-compose ps

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Restart specific service
docker-compose restart backend

# Update and restart
docker-compose pull
docker-compose up -d
```

---

## 🌐 Production Deployment Options

### Option 1: Railway (Recommended for Beginners) ⭐

**Pros:** Easy setup, automatic HTTPS, good free tier, PostgreSQL support
**Cost:** Free tier available, ~$5/month for production

#### Backend Deployment on Railway

1. **Create Railway account** at https://railway.app

2. **Create new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select `Agent-ChatBot` repository

3. **Configure Backend Service**
   ```bash
   # In Railway dashboard:
   # 1. Click "Add Service" → "GitHub Repo"
   # 2. Select your repo
   # 3. Set Root Directory: backend
   # 4. Railway auto-detects Python
   ```

4. **Add Environment Variables**
   ```
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=https://your-frontend-url.railway.app
   DEBUG=False
   ```

5. **Configure Start Command** (if not auto-detected)
   ```bash
   python main.py
   ```

6. **Add Persistent Volume**
   - Go to Settings → Volumes
   - Add volume: `/app/data`

7. **Deploy**
   - Railway auto-deploys on push
   - Get your backend URL: `https://your-app.up.railway.app`

#### Frontend Deployment on Railway

1. **Add new service** in same project

2. **Configure Frontend Service**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Start Command: `serve -s dist -p 3000`

3. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

4. **Install serve** (add to package.json)
   ```json
   {
     "scripts": {
       "start": "serve -s dist -p 3000"
     },
     "dependencies": {
       "serve": "^14.2.0"
     }
   }
   ```

---

### Option 2: Render (Free Tier Available)

**Pros:** Free tier, easy setup, automatic SSL
**Cost:** Free (with limitations), $7/month for paid

#### Backend on Render

1. **Go to** https://render.com

2. **Create Web Service**
   - Connect GitHub repository
   - Select `backend` folder
   - Name: `chatbot-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

3. **Environment Variables**
   ```
   OPENROUTER_API_KEY=your_key
   CORS_ORIGINS=https://your-frontend.onrender.com
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. **Add Persistent Disk**
   - Go to Settings → Disks
   - Mount Path: `/app/data`
   - Size: 1GB (free tier)

#### Frontend on Render

1. **Create Static Site**
   - Select repository
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`

2. **Environment Variables**
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

---

### Option 3: AWS (Production Grade)

**Pros:** Full control, scalable, enterprise-ready
**Cost:** ~$20-50/month

#### Using AWS ECS (Elastic Container Service)

1. **Install AWS CLI**
   ```bash
   # Install AWS CLI
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Configure
   aws configure
   ```

2. **Create ECR Repositories**
   ```bash
   # Create repositories for images
   aws ecr create-repository --repository-name chatbot-backend
   aws ecr create-repository --repository-name chatbot-frontend
   ```

3. **Build and Push Docker Images**
   ```bash
   # Get ECR login
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag backend
   docker build -t chatbot-backend ./backend
   docker tag chatbot-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   
   # Build and tag frontend
   docker build -t chatbot-frontend ./frontend
   docker tag chatbot-frontend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-frontend:latest
   ```

4. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name chatbot-cluster
   ```

5. **Create Task Definitions**
   - Use AWS Console or CLI
   - Configure CPU, memory, environment variables
   - Add persistent storage (EFS)

6. **Create Services**
   - Create Application Load Balancer
   - Create ECS services
   - Configure auto-scaling

---

### Option 4: DigitalOcean (Balanced)

**Pros:** Good balance of simplicity and control, excellent docs
**Cost:** ~$12-24/month

1. **Create Droplet**
   - Choose Docker on Ubuntu
   - Size: 2GB RAM minimum
   - Add SSH key

2. **Connect via SSH**
   ```bash
   ssh root@your_droplet_ip
   ```

3. **Clone and Setup**
   ```bash
   git clone https://github.com/jahidulzaid/Agent-ChatBot.git
   cd Agent-ChatBot
   
   # Copy and edit .env
   cp .env.example backend/.env
   nano backend/.env
   ```

4. **Install Docker Compose**
   ```bash
   curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   ```

5. **Deploy**
   ```bash
   docker-compose up -d
   ```

6. **Configure Nginx Reverse Proxy**
   ```bash
   apt install nginx
   nano /etc/nginx/sites-available/chatbot
   ```
   
   Add configuration:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }

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

7. **Enable site and restart**
   ```bash
   ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

---

## 🔄 CI/CD Setup

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run backend tests
        run: |
          cd backend
          pytest tests/ || echo "No tests found"
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build frontend
        run: |
          cd frontend
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: |
          # Railway auto-deploys on push
          echo "Railway will auto-deploy"
      
      # Or deploy to your own server
      - name: Deploy to Server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /path/to/Agent-ChatBot
            git pull
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
```

### Set GitHub Secrets

Go to Settings → Secrets and add:
- `SERVER_HOST`
- `SERVER_USER`
- `SSH_PRIVATE_KEY`
- `OPENROUTER_API_KEY`

---

## 🔒 Domain & SSL Configuration

### Using Cloudflare (Recommended)

1. **Add your domain to Cloudflare**

2. **Update DNS records**
   ```
   Type  Name  Content                 Proxy
   A     @     your_server_ip          ✓ Proxied
   A     www   your_server_ip          ✓ Proxied
   ```

3. **SSL/TLS Settings**
   - SSL/TLS → Overview → Full (strict)
   - Edge Certificates → Always Use HTTPS: On

### Using Certbot (Let's Encrypt)

```bash
# Install certbot
apt install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

---

## 📊 Monitoring & Maintenance

### Health Checks

Both services have health check endpoints:
- Backend: `http://your-domain.com:8000/health`
- Frontend: `http://your-domain.com:3000`

### Logging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Save logs to file
docker-compose logs > logs.txt
```

### Database Backup

```bash
# Backup ChromaDB data
docker-compose exec backend tar -czf /app/backup.tar.gz /app/data
docker cp chatbot-backend:/app/backup.tar.gz ./backup.tar.gz

# Restore
docker cp ./backup.tar.gz chatbot-backend:/app/backup.tar.gz
docker-compose exec backend tar -xzf /app/backup.tar.gz -C /
```

### Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Check status
docker-compose ps
```

### Performance Monitoring

Add to `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - chatbot-network

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    networks:
      - chatbot-network
```

---

## 🎯 Complete Deployment Checklist

### Pre-Deployment
- [ ] Test application locally
- [ ] Review and update environment variables
- [ ] Test Docker build locally
- [ ] Review security settings
- [ ] Prepare backup strategy

### Deployment
- [ ] Choose hosting platform
- [ ] Configure domain (if applicable)
- [ ] Set up SSL certificates
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Configure environment variables
- [ ] Set up persistent storage

### Post-Deployment
- [ ] Test all endpoints
- [ ] Verify frontend-backend communication
- [ ] Test document upload
- [ ] Test RAG functionality
- [ ] Set up monitoring
- [ ] Configure automatic backups
- [ ] Set up CI/CD pipeline
- [ ] Document any custom configurations

### Ongoing Maintenance
- [ ] Monitor error logs
- [ ] Review performance metrics
- [ ] Apply security updates
- [ ] Backup database regularly
- [ ] Update dependencies monthly
- [ ] Review and optimize costs

---

## 📞 Support & Resources

- **GitHub Issues**: https://github.com/jahidulzaid/Agent-ChatBot/issues
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Docker Docs**: https://docs.docker.com
- **AWS ECS Docs**: https://docs.aws.amazon.com/ecs

---

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep OPENROUTER

# Rebuild
docker-compose build --no-cache backend
```

**Frontend can't connect to backend:**
- Check CORS settings in backend/.env
- Verify VITE_API_URL in frontend
- Check network connectivity

**Out of memory:**
- Increase Docker memory limits
- Upgrade server plan
- Optimize model loading

**Database issues:**
- Check volume mounts
- Verify permissions
- Clear and reinitialize if needed

---

## 🎉 You're All Set!

Your Agentic RAG Chatbot is now ready for production! Choose your deployment platform, follow the guide, and your chatbot will be live in no time.

**Happy Deploying! 🚀**
