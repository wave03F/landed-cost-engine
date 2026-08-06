from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Locate .env relative to this file (app/config.py → project root)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/landed_cost"
    test_database_url: str = "sqlite+aiosqlite:///./test.db"
    app_env: str = "development"
    log_level: str = "INFO"
    api_keys: list[str] = []  # Comma-separated API keys; empty = auth disabled

    # JWT
    jwt_secret: str = "change-me-in-production-use-long-random-string"

    # OAuth - Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # OAuth - GitHub
    github_client_id: str = ""
    github_client_secret: str = ""

    # URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # Rate limiting
    daily_calc_limit_user: int = 50
    daily_calc_limit_admin: int = 99999

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}

    @property
    def async_database_url(self) -> str:
        """Ensure the database URL uses the asyncpg driver.
        Render provides 'postgresql://' but SQLAlchemy async needs 'postgresql+asyncpg://'."""
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
