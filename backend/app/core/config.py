import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Report Assistant"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Config
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "Mreport")
    
    # Paths & Storage
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", os.path.join(BASE_DIR, "..", "documents"))
    UPLOAD_DIR: str = os.path.join(DOCUMENTS_DIR, "uploads")
    LOG_DIR: str = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
    LOG_FILE: str = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "application.log"))
    VECTOR_STORE_DIR: str = os.getenv("VECTOR_STORE_DIR", os.path.join(BASE_DIR, "data", "vector_store"))
    
    # Ingestion Rules
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_MB: int = 25
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "")
    POPPLER_PATH: str = os.getenv("POPPLER_PATH", "")

    # AI & Pipeline Settings. LLM_* is provider-neutral; GROQ_* is retained only
    # for existing local installations until they migrate to LLM_*.
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")
    LLM_REQUIRED: bool = os.getenv("LLM_REQUIRED", "false").lower() == "true"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")
    MONGODB_REQUIRED: bool = os.getenv("MONGODB_REQUIRED", "false").lower() == "true"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    VECTOR_DB: str = "faiss"
    DEFAULT_LANGUAGE: str = "en"
    AUTH_SECRET_KEY: str = os.getenv("AUTH_SECRET_KEY", "development-only-change-me")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

# Ensure storage & log directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
