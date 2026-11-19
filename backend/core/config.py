import os
from typing import Optional
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, ConfigDict

    class Settings(BaseSettings):
        model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

        APP_ENV: str = "development"
        APP_PORT: int = 8000
        FRONTEND_PORT: int = 8501
        BACKEND_URL: str = "http://localhost:8000"

        DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/multimodal_chatbot"
        SQLITE_FALLBACK_URL: str = "sqlite:///./chatbot.db"

        LLM_PROVIDER: str = "gemini"

        GEMINI_API_KEY: Optional[str] = None
        GEMINI_MODEL: str = "gemini-2.5-flash"
        GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

        OPENAI_API_KEY: Optional[str] = None
        OPENAI_MODEL: str = "gpt-4o-mini"
        OPENAI_BASE_URL: Optional[str] = None
        OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

        GROQ_API_KEY: Optional[str] = None
        GROQ_MODEL: str = "qwen/qwen3.8-27b"

        ANTHROPIC_API_KEY: Optional[str] = None
        CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

        NANO_BANANA_MODEL: str = "nano-banana-2.1"
        CANVA_ENABLED: bool = True

        VECTOR_STORE_DIR: str = "./storage/vector_db"
        UPLOAD_DIR: str = "./storage/uploads"
        RAG_CHUNK_SIZE: int = 500
        RAG_CHUNK_OVERLAP: int = 100
        RAG_TOP_K: int = 4
        RAG_SIMILARITY_THRESHOLD: float = 0.15

        ENABLE_SAFETY_GUARDRAILS: bool = True
        RATE_LIMIT_PER_MINUTE: int = 60
        MAX_UPLOAD_SIZE_MB: int = 15

    settings = Settings()

except Exception:
    # Fallback loader if pydantic_settings is not yet installed
    from dotenv import load_dotenv
    load_dotenv()

    class ManualSettings:
        def __init__(self):
            self.APP_ENV = os.getenv("APP_ENV", "development")
            self.APP_PORT = int(os.getenv("APP_PORT", 8000))
            self.FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 8501))
            self.BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

            self.DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/multimodal_chatbot")
            self.SQLITE_FALLBACK_URL = os.getenv("SQLITE_FALLBACK_URL", "sqlite:///./chatbot.db")

            self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

            self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            self.GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")

            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
            self.OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

            self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            self.GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

            self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
            self.CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            self.NANO_BANANA_MODEL = os.getenv("NANO_BANANA_MODEL", "nano-banana-2.1")
            self.CANVA_ENABLED = os.getenv("CANVA_ENABLED", "true").lower() in ("true", "1", "yes")

            self.VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "./storage/vector_db")
            self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./storage/uploads")
            self.RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", 500))
            self.RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", 100))
            self.RAG_TOP_K = int(os.getenv("RAG_TOP_K", 4))
            self.RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", 0.55))

            self.ENABLE_SAFETY_GUARDRAILS = os.getenv("ENABLE_SAFETY_GUARDRAILS", "true").lower() in ("true", "1", "yes")
            self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
            self.MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 15))

    settings = ManualSettings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
