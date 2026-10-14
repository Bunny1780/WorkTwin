"""API contracts for the legacy agent-profile endpoints."""

from uuid import UUID

from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    id: UUID
    name: str
    role: str
    department: str
    seniority: str
    expertise: list[str] = Field(default_factory=list)
    personality: dict[str, str] = Field(default_factory=dict)
    working_style: dict[str, str] = Field(default_factory=dict)


class AgentProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, min_length=1, max_length=120)
    department: str | None = Field(default=None, min_length=1, max_length=120)
    seniority: str | None = Field(default=None, min_length=1, max_length=80)
    expertise: list[str] | None = Field(default=None, max_length=30)
    personality: dict[str, str] | None = None
    working_style: dict[str, str] | None = None


class AgentProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    department: str = Field(min_length=1, max_length=120)
    seniority: str = Field(min_length=1, max_length=80)
    expertise: list[str] = Field(default_factory=list, max_length=30)
    personality: dict[str, str] = Field(default_factory=dict)
    working_style: dict[str, str] = Field(default_factory=dict)
