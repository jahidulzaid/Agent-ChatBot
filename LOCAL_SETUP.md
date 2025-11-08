# Running the Agentic RAG Chatbot Locally

This guide provides step-by-step instructions to run the Agentic RAG Chatbot project locally on your machine, including both the backend (FastAPI) and frontend (React/Vite) components.

## Prerequisites

- **Python 3.11** (the project uses a Python 3.11 virtual environment)
- **Node.js 16+** (for the frontend)
- **Git** (to clone the repository)
- **OpenRouter API Key** (get from [openrouter.ai](https://openrouter.ai/))

## Project Structure

```
Agent-ChatBot/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── py11/             # Python 3.11 virtual environment
└── data/             # Vector database and uploads
```

## Backend Setup

### 1. Activate Python 3.11 Environment

The project includes a pre-configured Python 3.11 virtual environment in the `py11/` directory.

```bash
# On Windows (PowerShell)
call py11\Scripts\activate.bat

# On Linux/Mac
source py11/bin/activate
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

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

### 4. Run the Backend Server

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`.

## Frontend Setup

### 1. Install Node.js Dependencies

```bash
cd frontend
npm install
```

### 2. Run the Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:3000` (or `http://localhost:3001` if 3000 is occupied).

## Running Both Services

### Option 1: Manual (Recommended for Development)

1. **Terminal 1 - Backend:**
   ```bash
   call py11\Scripts\activate.bat  # Windows
   cd backend
   python main.py
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

### Option 2: Using Scripts (Windows)

Create batch files for convenience:

**start_backend.bat:**
```batch
call py11\Scripts\activate.bat
cd backend
python main.py
```

**start_frontend.bat:**
```batch
cd frontend
npm run dev
```

Then run both batch files.

## Accessing the Application

- **Frontend:** http://localhost:3000 (or 3001)
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Testing the Setup

1. Open the frontend in your browser
2. Try sending a message like "Hello!"
3. Upload a document (PDF, DOCX, TXT, MD) to test RAG functionality
4. Ask questions about the uploaded document

## Troubleshooting

### Backend Issues

- **Import Errors:** Ensure you're using the `py11` environment and all dependencies are installed
- **API Key Issues:** Verify your OpenRouter API key is correct and has credits
- **Port Conflicts:** Change the port in `main.py` if 8000 is in use

### Frontend Issues

- **Port Conflicts:** Vite will automatically use 3001 if 3000 is occupied
- **CORS Errors:** Ensure the backend is running and CORS is configured correctly
- **Build Errors:** Run `npm install` again and check Node.js version

### Common Problems

- **Python Version:** Must use Python 3.11 (the py11 environment)
- **Dependencies:** Some packages may require additional system dependencies (e.g., Rust for certain Python packages)
- **Vector Database:** ChromaDB data is stored in `backend/data/chromadb/`

## Development Notes

- The backend uses ChromaDB for vector storage
- Documents are processed and stored in the `data/uploads/` directory
- The ReAct agent supports multiple AI models via OpenRouter
- Real-time reasoning traces are shown in the frontend

## Stopping the Services

- Press `Ctrl+C` in each terminal to stop the servers
- Data persists between runs in the `data/` directory

---

For production deployment, see the main [README.md](README.md) for Docker and cloud deployment options.</content>
<parameter name="filePath">H:\Personal\ChatBot\LOCAL_SETUP.md