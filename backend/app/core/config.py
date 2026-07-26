import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Report Assistant"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB Config
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://Olladapu_Shruthi:shruthi17925@shruthi.p5q77.mongodb.net/?appName=Shruthi")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "Mreport")
    
    # Paths & Storage
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DOCUMENTS_DIR: str = os.getenv("DOCUMENTS_DIR", os.path.join(BASE_DIR, "..", "documents"))
    UPLOAD_DIR: str = os.path.join(DOCUMENTS_DIR, "uploads")
    LOG_DIR: str = os.getenv("LOG_DIR", os.path.join(BASE_DIR, "logs"))
    LOG_FILE: str = os.getenv("LOG_FILE", os.path.join(LOG_DIR, "application.log"))
    
    # Ingestion Rules
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_MB: int = 25

    # AI & Pipeline Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    VECTOR_DB: str = "faiss"
    DEFAULT_LANGUAGE: str = "en"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# Ensure storage & log directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)
