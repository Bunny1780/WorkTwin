"""CLI entry point for derived Twin profile generation."""

import asyncio
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.repositories.profiles import SupabaseProfileRepository
from app.services.derived_profiles import DerivedProfileContent, DerivedProfileGenerator, ProfileRepository, build_evidence_prompt


async def main() -> None:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("Set OPENAI_API_KEY before generating derived profiles.")
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before generating derived profiles.")
    result = await DerivedProfileGenerator(
        SupabaseProfileRepository(settings.supabase_url, settings.supabase_service_role_key),
        AsyncOpenAI(api_key=settings.openai_api_key),
        settings.openai_model,
    ).refresh_profiles()
    print(f"Refreshed {result['refreshed']} profiles; skipped {result['skipped']} employees without artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
