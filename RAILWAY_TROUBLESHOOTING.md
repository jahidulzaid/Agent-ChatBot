# 🚂 Railway Deployment - Troubleshooting Guide

## Issue: "Railpack could not determine how to build the app"

### ✅ Solution: Configuration Files Added

I've created 3 configuration files that tell Railway how to build your app:

1. **`railway.json`** - Railway-specific config
2. **`nixpacks.toml`** - Build instructions
3. **`Procfile`** - Start command

These files are now in your repository root.

---

## 🚀 Quick Fix Steps

### Step 1: Commit and Push New Files

```powershell
# In your ChatBot directory
git add railway.json nixpacks.toml Procfile
git commit -m "Add Railway configuration files"
git push origin main
```

### Step 2: Railway Will Auto-Deploy

Once you push, Railway will:
1. Detect the configuration files
2. Install Python 3.11
3. Go to `backend` folder
4. Install requirements
5. Start the app with `python main.py`

---

## 📋 What Each File Does

### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```
- Tells Railway to use Nixpacks builder
- Defines start command
- Sets restart policy

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python311", "gcc"]

[phases.install]
cmds = ["cd backend && pip install -r requirements.txt"]

[phases.build]
cmds = ["cd backend && mkdir -p data/chromadb data/uploads"]

[start]
cmd = "cd backend && python main.py"
```
- Installs Python 3.11 and gcc
- Installs Python dependencies
- Creates necessary directories
- Starts the application

### Procfile
```
web: cd backend && python main.py
```
- Simple start command
- Runs the FastAPI app

---

## 🔧 Alternative: Deploy Backend Folder Only

If you want to deploy ONLY the backend folder:

### Option 1: Change Root Directory in Railway

1. Go to Railway Dashboard
2. Click on your service
3. Go to **Settings**
4. Under **Source**, set **Root Directory** to: `backend`
5. Remove the `cd backend &&` from start command
6. Redeploy

### Option 2: Create Separate Backend Repo

```powershell
# Create new repo with just backend
mkdir Agent-ChatBot-Backend
cd Agent-ChatBot-Backend

# Copy backend files
cp -r ../Agent-ChatBot/backend/* .

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Push to GitHub
# Then deploy this repo to Railway
```

---

## 🎯 Recommended Approach

**Use the configuration files** (already created):
- ✅ Keep full repo structure
- ✅ Easy to maintain
- ✅ Single source of truth
- ✅ Works with Railway's auto-deploy

Just push the files and Railway will handle everything!

---

## 📊 Deployment Flow

```
Push to GitHub
     ↓
Railway detects push
     ↓
Reads railway.json
     ↓
Uses nixpacks.toml for build
     ↓
Installs Python 3.11 + gcc
     ↓
cd backend && pip install -r requirements.txt
     ↓
Creates data directories
     ↓
Runs: cd backend && python main.py
     ↓
✅ App is live!
```

---

## ✅ Verification Steps

After pushing the config files:

1. **Check Railway Dashboard**:
   - Go to your service
   - Click on "Deployments"
   - Watch the build logs

2. **Should see**:
   ```
   ✓ Installing Python 3.11
   ✓ Installing dependencies
   ✓ Building application
   ✓ Starting application
   ✓ Deployment successful
   ```

3. **Get your URL**:
   - Go to Settings → Networking
   - Copy the public URL

4. **Test**:
   ```powershell
   curl https://your-app.up.railway.app/health
   ```

---

## 🐛 Troubleshooting

### Build still failing?

**Check logs in Railway dashboard**:
- Look for error messages
- Common issues:
  * Missing dependencies in requirements.txt
  * Wrong Python version
  * Permission errors

### "Module not found" errors?

**Ensure requirements.txt is complete**:
```bash
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### App starts but crashes?

**Check environment variables**:
1. Railway Dashboard → Your Service
2. Variables tab
3. Ensure these are set:
   ```
   OPENROUTER_API_KEY=your_key
   DEBUG=False
   CORS_ORIGINS=your_frontend_url
   ```

### Need to see live logs?

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs
```

---

## 🎉 Success!

Once deployed, you'll have:
- ✅ Backend running on Railway
- ✅ Auto-deploy on git push
- ✅ Health endpoint working
- ✅ API docs available
- ✅ Ready for frontend connection

Next: Deploy frontend to Render (see RAILWAY_RENDER_SETUP.md)

---

## 📞 Quick Commands

```powershell
# Push config files
git add railway.json nixpacks.toml Procfile
git commit -m "Add Railway config"
git push origin main

# Test deployment
curl https://your-app.up.railway.app/health

# View deployment in browser
start https://your-app.up.railway.app/docs
```

---

Your Railway deployment is now configured! Push the files and watch it deploy automatically! 🚀
