# 🚀 Quick Start Guide

## Option 1: Automated Setup (Recommended)

### Windows (PowerShell)
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Option 2: Manual Setup

### Step 1: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

Backend will be available at: http://localhost:8000

### Step 2: Frontend Setup (New Terminal)

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## First Steps After Setup

### 1. Test the API
Visit http://localhost:8000/docs for interactive API documentation

### 2. Upload a Document
- Click the sidebar menu icon
- Click "Upload Document"
- Choose a PDF, DOCX, TXT, or MD file
- Wait for processing

### 3. Ask Questions
Try these example queries:
- "What documents do you have?"
- "What is the current time?"
- "Calculate 2 + 2"
- "Search for [topic] in my documents"

## Troubleshooting

### Backend won't start
**Error: ModuleNotFoundError**
```powershell
# Make sure virtual environment is activated
# Then reinstall
pip install -r requirements.txt --force-reinstall
```

**Error: Address already in use**
```powershell
# Change port in backend/.env
API_PORT=8001
```

### Frontend won't start
**Error: Cannot find module**
```powershell
# Clear and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

**Error: Failed to fetch**
- Make sure backend is running
- Check backend URL in console
- Verify CORS settings

### ChromaDB Issues
```powershell
# Clear the database
Remove-Item -Recurse -Force backend\data\chromadb\*
```

## Testing the Agent

### Test 1: Simple Question
```
You: Hello!
Bot: [Direct response without tools]
```

### Test 2: Tool Use
```
You: What time is it?
Bot: [Uses get_current_time tool]
```

### Test 3: RAG Query (after uploading docs)
```
You: What is in my documents?
Bot: [Uses search_documents tool]
```

### Test 4: Multi-Step Reasoning
```
You: How many documents do I have and what time is it?
Bot: [Uses multiple tools and combines results]
```

## API Endpoints to Test

### Health Check
```bash
curl http://localhost:8000/health
```

### Get Status
```bash
curl http://localhost:8000/status
```

### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "conversation_history": []}'
```

### Upload Document
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@path/to/document.pdf"
```

## Development Tips

### Backend Development
- Auto-reload enabled with `DEBUG=True`
- Check logs in terminal
- Test endpoints at http://localhost:8000/docs

### Frontend Development
- Hot reload enabled by default
- Check browser console for errors
- React DevTools recommended

### Adding New Features
1. Backend: Add tool in `backend/app/tools/agent_tools.py`
2. Frontend: Modify components in `frontend/src/components/`
3. Test changes locally
4. Update README with new features

## Performance Optimization

### Backend
- Reduce `CHUNK_SIZE` for faster processing
- Increase `TOP_K_RESULTS` for more context
- Adjust `MAX_ITERATIONS` for agent depth

### Frontend
- Images: Add lazy loading
- State: Implement memoization
- API: Add request caching

## Next Steps

1. ✅ Get familiar with the chat interface
2. ✅ Upload sample documents
3. ✅ Test different query types
4. ✅ View reasoning traces
5. ✅ Explore the codebase
6. ✅ Customize prompts and tools
7. ✅ Deploy to cloud (optional)

## Useful Commands

### Backend
```powershell
# Run tests (if added)
pytest

# Check code style
black app/

# Type checking
mypy app/
```

### Frontend
```powershell
# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- ChromaDB Docs: https://docs.trychroma.com/
- OpenRouter Docs: https://openrouter.ai/docs

Happy coding! 🎉
