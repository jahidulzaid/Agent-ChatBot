"""FastAPI application - main entry point."""
import logging
import json
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import aiofiles
from pathlib import Path
import uuid

from app.config import settings
from app.agents.react_agent import react_agent
from app.agents.agent_runtime import agent_runtime
from app.rag.vector_store import vector_store
from app.rag.document_processor import document_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic RAG Chatbot with reasoning and tool use capabilities"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    use_rag: bool = True
    model: Optional[str] = None
    provider: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    reasoning_trace: List[Dict[str, Any]]
    iterations: int
    provider: Optional[str] = None
    model: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    filename: str
    chunks_created: int
    message: str


class DocumentSearchRequest(BaseModel):
    """Document search request."""
    query: str
    top_k: int = 5


class DocumentSearchResponse(BaseModel):
    """Document search response."""
    results: List[Dict[str, Any]]


class SystemStatus(BaseModel):
    """System status model."""
    status: str
    version: str
    total_documents: int
    available_tools: List[str]
    llm_provider_preference: str
    has_openrouter_key: bool
    has_openai_key: bool
    default_model: str


# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agentic RAG Chatbot API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status."""
    stats = vector_store.get_collection_stats()
    from app.tools.agent_tools import agent_tools
    from app.agents.llm_client import llm_client
    model_catalog = llm_client.get_model_catalog()
    provider_status = llm_client.get_provider_status()
    preferred_provider = model_catalog['recommended_provider']
    default_model = (
        provider_status['default_openrouter_model']
        if preferred_provider == 'openrouter'
        else provider_status['default_openai_model']
    )
    
    return SystemStatus(
        status="operational",
        version=settings.APP_VERSION,
        total_documents=stats['total_documents'],
        available_tools=list(agent_tools.tools.keys()),
        llm_provider_preference=preferred_provider,
        has_openrouter_key=provider_status['has_openrouter_key'],
        has_openai_key=provider_status['has_openai_key'],
        default_model=default_model,
    )


@app.get("/models")
async def get_models():
    """Get available model catalog and provider status."""
    from app.agents.llm_client import llm_client
    return llm_client.get_model_catalog()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the agent.
    
    The agent will use RAG (if enabled) and can use tools to answer questions.
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}")
        if request.model:
            logger.info(f"Using model: {request.model}")
        
        # Run the agent
        result = await react_agent.run(
            user_message=request.message,
            conversation_history=request.conversation_history or [],
            model=request.model,
            provider=request.provider,
            use_rag=request.use_rag,
        )
        
        return ChatResponse(
            answer=result['answer'],
            reasoning_trace=result['reasoning_trace'],
            iterations=result['iterations'],
            provider=result.get('provider'),
            model=result.get('model'),
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat trace events and final answer as NDJSON."""
    try:
        async def generate():
            async for event in agent_runtime.run_with_events(
                user_message=request.message,
                conversation_history=request.conversation_history or [],
                model=request.model,
                provider=request.provider,
                use_rag=request.use_rag,
            ):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
    except Exception as e:
        logger.error(f"Error in stream endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document.
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
        file_ext = Path(file.filename).suffix.lower() # pyright: ignore[reportArgumentType]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        file_path = upload_dir / f"{file_id}_{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Saved file: {file_path}")
        
        # Process document
        documents = document_processor.process_file(str(file_path))
        
        # Add to vector store
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        vector_store.add_documents(texts=texts, metadatas=metadatas)
        
        logger.info(f"Processed and stored {len(documents)} chunks from {file.filename}")
        
        return DocumentUploadResponse(
            filename=file.filename, # type: ignore
            chunks_created=len(documents),
            message=f"Successfully processed {file.filename} into {len(documents)} chunks"
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """Search through uploaded documents."""
    try:
        results = vector_store.search(request.query, n_results=request.top_k)
        
        return DocumentSearchResponse(results=results)
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/stats")
async def get_document_stats():
    """Get statistics about the document collection."""
    try:
        stats = vector_store.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/clear")
async def clear_documents():
    """Clear all documents from the vector store."""
    try:
        vector_store.clear_documents()
        
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def get_available_tools():
    """Get list of available tools the agent can use."""
    from app.tools.agent_tools import agent_tools
    return {
        "tools": agent_tools.get_tool_descriptions()
    }


if __name__ == "__main__":
    import uvicorn
    api_port = int(os.getenv("PORT", str(settings.API_PORT)))
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=api_port,
        reload=settings.DEBUG
    )
