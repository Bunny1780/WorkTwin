"""Contracts for the legacy OpenAI connectivity endpoint."""

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=4_000)]
    agent_id: UUID | None = None


class ChatResponse(BaseModel):
    model: str
    reply: str
