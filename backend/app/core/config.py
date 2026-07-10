from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file: backend/app/core/config.py → project root .env
# In Docker, env vars come from docker-compose env_file, so missing .env is fine.
_env_path = Path(__file__).resolve().parents[3] / ".env"

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-2.0-flash"
    # Redis connection URL used by both the API (to enqueue) and the worker.
    # Override via REDIS_URL env var or .env file for non-local environments.
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Google OAuth 2.0 ──────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=str(_env_path) if _env_path.exists() else None,
        extra="ignore",
    )

settings = Settings()