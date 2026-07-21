"""Evidence-grounded Twin Q&A with scope-aware memory retrieval."""

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Literal, Protocol
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.artifact_embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from app.config import Settings, get_settings


ResponseMode = Literal["advice", "implementation_plan", "code_draft"]
HUMAN_APPROVAL_POLICY = (
    "Twins may draft and advise from evidence, but deployment, pull-request approval, production changes, "
    "and access to restricted artifacts require human approval."
)


class TwinQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)
    include_company_shared: bool = True
    response_mode: ResponseMode = "advice"


class EvidenceCitation(BaseModel):
    artifact_id: UUID
    source_type: str
    title: str | None = None
    occurred_at: datetime
    source_uri: str
    excerpt: str


class TwinQueryResponse(BaseModel):
    reply: str
    citations: list[EvidenceCitation]
    representation: Literal["current_evidence_based", "historical_evidence_based"]
    response_mode: ResponseMode
    human_approval_required: bool = True
    policy: str = HUMAN_APPROVAL_POLICY


class TwinQueryRepository(Protocol):
    async def get_employee(self, employee_id: UUID) -> dict[str, Any] | None: ...

    async def match_memories(
        self, query_embedding: list[float], employee_id: UUID, include_company_shared: bool
    ) -> list[dict[str, Any]]: ...

    async def record_interaction(self, payload: dict[str, Any]) -> None: ...


@dataclass(frozen=True)
class SupabaseTwinQueryRepository:
    url: str
    service_role_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }

    async def request(self, method: str, path: str, **kwargs: Any) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(base_url=self.url, timeout=20.0) as client:
                response = await client.request(method, path, headers=self.headers, **kwargs)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to reach Supabase.") from exc
        if response.is_error:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Supabase could not retrieve permitted memories.")
        return response.json() if response.content else []

    async def get_employee(self, employee_id: UUID) -> dict[str, Any] | None:
        rows = await self.request(
            "GET",
            "/rest/v1/employees",
            params={
                "select": "id,display_name,role,department,employment_status",
                "id": f"eq.{employee_id}",
                "limit": "1",
            },
        )
        return rows[0] if rows else None

    async def match_memories(
        self, query_embedding: list[float], employee_id: UUID, include_company_shared: bool
    ) -> list[dict[str, Any]]:
        return await self.request(
            "POST",
            "/rest/v1/rpc/match_twin_memory_chunks",
            json={
                "query_embedding": query_embedding,
                "target_employee_id": str(employee_id),
                "include_company_shared": include_company_shared,
                "match_count": 8,
            },
        )

    async def record_interaction(self, payload: dict[str, Any]) -> None:
        await self.request("POST", "/rest/v1/twin_interactions", json=payload)


def get_twin_query_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseTwinQueryRepository:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )
    return SupabaseTwinQueryRepository(settings.supabase_url.rstrip("/"), settings.supabase_service_role_key)


class TwinQueryService:
    def __init__(self, repository: TwinQueryRepository, client: AsyncOpenAI, model: str) -> None:
        self.repository = repository
        self.client = client
        self.model = model

    async def answer(self, employee_id: UUID, request: TwinQueryRequest) -> TwinQueryResponse:
        employee = await self.repository.get_employee(employee_id)
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee Twin not found.")
        embedding_response = await self.client.embeddings.create(model=EMBEDDING_MODEL, input=[request.question])
        query_embedding = embedding_response.data[0].embedding
        if len(query_embedding) != EMBEDDING_DIMENSIONS:
            raise HTTPException(status_code=502, detail="OpenAI returned an unexpected query embedding.")
        memories = await self.repository.match_memories(query_embedding, employee_id, request.include_company_shared)
        historical = employee["employment_status"] == "departed"
        citations = [
            EvidenceCitation(
                artifact_id=memory["artifact_id"],
                source_type=memory["source_type"],
                title=memory.get("title"),
                occurred_at=memory["occurred_at"],
                source_uri=memory["source_uri"],
                excerpt=memory["chunk_text"],
            )
            for memory in memories
        ]
        representation: Literal["current_evidence_based", "historical_evidence_based"] = (
            "historical_evidence_based" if historical else "current_evidence_based"
        )
        if not memories:
            response = TwinQueryResponse(
                reply="I don't have permitted organizational evidence to answer that question.",
                citations=[],
                representation=representation,
                response_mode=request.response_mode,
            )
            await self._record_interaction(employee_id, request, response)
            return response
        evidence = "\n\n".join(
            f"[{index}] {memory['source_type']} | {memory.get('title') or 'Untitled'} | {memory['occurred_at']}\n{memory['chunk_text']}"
            for index, memory in enumerate(memories, start=1)
        )
        system_message = (
            "Answer only from the supplied organizational evidence. State uncertainty when evidence is incomplete. "
            "Cite every substantive claim using the supplied bracketed evidence numbers. "
            "Do not claim personal experiences or present-day knowledge beyond the evidence."
        )
        if request.response_mode == "implementation_plan":
            system_message += " Provide an implementation plan, not an executed change."
        elif request.response_mode == "code_draft":
            system_message += " Provide a code draft only; do not claim it has been deployed, reviewed, or approved."
        system_message += f" {HUMAN_APPROVAL_POLICY}"
        if historical:
            system_message += " This is a historical evidence-based representation of a former employee, not a real-time message."
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Question: {request.question}\n\nEvidence:\n{evidence}"},
            ],
        )
        reply = completion.choices[0].message.content
        if not reply:
            raise HTTPException(status_code=502, detail="OpenAI returned an empty Twin answer.")
        response = TwinQueryResponse(
            reply=reply,
            citations=citations,
            representation=representation,
            response_mode=request.response_mode,
        )
        await self._record_interaction(employee_id, request, response)
        return response

    async def _record_interaction(
        self, employee_id: UUID, request: TwinQueryRequest, response: TwinQueryResponse
    ) -> None:
        await self.repository.record_interaction(
            {
                "employee_id": str(employee_id),
                "requested_action": request.question,
                "response_mode": request.response_mode,
                "include_company_shared": request.include_company_shared,
                "retrieved_evidence": [citation.model_dump(mode="json") for citation in response.citations],
                "response_text": response.reply,
            }
        )
