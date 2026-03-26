from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ─── Admin JWT ────────────────────────────────────────────────────────────
    ADMIN_JWT_SECRET: str = "cambiar-en-produccion"
    ADMIN_JWT_EXPIRE_HOURS: int = 24

    # ─── CORS ─────────────────────────────────────────────────────────────────
    # Separado por comas: "http://a.com,http://b.com"  o  "*"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:4173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ─── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ─── Pipeline ─────────────────────────────────────────────────────────────
    MAX_ITEMS_PER_RESPONSE: int = 5
    CONTEXT_WINDOW_MESSAGES: int = 10


settings = Settings()