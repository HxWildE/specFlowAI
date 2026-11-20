from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration validated via Pydantic.
    Reads from environment variables and an optional .env file.
    """
    # Application Info
    PROJECT_NAME: str = "SpecFlow AI"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # PostgreSQL + pgvector
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: str = "postgresql+asyncpg://specflow:specflow_secret@localhost:5432/specflow_db"

    # Google Gemini API
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # File Ingestion
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 50

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def upload_path(self) -> Path:
        """Returns Path object for UPLOAD_DIR and ensures it exists."""
        p = Path(self.UPLOAD_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


# Singleton instance shared across the application
settings = Settings()
