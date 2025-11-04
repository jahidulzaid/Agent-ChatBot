# Railway Deployment Guide for Agentic RAG Chatbot

## Why Railway?
- ✅ Handles heavy ML dependencies (no OOM errors)
- ✅ Persistent volume support for ChromaDB
- ✅ Easy GitHub integration
- ✅ Automatic HTTPS
- ✅ Better for ML/AI applications than Vercel

## Quick Deployment Steps

### 1. Backend Deployment

1. Go to [Railway](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select **Agent-ChatBot** repository
4. Railway will detect your Python backend automatically

### 2. Configure Backend Service

**Root Directory:** `backend`

**Build Command:** (Auto-detected)
```bash
pip install -r requirements.txt
```

**Start Command:** (Auto-detected)
```bash
python main.py
```

### 3. Add Environment Variables

In Railway dashboard → Variables:

```
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.railway.app
```

### 4. Add Persistent Volume

1. Go to **Settings** → **Volumes**
2. Click **"New Volume"**
3. Mount Path: `/app/data`
4. Size: 1GB (or more if needed)

This ensures your ChromaDB data persists between deployments!

### 5. Frontend Deployment

1. In the same Railway project, click **"New Service"**
2. Select the same GitHub repo
3. **Root Directory:** `frontend`

**Build Command:**
```bash
npm install && npm run build
```

**Start Command:**
```bash
npm run preview -- --host 0.0.0.0 --port $PORT
```

### 6. Update Frontend Environment

Add to frontend variables:
```
VITE_API_URL=https://your-backend-url.railway.app
```

You'll get this URL from your backend service.

### 7. Update Backend CORS

After frontend is deployed, update backend CORS_ORIGINS with your frontend URL.

## Cost Estimate

- **Free tier:** $5 credit/month (good for testing)
- **Hobby plan:** $5/month per service
- **Total:** ~$10/month for both services

## Automatic Deploys

Railway automatically deploys when you push to GitHub! 🚀

## Monitoring

- View logs in Railway dashboard
- Check health: `https://your-backend.railway.app/health`
- Check status: `https://your-backend.railway.app/status`

## Troubleshooting

If build fails:
1. Check logs in Railway dashboard
2. Verify environment variables are set
3. Ensure volume is mounted to `/app/data`

## Alternative: One-Click Deploy Button

Add this to your README.md:

```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/jahidulzaid/Agent-ChatBot)
```

---

## Why NOT Vercel?

❌ **OOM during builds** - ML dependencies are too heavy
❌ **No persistent storage** - ChromaDB needs persistent disk
❌ **Serverless architecture** - Not suitable for ML models
❌ **Cold starts** - Loading models on each request is slow

**Use Railway, Render, or Docker-based platforms instead!**
