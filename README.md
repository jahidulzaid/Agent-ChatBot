# 🤖 Agentic RAG Chatbot

A full-stack intelligent chatbot with Retrieval-Augmented Generation (RAG), ReAct reasoning pattern, and multiple AI tools.

[![GitHub stars](https://img.shields.io/github/stars/jahidulzaid/Agent-ChatBot)](https://github.com/jahidulzaid/Agent-ChatBot/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](docker-compose.yml)

## ✨ Features

- 🧠 **ReAct Pattern**: Reasoning + Acting for intelligent decision-making
- 📚 **RAG System**: Upload documents (PDF, DOCX, TXT, MD) for context-aware responses
- 🔧 **Multiple Tools**:
  - Document search with vector embeddings
   - Web search (Tavily API)
  - Calculator for math operations
  - Current time/date
  - Greetings & wishes generator
  - Programming jokes
- 🎨 **Modern UI**: React + Vite with beautiful interface
- 🔄 **Real-time Reasoning**: View AI's thought process step-by-step
- 🤖 **Multiple AI Models**: Switch between 6+ free OpenRouter models
- 🔀 **Dual Provider Support**: OpenRouter-first with optional direct OpenAI fallback
- 🐳 **Docker Ready**: One-command deployment

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React UI      │ ───► │  FastAPI Backend │ ───► │  OpenRouter API │
│   (Frontend)    │      │   (Agent Core)   │      │   (LLM)         │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   ChromaDB       │
                         │  (Vector Store)  │
                         └──────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenRouter API Key (recommended, from [openrouter.ai](https://openrouter.ai/))
- Optional OpenAI API Key (for direct OpenAI provider mode)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/jahidulzaid/Agent-ChatBot.git
cd Agent-ChatBot

# Configure environment
cp .env.example backend/.env
# Edit backend/.env with your API keys

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run backend
python main.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## � Project Structure

```
Agent-ChatBot/
├── backend/
│   ├── app/
│   │   ├── agents/          # ReAct agent implementation
│   │   ├── rag/             # RAG system (vector store, document processor)
│   │   ├── tools/           # Agent tools (search, calculator, etc.)
│   │   └── config.py        # Configuration management
│   ├── data/
│   │   ├── chromadb/        # Vector database
│   │   └── uploads/         # Uploaded documents
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.jsx          # Main application
│   ├── Dockerfile           # Frontend Docker configuration
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Multi-container setup
├── ARCHITECTURE.md          # Detailed system architecture
└── README.md                # This file
```

## 🎯 Key Components

### Backend (FastAPI + Python)

- **ReAct Agent**: Implements Reasoning + Acting pattern
- **RAG System**: ChromaDB for vector storage, sentence-transformers for embeddings
- **LLM Integration**: OpenRouter API with multiple model support
- **Tools**: Search, calculate, time, greet, wish, joke, web_search

### Frontend (React + Vite)

- **Chat Interface**: Clean, modern UI with message history
- **Reasoning Viewer**: Expandable reasoning trace for transparency
- **Model Selector**: Choose from 6+ free AI models
- **Document Manager**: Upload and manage documents
- **Responsive Design**: Works on desktop and mobile

## � Usage Examples

### Chat with the Bot

```
User: "Hello!"
Bot: "Hello! Welcome! I'm an AI assistant equipped with various tools..."

User: "What's 25 * 4?"
Bot: [Uses calculator tool] "The result is 100."

User: "Tell me a joke"
Bot: [Uses joke tool] "Why do programmers prefer dark mode? Because light attracts bugs! 🐛"
```

### Document Upload & RAG

1. Upload a PDF/DOCX document
2. Ask questions about the content
3. Bot searches the document and provides accurate answers

### Web Search

```
User: "Search for Python 3.12 new features"
Bot: [Uses web_search tool]
🔍 Web Search Results:
1. What's New In Python 3.12
   https://docs.python.org/3/whatsnew/3.12.html
   ...
```

## 🔧 Configuration

### Environment Variables

Create `backend/.env`:

```env
# Preferred provider (openrouter | openai | auto)
LLM_PROVIDER=openrouter

# Recommended
OPENROUTER_API_KEY=your_api_key_here

# Optional OpenAI fallback
# OPENAI_API_KEY=your_openai_key_here

# Optional (defaults shown)
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
OPENAI_MODEL=gpt-4o-mini
WEB_SEARCH_PROVIDER=tavily
# TAVILY_API_KEY=tvly-YOUR_API_KEY
MAX_ITERATIONS=8
TEMPERATURE=0.3
MAX_TOKENS=1000
DEBUG=False
```

### Available Models

- GPT-4o Mini (OpenAI) - Default
- Gemini Flash 1.5 (Google)
- Llama 3.2 3B (Meta)
- Phi-3 Mini (Microsoft)
- Mistral 7B (Mistral)
- Qwen 2 7B (Qwen)

## 📖 Documentation

- **[Architecture Guide](ARCHITECTURE.md)**: Detailed system architecture and diagrams
- **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when backend is running)

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend
black .
flake8 .

# Frontend
npm run lint
npm run format
```

## 📝 Deployment

### ⚠️ Important: Platform Compatibility

**Backend is NOT Compatible with Vercel** ❌
- Backend uses ML/runtime components (sentence-transformers, vector storage) that are not a fit for Vercel serverless limits.
- Deploy backend on Railway/Render/VPS.

**Frontend is Compatible with Vercel** ✅
- You can host the React frontend on Vercel and point it to your Railway backend.

**✅ Recommended Platforms:**

1. **Railway** (⭐ Best Choice)
   - Handles heavy ML dependencies
   - Persistent storage for ChromaDB
   - Easy GitHub integration

2. **Render**
   - Free tier available
   - Good for ML/AI apps

3. **Docker on VPS** (DigitalOcean, AWS, etc.)
   - Full control

### Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/jahidulzaid/Agent-ChatBot)

Use two Railway services from the same repo (monorepo setup):

1. Create a new Railway project from this GitHub repository.
2. Add service `backend`:
    - Root Directory: `backend`
    - Railway will use `backend/railway.json` and `backend/Dockerfile`.
    - Set required variables:
       - `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`)
       - `LLM_PROVIDER` (`openrouter`, `openai`, or `auto`)
       - `TAVILY_API_KEY` (if using Tavily web search)
    - Set CORS for your frontend URL:
       - `CORS_ORIGINS=https://<your-frontend-domain>`
3. Deploy backend once and copy its public URL, for example:
    - `https://agent-chatbot-backend-production.up.railway.app`
4. Add service `frontend`:
    - Root Directory: `frontend`
    - Railway will use `frontend/railway.json` and `frontend/Dockerfile`.
    - Set variable:
       - `BACKEND_URL=https://<your-backend-domain>`
5. Deploy frontend and open its public URL.

Notes:
- Frontend now proxies `/api/*` requests to `BACKEND_URL` via Nginx.
- Railway dynamic `PORT` is handled automatically in both services.
- If CORS errors appear, ensure `CORS_ORIGINS` exactly matches the frontend domain (including `https://`).

### Frontend on Vercel + Backend on Railway

1. Keep backend deployed on Railway.
2. In Railway backend variables, set:
   - `CORS_ORIGINS=https://<your-vercel-domain>`
   - `CORS_ORIGIN_REGEX=^https://.*\\.vercel\\.app$` (recommended for preview deployments)
3. Deploy `frontend/` to Vercel.
4. In Vercel Project Settings -> Environment Variables, set:
   - `VITE_API_URL=https://<your-railway-backend-domain>`
5. Redeploy frontend in Vercel so the env value is included in the build.

For detailed deployment instructions on other platforms, see:

- 🚂 Railway (Recommended for beginners)
- 🎨 Render (Free tier available)
- ☁️ AWS ECS (Production grade)
- 🌊 DigitalOcean (Balanced approach)
- 🐳 Docker on any VPS

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenRouter for LLM API access
- ChromaDB for vector storage
- FastAPI for the backend framework
- React + Vite for the frontend
- Sentence-Transformers for embeddings

## 📧 Contact

Jahidul Zaid - [@jahidulzaid](https://github.com/jahidulzaid)

Project Link: [https://github.com/jahidulzaid/Agent-ChatBot](https://github.com/jahidulzaid/Agent-ChatBot)

---

⭐ **Star this repository if you find it helpful!** ⭐
