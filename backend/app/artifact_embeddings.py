"""CLI entry point for the artifact embedding worker."""

import asyncio
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.repositories.artifacts import SupabaseArtifactRepository
from app.services.artifact_embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    ArtifactEmbeddingWorker,
    ArtifactRepository,
    Chunk,
    chunk_content,
)


async def main() -> None:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("Set OPENAI_API_KEY before embedding artifacts.")
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before embedding artifacts.")
    worker = ArtifactEmbeddingWorker(
        SupabaseArtifactRepository(settings.supabase_url, settings.supabase_service_role_key),
        AsyncOpenAI(api_key=settings.openai_api_key),
    )
    result = await worker.embed_artifacts()
    print(f"Embedded {result['chunks']} chunks from {result['artifacts']} artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
