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
  - Web search (Google via Zenserp API)
  - Calculator for math operations
  - Current time/date
  - Greetings & wishes generator
  - Programming jokes
- 🎨 **Modern UI**: React + Vite with beautiful interface
- 🔄 **Real-time Reasoning**: View AI's thought process step-by-step
- 🤖 **Multiple AI Models**: Switch between 6+ free OpenRouter models
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
- OpenRouter API Key (get from [openrouter.ai](https://openrouter.ai/))

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/jahidulzaid/Agent-ChatBot.git
cd Agent-ChatBot

# Configure environment
cp .env.example backend/.env
# Edit backend/.env with your OPENROUTER_API_KEY

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
# Edit .env with your OPENROUTER_API_KEY

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
├── DEPLOYMENT.md            # Comprehensive deployment guide
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
# Required
OPENROUTER_API_KEY=your_api_key_here

# Optional (defaults shown)
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18
MAX_ITERATIONS=8
TEMPERATURE=0.3
MAX_TOKENS=1000
DEBUG=True
```

### Available Models

- GPT-4o Mini (OpenAI) - Default
- Gemini Flash 1.5 (Google)
- Llama 3.2 3B (Meta)
- Phi-3 Mini (Microsoft)
- Mistral 7B (Mistral)
- Qwen 2 7B (Qwen)

## � Documentation

- **[Deployment Guide](DEPLOYMENT.md)**: Complete guide for deploying to production
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

**NOT Compatible with Vercel** ❌
- This app uses ML models (sentence-transformers, ChromaDB) that cause OOM errors on Vercel
- Vercel's serverless architecture doesn't support persistent vector databases
- Build process requires 8GB+ RAM for dependencies

**✅ Recommended Platforms:**

1. **Railway** (⭐ Best Choice)
   - Handles heavy ML dependencies
   - Persistent storage for ChromaDB
   - Easy GitHub integration
   - See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)

2. **Render**
   - Free tier available
   - Good for ML/AI apps
   - See [RENDER_DEPLOY.md](RENDER_DEPLOY.md)

3. **Docker on VPS** (DigitalOcean, AWS, etc.)
   - Full control
   - See [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/jahidulzaid/Agent-ChatBot)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:

- 🚂 Railway (Recommended for beginners) - [Quick Guide](RAILWAY_DEPLOY.md)
- 🎨 Render (Free tier available) - [Quick Guide](RENDER_DEPLOY.md)
- ☁️ AWS ECS (Production grade)
- 🌊 DigitalOcean (Balanced approach)
- 🐳 Docker on any VPS

## 📝 License

MIT License - feel free to use this project for your portfolio!

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
