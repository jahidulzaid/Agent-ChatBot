# 🤖 Agentic RAG Chatbot

A full-stack intelligent chatbot that combines **Retrieval-Augmented Generation (RAG)** with **Agentic capabilities** - enabling it to reason, plan, and take actions dynamically. Built with FastAPI, React, and OpenRouter API.

## ✨ Features

### 🧠 Agentic Reasoning
- **ReAct Pattern**: Implements Reasoning + Acting loop for complex query handling
- **Multi-step Planning**: Agent can break down complex tasks into steps
- **Tool Use**: Dynamic tool selection and execution based on context

### 📚 RAG System
- **Document Processing**: Support for PDF, DOCX, TXT, and Markdown files
- **Vector Search**: ChromaDB-powered semantic search
- **Smart Chunking**: Intelligent document segmentation with overlap
- **Real-time Ingestion**: Upload and query documents instantly

### 🛠️ Available Tools
- **Document Search**: Semantic search through uploaded documents
- **Time/Date**: Get current time and date information
- **Calculator**: Perform mathematical calculations
- **Document Summary**: Overview of knowledge base
- **Web Search**: Extensible for external data (placeholder)

### 💻 Modern UI
- **Real-time Chat**: Smooth, responsive chat interface
- **Reasoning Visualization**: View agent's thought process
- **Document Management**: Easy upload and management
- **Progress Tracking**: Upload progress and status indicators

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

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=your_key_here
```

5. **Run the backend:**
```bash
python main.py
```

Backend will start at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will start at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "What documents do you have?",
  "conversation_history": [],
  "use_rag": true
}
```

#### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data

file: <file>
```

#### Search Documents
```http
POST /documents/search
Content-Type: application/json

{
  "query": "machine learning",
  "top_k": 5
}
```

## 🎯 Usage Examples

### Upload and Query Documents

1. **Upload a document** through the sidebar (PDF, DOCX, TXT, MD)
2. **Ask questions** about the content:
   - "What is this document about?"
   - "Find information about [topic]"
   - "Summarize the key points"

### Agent Reasoning

The agent will automatically:
- **Analyze** your query
- **Choose** appropriate tools
- **Execute** actions
- **Provide** reasoned answers

Example conversation:
```
User: "What documents do I have and what time is it?"

Agent Reasoning:
Thought: User wants two pieces of information
Action: summarize_documents
Observation: Knowledge base contains 15 document chunks
Action: get_current_time
Observation: Current time is 2024-01-15 14:30:00
Answer: You have 15 document chunks in your knowledge base. 
        The current time is 2:30 PM on January 15, 2024.
```

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
# OpenRouter API
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini-2024-07-18

# Agent Settings
MAX_ITERATIONS=5
TEMPERATURE=0.7
MAX_TOKENS=2000

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend Configuration

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## 🐳 Docker Deployment (Optional)

### Backend Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./backend/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## 🎨 Customization

### Add New Tools

1. **Create tool function** in `backend/app/tools/agent_tools.py`:
```python
async def my_new_tool(self, param: str, **kwargs) -> str:
    """Tool description."""
    # Your logic here
    return "Result"
```

2. **Register tool** in `__init__`:
```python
self.tools['my_new_tool'] = self.my_new_tool
```

3. **Add description** in `get_tool_descriptions()`:
```python
{
    'name': 'my_new_tool',
    'description': 'What this tool does',
    'parameters': {'param': 'Parameter description'}
}
```

### Customize Agent Prompts

Edit `backend/app/agents/react_agent.py` to modify:
- System prompt
- Reasoning format
- Tool selection logic

## 📊 Project Structure

```
ChatBot/
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent logic & LLM client
│   │   ├── rag/             # RAG components
│   │   ├── tools/           # Agent tools
│   │   └── config.py        # Configuration
│   ├── data/
│   │   ├── uploads/         # Uploaded documents
│   │   └── chromadb/        # Vector database
│   ├── main.py              # FastAPI application
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── App.jsx          # Main component
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🔍 Troubleshooting

### Backend Issues

**ChromaDB Error:**
```bash
# Clear the database
rm -rf backend/data/chromadb/*
```

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**API Connection:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/config.py`

**Build Errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Production Deployment

### Environment Variables
- Set `DEBUG=False` in production
- Use production-grade API keys
- Configure proper CORS origins
- Set up SSL/TLS

### Performance
- Use production ASGI server (Gunicorn + Uvicorn workers)
- Implement caching layer
- Add rate limiting
- Monitor resource usage

### Security
- Add authentication/authorization
- Validate all inputs
- Implement file size limits
- Use environment secrets management

## 📝 License

MIT License - feel free to use this project for your portfolio!

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📧 Contact

Add your contact information here for portfolio purposes.

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)

---

Built with ❤️ for portfolio demonstration
