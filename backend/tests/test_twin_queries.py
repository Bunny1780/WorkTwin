import asyncio
from types import SimpleNamespace
from uuid import UUID

from app.artifact_embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from app.twin_queries import TwinQueryRequest, TwinQueryService


class FakeRepository:
    def __init__(self):
        self.interactions = []

    async def get_employee(self, employee_id):
        return {"id": str(employee_id), "display_name": "Priya Nair", "employment_status": "departed"}

    async def match_memories(self, query_embedding, employee_id, include_company_shared):
        assert len(query_embedding) == EMBEDDING_DIMENSIONS
        assert include_company_shared is True
        return [
            {
                "artifact_id": "4a7c14d8-c77d-4713-b863-ec5d02c189a3",
                "source_type": "slack_thread",
                "title": "Launch channel: retry telemetry proposal",
                "occurred_at": "2025-04-01T09:00:00Z",
                "source_uri": "https://example.test/slack/1",
                "chunk_text": "Make retry counts visible before launch.",
            }
        ]

    async def record_interaction(self, payload):
        self.interactions.append(payload)


class FakeEmbeddings:
    last_request = None

    async def create(self, **kwargs):
        type(self).last_request = kwargs
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1] * EMBEDDING_DIMENSIONS)])


class FakeCompletions:
    last_request = None

    async def create(self, **kwargs):
        type(self).last_request = kwargs
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Retry telemetry was proposed before launch. [1]"))])


class FakeOpenAIClient:
    embeddings = FakeEmbeddings()
    chat = SimpleNamespace(completions=FakeCompletions())


def test_twin_query_grounds_a_historical_answer_and_returns_citations():
    employee_id = UUID("8d2e5c50-7b1c-4d6e-a7ec-33c5cc7f1c01")
    repository = FakeRepository()
    response = asyncio.run(
        TwinQueryService(repository, FakeOpenAIClient(), "test-model").answer(
            employee_id, TwinQueryRequest(question="What was required before launch?", response_mode="implementation_plan")
        )
    )

    assert FakeEmbeddings.last_request == {"model": EMBEDDING_MODEL, "input": ["What was required before launch?"]}
    assert FakeCompletions.last_request["model"] == "test-model"
    assert "historical evidence-based representation" in FakeCompletions.last_request["messages"][0]["content"]
    assert response.representation == "historical_evidence_based"
    assert response.response_mode == "implementation_plan"
    assert response.human_approval_required is True
    assert response.citations[0].source_type == "slack_thread"
    assert response.citations[0].source_uri == "https://example.test/slack/1"
    assert repository.interactions[0]["requested_action"] == "What was required before launch?"
    assert repository.interactions[0]["retrieved_evidence"][0]["artifact_id"] == "4a7c14d8-c77d-4713-b863-ec5d02c189a3"
