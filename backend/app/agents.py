"""Supabase-backed agent profile storage."""

from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.config import Settings, get_settings


class AgentProfile(BaseModel):
    """A WorkTwin employee agent and the metadata that shapes its behavior."""

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


@dataclass(frozen=True)
class SupabaseAgentRepository:
    url: str
    service_role_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(base_url=self.url, timeout=10.0) as client:
                headers = self.headers
                if method in {"POST", "PATCH"}:
                    headers["Prefer"] = "return=representation"
                response = await client.request(
                    method,
                    "/rest/v1/agent_profiles",
                    headers=headers,
                    params=params,
                    json=json,
                )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to reach Supabase.",
            ) from exc

        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Supabase could not complete the agent profile request.",
            )
        return response.json()

    async def list_profiles(self) -> list[AgentProfile]:
        rows = await self._request("GET", params={"select": "*", "order": "name.asc"})
        return [AgentProfile.model_validate(row) for row in rows]

    async def get_profile(self, agent_id: UUID) -> AgentProfile | None:
        rows = await self._request(
            "GET",
            params={"select": "*", "id": f"eq.{agent_id}", "limit": "1"},
        )
        return AgentProfile.model_validate(rows[0]) if rows else None

    async def update_profile(
        self,
        agent_id: UUID,
        update: AgentProfileUpdate,
    ) -> AgentProfile | None:
        payload = update.model_dump(exclude_none=True, mode="json")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provide at least one profile field to update.",
            )
        rows = await self._request(
            "PATCH",
            params={"id": f"eq.{agent_id}"},
            json=payload,
        )
        return AgentProfile.model_validate(rows[0]) if rows else None

    async def create_profile(self, profile: AgentProfileCreate) -> AgentProfile:
        rows = await self._request("POST", json=profile.model_dump(mode="json"))
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Supabase did not return the created agent profile.",
            )
        return AgentProfile.model_validate(rows[0])


def get_agents_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseAgentRepository:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
        )
    return SupabaseAgentRepository(
        url=settings.supabase_url.rstrip("/"),
        service_role_key=settings.supabase_service_role_key,
    )
