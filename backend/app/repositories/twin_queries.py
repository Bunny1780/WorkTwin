"""Supabase adapter for Twin evidence retrieval and interaction auditing."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx
from fastapi import HTTPException, status


@dataclass(frozen=True)
class SupabaseTwinQueryRepository:
    url: str
    service_role_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {"apikey": self.service_role_key, "Authorization": f"Bearer {self.service_role_key}", "Content-Type": "application/json"}

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
        rows = await self.request("GET", "/rest/v1/employees", params={"select": "id,display_name,role,department,employment_status", "id": f"eq.{employee_id}", "limit": "1"})
        return rows[0] if rows else None

    async def get_profile(self, employee_id: UUID) -> dict[str, Any] | None:
        rows = await self.request("GET", "/rest/v1/twin_profiles", params={"select": "expertise,ownership,working_patterns,communication_summary", "employee_id": f"eq.{employee_id}", "limit": "1"})
        return rows[0] if rows else None

    async def match_memories(self, query_embedding: list[float], employee_id: UUID, include_company_shared: bool) -> list[dict[str, Any]]:
        return await self.request("POST", "/rest/v1/rpc/match_twin_memory_chunks", json={"query_embedding": query_embedding, "target_employee_id": str(employee_id), "include_company_shared": include_company_shared, "match_count": 8})

    async def record_interaction(self, payload: dict[str, Any]) -> None:
        await self.request("POST", "/rest/v1/twin_interactions", json=payload)
