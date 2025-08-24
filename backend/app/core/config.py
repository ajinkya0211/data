from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Literal, Union
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "AI Notebook System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://notebook_user:notebook_pass@localhost:5432/ai_notebook"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_POOL_SIZE: int = 10
    
    # MinIO/S3 settings
    MINIO_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "notebook-artifacts"
    MINIO_SECURE: bool = False
    
    # JWT settings
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Provider Configuration
    DEFAULT_AI_PROVIDER: Literal["ollama", "openai", "gemini"] = "ollama"
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_MAX_TOKENS: int = 4000
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Google Gemini settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_MAX_TOKENS: int = 4000
    GEMINI_TEMPERATURE: float = 0.7
    
    # Ollama settings (Local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2:3b"  # Switch to faster model
    OLLAMA_TIMEOUT: int = 60  # Reduce timeout
    OLLAMA_MAX_TOKENS: int = 2000  # Reduce tokens for faster response
    OLLAMA_TEMPERATURE: float = 0.7
    
    # Jupyter kernel settings
    JUPYTER_KERNEL_URL: str = "http://localhost:8888"
    JUPYTER_KERNEL_TOKEN: str = "notebook_token"
    KERNEL_TIMEOUT_SECONDS: int = 300
    
    # File upload settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: Union[List[str], str] = [".csv", ".parquet", ".json", ".xlsx", ".ipynb"]
    
    @field_validator('ALLOWED_FILE_TYPES', mode='before')
    @classmethod
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(',') if x.strip()]
        return v
    
    # Execution settings
    MAX_CONCURRENT_RUNS: int = 10
    MAX_BLOCKS_PER_RUN: int = 100
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    
    # Frontend settings (optional)
    REACT_APP_API_URL: Optional[str] = None
    REACT_APP_WS_URL: Optional[str] = None
    REACT_APP_ENVIRONMENT: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env
    
    @property
    def allowed_file_types(self) -> List[str]:
        """Get allowed file types with fallback to default"""
        if self.ALLOWED_FILE_TYPES is not None:
            return self.ALLOWED_FILE_TYPES
        return [".csv", ".parquet", ".json", ".xlsx", ".ipynb"]

# Create settings instance
settings = Settings()

# Override with environment variables if present
if os.getenv("DATABASE_URL"):
    settings.DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("REDIS_URL"):
    settings.REDIS_URL = os.getenv("REDIS_URL")
if os.getenv("MINIO_URL"):
    settings.MINIO_URL = os.getenv("MINIO_URL")
if os.getenv("OPENAI_API_KEY"):
    settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if os.getenv("GEMINI_API_KEY"):
    settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if os.getenv("DEFAULT_AI_PROVIDER"):
    settings.DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER") 