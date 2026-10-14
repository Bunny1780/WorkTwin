"""Supabase adapter for derived Twin profile persistence."""

from typing import Any

import httpx


class SupabaseProfileRepository:
    def __init__(self, url: str, service_role_key: str) -> None:
        self.url = url.rstrip("/")
        self.headers = {"apikey": service_role_key, "Authorization": f"Bearer {service_role_key}", "Content-Type": "application/json", "Prefer": "return=minimal,resolution=merge-duplicates"}

    async def request(self, method: str, table: str, **kwargs: Any) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.url, timeout=30.0) as client:
            response = await client.request(method, f"/rest/v1/{table}", headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else []

    async def list_employees(self) -> list[dict[str, Any]]:
        return await self.request("GET", "employees", params={"select": "id,display_name,role,department"})

    async def list_artifacts(self, employee_id: str) -> list[dict[str, Any]]:
        return await self.request("GET", "work_artifacts", params={"select": "id,source_type,title,content,occurred_at,source_uri", "author_employee_id": f"eq.{employee_id}", "order": "occurred_at.asc"})

    async def upsert_profile(self, payload: dict[str, Any]) -> None:
        await self.request("POST", "twin_profiles", params={"on_conflict": "employee_id"}, json=payload)
