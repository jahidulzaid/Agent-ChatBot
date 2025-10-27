"""Application configuration management."""
from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter API
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini-2024-07-18"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Application
    APP_NAME: str = "Agentic RAG Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chromadb"
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-MiniLM-L3-v2"
    
    # Agent Configuration
    MAX_ITERATIONS: int = 8
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 1000
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:5173"
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
