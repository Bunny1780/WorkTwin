"""Chunk imported artifacts and store OpenAI embeddings in Supabase."""

import asyncio
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from openai import AsyncOpenAI

from app.config import get_settings


EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
MAX_CHUNK_CHARS = 800
EMBEDDING_BATCH_SIZE = 100


@dataclass(frozen=True)
class Chunk:
    artifact_id: str
    chunk_index: int
    chunk_text: str
    access_scope: str


class ArtifactRepository(Protocol):
    async def list_artifacts(self) -> list[dict[str, Any]]: ...

    async def upsert_chunks(self, payloads: list[dict[str, Any]]) -> None: ...


def chunk_content(content: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split normalized text into stable, word-boundary chunks."""
    words = content.split()
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0
    for word in words:
        separator = 1 if current else 0
        if current and current_length + separator + len(word) > max_chars:
            chunks.append(" ".join(current))
            current = []
            current_length = 0
            separator = 0
        current.append(word)
        current_length += separator + len(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


class SupabaseArtifactRepository:
    def __init__(self, url: str, service_role_key: str) -> None:
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates",
        }

    async def request(self, method: str, table: str, **kwargs: Any) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.url, timeout=30.0) as client:
            response = await client.request(method, f"/rest/v1/{table}", headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else []

    async def list_artifacts(self) -> list[dict[str, Any]]:
        return await self.request("GET", "work_artifacts", params={"select": "id,content,access_scope"})

    async def upsert_chunks(self, payloads: list[dict[str, Any]]) -> None:
        if payloads:
            await self.request(
                "POST",
                "memory_chunks",
                params={"on_conflict": "artifact_id,chunk_index"},
                json=payloads,
            )


class ArtifactEmbeddingWorker:
    def __init__(self, repository: ArtifactRepository, client: AsyncOpenAI) -> None:
        self.repository = repository
        self.client = client

    async def embed_artifacts(self) -> dict[str, int]:
        artifacts = await self.repository.list_artifacts()
        chunks = [
            Chunk(
                artifact_id=artifact["id"],
                chunk_index=index,
                chunk_text=chunk_text,
                access_scope=artifact["access_scope"],
            )
            for artifact in artifacts
            for index, chunk_text in enumerate(chunk_content(artifact["content"]))
        ]
        for batch_start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
            batch = chunks[batch_start : batch_start + EMBEDDING_BATCH_SIZE]
            response = await self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[chunk.chunk_text for chunk in batch],
            )
            vectors = [item.embedding for item in response.data]
            if len(vectors) != len(batch) or any(len(vector) != EMBEDDING_DIMENSIONS for vector in vectors):
                raise ValueError("OpenAI returned an unexpected embedding count or dimension.")
            await self.repository.upsert_chunks(
                [
                    {
                        "artifact_id": chunk.artifact_id,
                        "chunk_index": chunk.chunk_index,
                        "chunk_text": chunk.chunk_text,
                        "embedding": vector,
                        "access_scope": chunk.access_scope,
                    }
                    for chunk, vector in zip(batch, vectors, strict=True)
                ]
            )
        return {"artifacts": len(artifacts), "chunks": len(chunks)}


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
