"""Application configuration management."""
from pydantic_settings import BaseSettings
from typing import List, Union, Optional, Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Provider Strategy
    LLM_PROVIDER: Literal["auto", "openrouter", "openai"] = "openrouter"

    # OpenRouter API
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini-2024-07-18"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: Optional[str] = None
    OPENROUTER_APP_NAME: str = "Agentic RAG Chatbot"

    # OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Application
    APP_NAME: str = "Agentic RAG Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
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
    CORS_ORIGIN_REGEX: Optional[str] = r"^https://.*\.vercel\.app$"

    # Web Search
    WEB_SEARCH_PROVIDER: Literal["tavily", "duckduckgo", "zenserp"] = "tavily"
    TAVILY_API_KEY: Optional[str] = None
    TAVILY_SEARCH_DEPTH: Literal["advanced", "basic", "fast", "ultra-fast"] = "basic"
    TAVILY_MAX_RESULTS: int = 5
    ZENSERP_API_KEY: Optional[str] = None
    
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

    @property
    def has_openrouter_key(self) -> bool:
        """Whether an OpenRouter key is configured."""
        return bool(self.OPENROUTER_API_KEY)

    @property
    def has_openai_key(self) -> bool:
        """Whether an OpenAI key is configured."""
        return bool(self.OPENAI_API_KEY)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
