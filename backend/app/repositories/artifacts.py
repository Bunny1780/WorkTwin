"""Supabase adapter for normalized artifacts and memory chunks."""

from typing import Any

import httpx


class SupabaseArtifactRepository:
    def __init__(self, url: str, service_role_key: str) -> None:
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates",
        }

    async def request(self, method: str, table: str, **kwargs: Any) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.url, timeout=30.0) as client:
            response = await client.request(method, f"/rest/v1/{table}", headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else []

    async def list_artifacts(self) -> list[dict[str, Any]]:
        return await self.request("GET", "work_artifacts", params={"select": "id,content,access_scope"})

    async def upsert_chunks(self, payloads: list[dict[str, Any]]) -> None:
        if payloads:
            await self.request("POST", "memory_chunks", params={"on_conflict": "artifact_id,chunk_index"}, json=payloads)
