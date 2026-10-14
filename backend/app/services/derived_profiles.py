"""Generate evidence-backed Twin profiles from linked work artifacts."""

import json
from typing import Any, Protocol

from openai import AsyncOpenAI
from pydantic import BaseModel, Field


class DerivedProfileContent(BaseModel):
    expertise: list[str] = Field(default_factory=list, max_length=8)
    ownership: list[str] = Field(default_factory=list, max_length=8)
    working_patterns: dict[str, str] = Field(default_factory=dict)
    communication_summary: str | None = Field(default=None, max_length=1000)


class ProfileRepository(Protocol):
    async def list_employees(self) -> list[dict[str, Any]]: ...
    async def list_artifacts(self, employee_id: str) -> list[dict[str, Any]]: ...
    async def upsert_profile(self, payload: dict[str, Any]) -> None: ...


def build_evidence_prompt(employee: dict[str, Any], artifacts: list[dict[str, Any]]) -> str:
    evidence = [{"source_type": artifact["source_type"], "title": artifact.get("title"), "content": artifact["content"], "occurred_at": artifact["occurred_at"], "source_uri": artifact["source_uri"]} for artifact in artifacts]
    return (
        "Return a JSON object with exactly these keys: expertise (string array), ownership (string array), working_patterns (object of concise string values), and communication_summary (string or null). "
        "Derive only evidence-supported historical observations. Do not invent biography, personality traits, private facts, or current intent. If evidence is insufficient, return empty arrays/object and null.\n\n"
        f"Employee: {employee['display_name']}, {employee['role']} in {employee['department']}.\nEvidence: {json.dumps(evidence, ensure_ascii=False)}"
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
            completion = await self.client.chat.completions.create(model=self.model, response_format={"type": "json_object"}, messages=[{"role": "system", "content": "You create concise, evidence-backed historical WorkTwin profiles. Return JSON only."}, {"role": "user", "content": build_evidence_prompt(employee, artifacts)}])
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned an empty derived profile.")
            profile = DerivedProfileContent.model_validate_json(content)
            await self.repository.upsert_profile({"employee_id": employee["id"], **profile.model_dump(mode="json"), "source_artifact_count": len(artifacts), "source_last_occurred_at": artifacts[-1]["occurred_at"], "generation_metadata": {"model": self.model, "artifact_ids": [artifact["id"] for artifact in artifacts], "source_types": sorted({artifact["source_type"] for artifact in artifacts})}})
            refreshed += 1
        return {"refreshed": refreshed, "skipped": skipped}
