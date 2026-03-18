from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ─── Base de datos ────────────────────────────────────────────────────────
    # Formato: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: str

    # ─── Anthropic ────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str
    HAIKU_MODEL: str = "claude-haiku-4-5-20251001"
    SONNET_MODEL: str = "claude-sonnet-4-6"

    # ─── Seguridad ────────────────────────────────────────────────────────────
    API_SECRET_KEY: str
    API_KEY_HEADER: str = "X-API-Key"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["*"]

    # ─── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ─── Pipeline ─────────────────────────────────────────────────────────────
    MAX_ITEMS_PER_RESPONSE: int = 5
    CONTEXT_WINDOW_MESSAGES: int = 10


settings = Settings()
