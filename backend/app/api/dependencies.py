"""Shared FastAPI dependency providers."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from openai import AsyncOpenAI

from app.core.config import Settings, get_settings
from app.repositories.agents import SupabaseAgentRepository
from app.repositories.twin_queries import SupabaseTwinQueryRepository
from app.repositories.twins import SupabaseTwinRepository


def get_openai_client(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncOpenAI:
    if not settings.openai_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and set it.")
    return AsyncOpenAI(api_key=settings.openai_api_key)


def get_agents_repository(settings: Annotated[Settings, Depends(get_settings)]) -> SupabaseAgentRepository:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    return SupabaseAgentRepository(settings.supabase_url.rstrip("/"), settings.supabase_service_role_key)


def get_optional_agents_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseAgentRepository | None:
    """Provide legacy agent storage only when a chat request selects an agent."""
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None
    return SupabaseAgentRepository(settings.supabase_url.rstrip("/"), settings.supabase_service_role_key)


def get_twin_repository(settings: Annotated[Settings, Depends(get_settings)]) -> SupabaseTwinRepository:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    return SupabaseTwinRepository(settings.supabase_url.rstrip("/"), settings.supabase_service_role_key)


def get_twin_query_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseTwinQueryRepository:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )
    return SupabaseTwinQueryRepository(settings.supabase_url.rstrip("/"), settings.supabase_service_role_key)
