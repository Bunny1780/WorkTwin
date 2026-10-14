"""API contracts for evidence-backed Twin endpoints."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


ResponseMode = Literal["advice", "implementation_plan", "code_draft"]
HUMAN_APPROVAL_POLICY = (
    "Twins may draft and advise from evidence, but deployment, pull-request approval, production changes, "
    "and access to restricted artifacts require human approval."
)


class TwinDirectoryEntry(BaseModel):
    id: UUID
    display_name: str
    role: str
    department: str
    employment_status: Literal["active", "departed"]
    departed_at: datetime | None = None
    expertise: list[str] = Field(default_factory=list)
    source_artifact_count: int = 0
    source_last_occurred_at: datetime | None = None
    derived_at: datetime | None = None


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
