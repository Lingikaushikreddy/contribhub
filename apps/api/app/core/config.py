"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ContribHub API configuration.

    All values are loaded from environment variables or a .env file
    located in the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "ContribHub API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Networking ───────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── Postgres ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://contribhub:contribhub@localhost:5432/contribhub"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # ── GitHub App ───────────────────────────────────────────────────────
    GITHUB_APP_ID: str = ""
    GITHUB_PRIVATE_KEY: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # ── AI / LLM ─────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Rate Limiting ────────────────────────────────────────────────────
    GITHUB_API_RATE_LIMIT: int = 5000
    GITHUB_API_RATE_WINDOW: int = 3600  # seconds

    @property
    def database_url_sync(self) -> str:
        """Return a synchronous database URL for Alembic migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
