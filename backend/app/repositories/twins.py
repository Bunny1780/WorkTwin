"""Supabase adapter for the read-only Twin directory."""

from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.schemas.twins import TwinDirectoryEntry


@dataclass(frozen=True)
class SupabaseTwinRepository:
    url: str
    service_role_key: str

    @property
    def headers(self) -> dict[str, str]:
        return {"apikey": self.service_role_key, "Authorization": f"Bearer {self.service_role_key}"}

    async def request(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(base_url=self.url, timeout=10.0) as client:
                response = await client.get(f"/rest/v1/{table}", headers=self.headers, params=params)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to reach Supabase.") from exc
        if response.is_error:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Supabase could not load Twin profiles.")
        return response.json()

    async def list_directory(self) -> list[TwinDirectoryEntry]:
        employees = await self.request("employees", {"select": "id,display_name,role,department,employment_status,departed_at", "order": "employment_status.asc,display_name.asc"})
        profiles = await self.request("twin_profiles", {"select": "employee_id,expertise,source_artifact_count,source_last_occurred_at,derived_at"})
        profiles_by_employee = {profile["employee_id"]: profile for profile in profiles}
        return [TwinDirectoryEntry(**employee, expertise=profiles_by_employee.get(employee["id"], {}).get("expertise", []), source_artifact_count=profiles_by_employee.get(employee["id"], {}).get("source_artifact_count", 0), source_last_occurred_at=profiles_by_employee.get(employee["id"], {}).get("source_last_occurred_at"), derived_at=profiles_by_employee.get(employee["id"], {}).get("derived_at")) for employee in employees]
