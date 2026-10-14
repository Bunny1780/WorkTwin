"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    supabase_url: str | None
    supabase_service_role_key: str | None
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    configured_origins = tuple(
        origin.strip().rstrip("/")
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    )
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        cors_origins=configured_origins or ("http://localhost:5173", "http://127.0.0.1:5173"),
    )
