"""Evidence-grounded Twin answer generation."""

from typing import Any, Protocol
from uuid import UUID

from fastapi import HTTPException
from openai import AsyncOpenAI

from app.services.artifact_embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from app.schemas.twins import EvidenceCitation, HUMAN_APPROVAL_POLICY, TwinQueryRequest, TwinQueryResponse


class TwinQueryRepository(Protocol):
    async def get_employee(self, employee_id: UUID) -> dict[str, Any] | None: ...
    async def get_profile(self, employee_id: UUID) -> dict[str, Any] | None: ...
    async def match_memories(self, query_embedding: list[float], employee_id: UUID, include_company_shared: bool) -> list[dict[str, Any]]: ...
    async def record_interaction(self, payload: dict[str, Any]) -> None: ...


class TwinQueryService:
    def __init__(self, repository: TwinQueryRepository, client: AsyncOpenAI, model: str) -> None:
        self.repository = repository
        self.client = client
        self.model = model

    async def answer(self, employee_id: UUID, request: TwinQueryRequest) -> TwinQueryResponse:
        employee = await self.repository.get_employee(employee_id)
        if employee is None:
            raise HTTPException(status_code=404, detail="Employee Twin not found.")
        profile = await self.repository.get_profile(employee_id)
        embedding_response = await self.client.embeddings.create(model=EMBEDDING_MODEL, input=[request.question])
        query_embedding = embedding_response.data[0].embedding
        if len(query_embedding) != EMBEDDING_DIMENSIONS:
            raise HTTPException(status_code=502, detail="OpenAI returned an unexpected query embedding.")
        memories = await self.repository.match_memories(query_embedding, employee_id, request.include_company_shared)
        historical = employee["employment_status"] == "departed"
        citations = [EvidenceCitation(artifact_id=memory["artifact_id"], source_type=memory["source_type"], title=memory.get("title"), occurred_at=memory["occurred_at"], source_uri=memory["source_uri"], excerpt=memory["chunk_text"]) for memory in memories]
        representation = "historical_evidence_based" if historical else "current_evidence_based"
        if not memories:
            response = TwinQueryResponse(reply="I don't have permitted organizational evidence to answer that question.", citations=[], representation=representation, response_mode=request.response_mode)
            await self._record_interaction(employee_id, request, response)
            return response
        evidence = "\n\n".join(f"[{index}] {memory['source_type']} | {memory.get('title') or 'Untitled'} | {memory['occurred_at']}\n{memory['chunk_text']}" for index, memory in enumerate(memories, start=1))
        system_message = (
            "Answer only from the supplied organizational evidence. State uncertainty when evidence is incomplete. "
            "Cite every substantive claim using the supplied bracketed evidence numbers. "
            "Do not claim personal experiences or present-day knowledge beyond the evidence. "
            "Use the documented communication summary and working patterns to shape organization, level of detail, "
            "and tone, but do not exaggerate them into a fictional persona or invent traits."
        )
        if profile:
            system_message += f" Documented Twin profile: {{'expertise': {profile.get('expertise', [])}, 'ownership': {profile.get('ownership', [])}, 'working_patterns': {profile.get('working_patterns', {})}, 'communication_summary': {profile.get('communication_summary')}}}."
        if request.response_mode == "implementation_plan":
            system_message += " Provide an implementation plan, not an executed change."
        elif request.response_mode == "code_draft":
            system_message += " Provide a code draft only; do not claim it has been deployed, reviewed, or approved."
        system_message += f" {HUMAN_APPROVAL_POLICY}"
        if historical:
            system_message += " This is a historical evidence-based representation of a former employee, not a real-time message."
        completion = await self.client.chat.completions.create(model=self.model, messages=[{"role": "system", "content": system_message}, {"role": "user", "content": f"Question: {request.question}\n\nEvidence:\n{evidence}"}])
        reply = completion.choices[0].message.content
        if not reply:
            raise HTTPException(status_code=502, detail="OpenAI returned an empty Twin answer.")
        response = TwinQueryResponse(reply=reply, citations=citations, representation=representation, response_mode=request.response_mode)
        await self._record_interaction(employee_id, request, response)
        return response

    async def _record_interaction(self, employee_id: UUID, request: TwinQueryRequest, response: TwinQueryResponse) -> None:
        await self.repository.record_interaction({"employee_id": str(employee_id), "requested_action": request.question, "response_mode": request.response_mode, "include_company_shared": request.include_company_shared, "retrieved_evidence": [citation.model_dump(mode="json") for citation in response.citations], "response_text": response.reply})
