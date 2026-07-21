import asyncio
from types import SimpleNamespace

from app.artifact_embeddings import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    ArtifactEmbeddingWorker,
    chunk_content,
)


class FakeRepository:
    def __init__(self):
        self.payloads = []

    async def list_artifacts(self):
        return [
            {"id": "artifact-1", "content": "First artifact content", "access_scope": "company_shared"},
            {"id": "artifact-2", "content": "Restricted email decision", "access_scope": "restricted"},
        ]

    async def upsert_chunks(self, payloads):
        self.payloads.extend(payloads)


class FakeEmbeddings:
    last_request = None

    async def create(self, **kwargs):
        type(self).last_request = kwargs
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=[0.1] * EMBEDDING_DIMENSIONS) for _ in kwargs["input"]]
        )


class FakeOpenAIClient:
    embeddings = FakeEmbeddings()


def test_chunk_content_keeps_word_boundaries_and_normalizes_whitespace():
    assert chunk_content("one   two\nthree", max_chars=7) == ["one two", "three"]


def test_embedding_worker_uses_official_embedding_interface_and_preserves_scope():
    repository = FakeRepository()
    result = asyncio.run(ArtifactEmbeddingWorker(repository, FakeOpenAIClient()).embed_artifacts())

    assert result == {"artifacts": 2, "chunks": 2}
    assert FakeEmbeddings.last_request == {
        "model": EMBEDDING_MODEL,
        "input": ["First artifact content", "Restricted email decision"],
    }
    assert repository.payloads[0]["artifact_id"] == "artifact-1"
    assert repository.payloads[1]["access_scope"] == "restricted"
    assert len(repository.payloads[0]["embedding"]) == EMBEDDING_DIMENSIONS
