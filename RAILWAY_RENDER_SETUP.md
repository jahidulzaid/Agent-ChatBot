# 🚀 Railway + Render Deployment Guide

## Problem Solved
Render's free tier (512MB RAM) is too small for the backend. **Solution**: Deploy backend on Railway (better free tier) and frontend on Render (perfect for static sites).

---

## ✅ Quick Setup (15 minutes)

### Step 1: Deploy Backend to Railway

1. **Go to Railway**: https://railway.app

2. **Create Account** (use GitHub)

3. **New Project** → "Deploy from GitHub repo"

4. **Select Repository**: `jahidulzaid/Agent-ChatBot`

5. **Configure Service**:
   - Click on the deployed service
   - Go to **Settings**
   - Set **Root Directory**: `backend`
   - **No build command needed** (Railway auto-detects Python)

6. **Add Environment Variables**:
   ```
   OPENROUTER_API_KEY=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
   DEBUG=False
   API_HOST=0.0.0.0
   API_PORT=8000
   CORS_ORIGINS=https://agent-chatbot-76cd.onrender.com
   ```

7. **Add Volume** (for persistent data):
   - Go to **Settings** → **Volumes**
   - Add Volume: Mount path `/app/data`, Size: 1GB

8. **Get Backend URL**:
   - Go to **Settings** → **Networking**
   - Copy the public URL (e.g., `https://agent-chatbot-production.up.railway.app`)

9. **Wait for deployment** (~2-3 minutes)

10. **Test Backend**:
    - Visit: `https://your-backend-url.railway.app/health`
    - Should see: `{"status":"healthy",...}`

---

### Step 2: Update Render Frontend

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Delete Current Service** (the one that failed):
   - Click on "Agent-ChatBot"
   - Settings → "Delete Service"

3. **Create New Static Site**:
   - Click "New +" → "Static Site"
   - Connect your GitHub repo: `jahidulzaid/Agent-ChatBot`

4. **Configure Static Site**:
   ```
   Name: agent-chatbot-frontend
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

5. **Add Environment Variable**:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```
   (Use the Railway URL from Step 1)

6. **Create Static Site** (click button)

7. **Wait for deployment** (~3-5 minutes)

8. **Get Frontend URL**:
   - Copy the URL (e.g., `https://agent-chatbot-frontend.onrender.com`)

---

### Step 3: Update CORS Settings

1. **Go back to Railway** backend service

2. **Update Environment Variable**:
   ```
   CORS_ORIGINS=https://agent-chatbot-frontend.onrender.com
   ```
   (Use your actual Render frontend URL)

3. **Restart Backend**:
   - Railway will auto-restart with new env var

---

### Step 4: Test Everything

1. **Visit Frontend**: https://agent-chatbot-frontend.onrender.com

2. **Test Features**:
   - ✅ Chat interface loads
   - ✅ Send a message
   - ✅ Upload a document
   - ✅ Ask about the document
   - ✅ Test tools (calculator, time, joke)
   - ✅ Test web search
   - ✅ Switch AI models

3. **Check Health**:
   - Backend: `https://your-backend.railway.app/health`
   - API Docs: `https://your-backend.railway.app/docs`

---

## 🎉 Done!

You now have:
- ✅ **Backend** on Railway (better free tier, handles ML workload)
- ✅ **Frontend** on Render (perfect for static sites)
- ✅ **Both free tiers**
- ✅ **Auto-deploy** on GitHub push
- ✅ **Persistent storage** for documents

---

## 📊 Resource Usage

### Railway Backend:
- RAM: 512MB base + 512MB burst = **1GB total** ✅
- Disk: 1GB volume for documents
- CPU: Sufficient for your workload
- Free tier hours: 500 hours/month (plenty)

### Render Frontend:
- RAM: ~50MB (static site, very light) ✅
- Bandwidth: 100GB/month (free)
- Build minutes: Unlimited for static sites
- Auto-SSL: Included

---

## 🔧 Maintenance

### Update Deployment

```bash
# Just push to GitHub
git add .
git commit -m "Update"
git push origin main

# Both platforms auto-deploy!
```

### View Logs

**Railway**:
- Dashboard → Your service → **Logs** tab

**Render**:
- Dashboard → Your site → **Logs** tab

### Monitor Health

**Backend Health**:
```bash
curl https://your-backend.railway.app/health
```

**Frontend**:
```bash
curl https://your-frontend.onrender.com
```

---

## 💰 Cost

- **Railway Backend**: FREE (500 hours/month)
- **Render Frontend**: FREE (static site unlimited)
- **Total**: $0/month 🎉

---

## 🔄 Alternative: All on Railway

If you prefer everything on Railway:

1. Add another service in same Railway project
2. Deploy frontend:
   - Root: `frontend`
   - Build: `npm install && npm run build`
   - Start: `npx serve -s dist -p 3000`
3. Add `serve` to package.json dependencies

Both services on Railway = still FREE (shares 500 hours)

---

## 📞 Troubleshooting

### Backend not starting on Railway?
- Check logs in Railway dashboard
- Verify environment variables
- Ensure volume is mounted

### Frontend can't connect to backend?
- Check CORS_ORIGINS in Railway backend
- Verify VITE_API_URL in Render frontend
- Check both URLs are correct (https, no trailing slash)

### Document upload not working?
- Ensure Railway volume is mounted at `/app/data`
- Check logs for permission errors

---

## 🎯 URLs to Save

After deployment, save these:

```
Frontend: https://agent-chatbot-frontend.onrender.com
Backend: https://agent-chatbot-production.railway.app
API Docs: https://agent-chatbot-production.railway.app/docs
Health: https://agent-chatbot-production.railway.app/health
```

---

## ✨ Benefits of This Setup

1. **Free**: Both platforms offer generous free tiers
2. **Reliable**: Railway handles ML workload better
3. **Fast**: Render serves static files very quickly
4. **Scalable**: Easy to upgrade either service
5. **Simple**: Auto-deploy on git push
6. **Persistent**: Documents saved in Railway volume

---

## 🚀 You're Live!

Your chatbot is now deployed with:
- Professional architecture
- Auto-deployment
- Persistent storage
- Free hosting
- Production-ready setup

Share your links! 🎊
