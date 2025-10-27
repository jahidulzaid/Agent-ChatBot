# 🚨 Render Deployment - Memory Issue Fix

## Problem
Render free tier has **512MB RAM limit**, but the backend needs ~1-2GB for:
- ChromaDB
- Sentence-transformers model
- FastAPI runtime

## Solutions (Choose One)

---

## ✅ Solution 1: Optimize for Free Tier (Recommended)

### Backend Optimization

We'll reduce memory usage to fit in 512MB:

#### 1. Use Lighter Embedding Model

Edit `backend/app/config.py`:
```python
# Change from all-MiniLM-L6-v2 (384 dims) to:
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"  # 384→128 dims, much smaller
```

#### 2. Optimize ChromaDB Settings

Create `backend/app/rag/chromadb_config.py`:
```python
# Memory-efficient ChromaDB settings
CHROMA_SETTINGS = {
    "anonymized_telemetry": False,
    "allow_reset": True,
    "is_persistent": True,
}
```

#### 3. Reduce Model Loading

Edit `backend/app/tools/agent_tools.py` - Only load embeddings when needed:
```python
# Lazy load embeddings
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")
    return _embedding_model
```

#### 4. Use Render-Specific Dockerfile

Create `backend/Dockerfile.render`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .

# Install with minimal dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y torch torchvision torchaudio \
    && pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

COPY . .

RUN mkdir -p data/chromadb data/uploads

EXPOSE 8000

# Use gunicorn with limited workers
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--max-requests", "100", "--max-requests-jitter", "10"]
```

#### 5. Update requirements.txt

Create `backend/requirements.render.txt`:
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
python-multipart==0.0.6
openai==1.6.1
chromadb==0.4.22
sentence-transformers==2.3.1
PyPDF2==3.0.1
python-docx==1.1.0
markdown==3.5.1
httpx==0.26.0
pydantic-settings==2.1.0
```

#### 6. Configure Render

In Render Dashboard:
- **Build Command**: `pip install -r requirements.render.txt`
- **Start Command**: `gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --preload`
- **Docker Command**: Leave empty (use build command)
- **Environment Variables**:
  ```
  OPENROUTER_API_KEY=your_key
  DEBUG=False
  CORS_ORIGINS=https://your-frontend.onrender.com
  PYTHON_VERSION=3.11
  ```

---

## ✅ Solution 2: Deploy Backend + Frontend Separately

### Option A: Split Services

**Backend** → Railway (better free tier: 512MB RAM + 512MB burst)
**Frontend** → Render (static site, very light)

#### Backend on Railway:
```bash
# Railway gives you more memory and better free tier
1. Go to railway.app
2. Deploy backend
3. Get backend URL
```

#### Frontend on Render:
```bash
# Render dashboard:
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

Set environment:
```
VITE_API_URL=https://your-backend.railway.app
```

### Option B: Frontend Only on Render

Keep backend on Railway, deploy only frontend to Render as **Static Site**:

1. **Create Static Site** on Render
2. **Root Directory**: `frontend`
3. **Build Command**: `npm install && npm run build`
4. **Publish Directory**: `dist`
5. **Environment**:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

---

## ✅ Solution 3: Upgrade Render (Paid)

**Cost**: $7/month for 512MB → $7/month for 2GB RAM

In Render Dashboard:
1. Go to your service
2. Click "Upgrade"
3. Select "Starter" plan ($7/month)
4. Keep your current Docker setup

---

## ✅ Solution 4: Use Railway Instead (Better Free Tier)

Railway offers:
- **512MB RAM + 512MB burst** (vs Render's 512MB hard limit)
- Better for Python/ML apps
- Same auto-deploy features

### Quick Migration to Railway:

```bash
# 1. Go to railway.app
# 2. "New Project" → "Deploy from GitHub"
# 3. Select Agent-ChatBot repo
# 4. Railway auto-detects and deploys
```

**Configure Backend**:
- Root: `backend`
- Start: `python main.py`
- Add Volume: `/app/data` (1GB)

**Configure Frontend**:
- Root: `frontend`
- Build: `npm install && npm run build`
- Start: `npx serve -s dist -p 3000`

**Environment Variables** (Backend):
```
OPENROUTER_API_KEY=your_key
DEBUG=False
CORS_ORIGINS=https://your-frontend.up.railway.app
```

**Environment Variables** (Frontend):
```
VITE_API_URL=https://your-backend.up.railway.app
```

---

## ✅ Solution 5: Lightweight Alternative Stack

Replace heavy components:

### Instead of ChromaDB + SentenceTransformers:
Use **SQLite + OpenAI Embeddings** (via OpenRouter):

```python
# Much lighter, uses OpenRouter for embeddings
# No local ML models needed
# Fits in 512MB easily
```

This requires code changes but drastically reduces memory.

---

## 🎯 Recommended Solution

### For Free Tier:
**Use Railway** (Solution 4) - Better free tier for Python/ML apps

### For Render Free Tier:
**Split deployment** (Solution 2):
- Backend on Railway (free)
- Frontend on Render (free static site)

### For Staying on Render:
**Optimize** (Solution 1) + **Upgrade to $7/month** (Solution 3)

---

## 📊 Memory Comparison

| Platform | Free Tier RAM | Burst | Best For |
|----------|---------------|-------|----------|
| **Render** | 512MB | No | Static sites, light apps |
| **Railway** | 512MB | 512MB | Python, ML, databases |
| **Fly.io** | 256MB | No | Microservices |
| **Heroku** | 512MB | No | Ruby, Node.js |

---

## 🔧 Quick Fix Steps

### Immediate Fix (5 minutes):

1. **Deploy Backend to Railway**:
   ```bash
   # Go to railway.app
   # Connect GitHub
   # Deploy backend folder
   # Get URL: https://xxx.railway.app
   ```

2. **Update Render Frontend**:
   ```bash
   # In Render dashboard:
   # Change to Static Site
   # Build: cd frontend && npm install && npm run build
   # Publish: frontend/dist
   # Add env: VITE_API_URL=https://xxx.railway.app
   ```

3. **Done!** ✅

---

## 📞 Need Help?

Let me know which solution you'd like to implement:
1. ✅ Optimize for Render free tier
2. ✅ Split: Backend on Railway, Frontend on Render
3. ✅ Migrate everything to Railway
4. ✅ Upgrade Render to paid plan
5. ✅ Use lightweight alternative stack

I can help you implement any of these! 🚀
