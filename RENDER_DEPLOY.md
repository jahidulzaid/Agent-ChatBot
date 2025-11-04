# Render Configuration for Agentic RAG Chatbot

## Backend Service Configuration

### Service Type
Web Service

### Build Command
```bash
pip install -r requirements.render.txt
```

### Start Command
```bash
python main.py
```

### Environment Variables
```
OPENROUTER_API_KEY=your_actual_key
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
CORS_ORIGINS=https://your-frontend.onrender.com
PYTHON_VERSION=3.11
```

### Persistent Disk
- **Mount Path:** `/app/data`
- **Size:** 1GB (free tier)

### Health Check
- **Path:** `/health`

---

## Frontend Service Configuration

### Service Type
Static Site

### Build Command
```bash
cd frontend && npm install && npm run build
```

### Publish Directory
```
frontend/dist
```

### Environment Variables
```
VITE_API_URL=https://your-backend.onrender.com
```

---

## Cost
- **Free Tier:** Available with limitations (spins down after 15 min inactivity)
- **Paid:** $7/month per service

## Auto-Deploy
Render auto-deploys on git push to main branch.

## Notes
- Free tier services spin down after inactivity
- First request after spin-down takes 30-60 seconds
- Consider paid tier for production use
