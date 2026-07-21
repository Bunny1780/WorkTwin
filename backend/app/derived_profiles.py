"""Generate evidence-backed Twin profiles from an employee's work artifacts."""

import asyncio
import json
from typing import Any, Protocol

import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import get_settings


class DerivedProfileContent(BaseModel):
    expertise: list[str] = Field(default_factory=list, max_length=8)
    ownership: list[str] = Field(default_factory=list, max_length=8)
    working_patterns: dict[str, str] = Field(default_factory=dict)
    communication_summary: str | None = Field(default=None, max_length=1000)


class ProfileRepository(Protocol):
    async def list_employees(self) -> list[dict[str, Any]]: ...

    async def list_artifacts(self, employee_id: str) -> list[dict[str, Any]]: ...

    async def upsert_profile(self, payload: dict[str, Any]) -> None: ...


class SupabaseProfileRepository:
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

    async def list_employees(self) -> list[dict[str, Any]]:
        return await self.request("GET", "employees", params={"select": "id,display_name,role,department"})

    async def list_artifacts(self, employee_id: str) -> list[dict[str, Any]]:
        return await self.request(
            "GET",
            "work_artifacts",
            params={
                "select": "id,source_type,title,content,occurred_at,source_uri",
                "author_employee_id": f"eq.{employee_id}",
                "order": "occurred_at.asc",
            },
        )

    async def upsert_profile(self, payload: dict[str, Any]) -> None:
        await self.request("POST", "twin_profiles", params={"on_conflict": "employee_id"}, json=payload)


def build_evidence_prompt(employee: dict[str, Any], artifacts: list[dict[str, Any]]) -> str:
    evidence = [
        {
            "source_type": artifact["source_type"],
            "title": artifact.get("title"),
            "content": artifact["content"],
            "occurred_at": artifact["occurred_at"],
            "source_uri": artifact["source_uri"],
        }
        for artifact in artifacts
    ]
    return (
        "Return a JSON object with exactly these keys: expertise (string array), ownership "
        "(string array), working_patterns (object of concise string values), and "
        "communication_summary (string or null). Derive only evidence-supported historical "
        "observations. Do not invent biography, personality traits, private facts, or current "
        "intent. If evidence is insufficient, return empty arrays/object and null.\n\n"
        f"Employee: {employee['display_name']}, {employee['role']} in {employee['department']}.\n"
        f"Evidence: {json.dumps(evidence, ensure_ascii=False)}"
    )


class DerivedProfileGenerator:
    def __init__(self, repository: ProfileRepository, client: AsyncOpenAI, model: str) -> None:
        self.repository = repository
        self.client = client
        self.model = model

    async def refresh_profiles(self) -> dict[str, int]:
        refreshed = 0
        skipped = 0
        for employee in await self.repository.list_employees():
            artifacts = await self.repository.list_artifacts(employee["id"])
            if not artifacts:
                skipped += 1
                continue
            completion = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You create concise, evidence-backed historical WorkTwin profiles. Return JSON only.",
                    },
                    {"role": "user", "content": build_evidence_prompt(employee, artifacts)},
                ],
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned an empty derived profile.")
            profile = DerivedProfileContent.model_validate_json(content)
            await self.repository.upsert_profile(
                {
                    "employee_id": employee["id"],
                    **profile.model_dump(mode="json"),
                    "source_artifact_count": len(artifacts),
                    "source_last_occurred_at": artifacts[-1]["occurred_at"],
                    "generation_metadata": {
                        "model": self.model,
                        "artifact_ids": [artifact["id"] for artifact in artifacts],
                        "source_types": sorted({artifact["source_type"] for artifact in artifacts}),
                    },
                }
            )
            refreshed += 1
        return {"refreshed": refreshed, "skipped": skipped}


async def main() -> None:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("Set OPENAI_API_KEY before generating derived profiles.")
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before generating derived profiles.")
    result = await DerivedProfileGenerator(
        SupabaseProfileRepository(settings.supabase_url, settings.supabase_service_role_key),
        AsyncOpenAI(api_key=settings.openai_api_key),
        settings.openai_model,
    ).refresh_profiles()
    print(f"Refreshed {result['refreshed']} profiles; skipped {result['skipped']} employees without artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
