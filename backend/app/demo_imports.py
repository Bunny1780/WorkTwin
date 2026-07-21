"""Repeatable, provenance-preserving demo imports for WorkTwin."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from app.config import get_settings


ALLOWED_ACCESS_SCOPES = {"company_shared", "restricted"}
PROVIDERS = {"slack", "github", "email"}


@dataclass(frozen=True)
class DemoEmployee:
    key: str
    display_name: str
    role: str
    department: str
    identities: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class DemoArtifact:
    source_type: str
    source_external_id: str
    source_uri: str
    title: str
    content: str
    author_identity: tuple[str, str]
    occurred_at: str
    source_metadata: dict[str, Any]
    access_scope: str = "company_shared"
    project_context: dict[str, Any] | None = None


DEMO_ORGANIZATION = {"name": "Northstar Labs", "slug": "northstar-labs"}
DEMO_EMPLOYEES = (
    DemoEmployee(
        key="maya",
        display_name="Maya Chen",
        role="Product Manager",
        department="Product",
        identities=(
            {"provider": "slack", "external_id": "U-MAYA", "external_handle": "maya"},
            {"provider": "github", "external_id": "maya-chen", "external_handle": "mayachen"},
            {"provider": "email", "external_id": "maya@northstar.example", "email_address": "maya@northstar.example"},
        ),
    ),
    DemoEmployee(
        key="diego",
        display_name="Diego Ruiz",
        role="Staff Engineer",
        department="Engineering",
        identities=(
            {"provider": "slack", "external_id": "U-DIEGO", "external_handle": "diego"},
            {"provider": "github", "external_id": "druiz", "external_handle": "druiz"},
            {"provider": "email", "external_id": "diego@northstar.example", "email_address": "diego@northstar.example"},
        ),
    ),
)
DEMO_ARTIFACTS = (
    DemoArtifact(
        source_type="slack_thread",
        source_external_id="slack:C012-launch:1711962000.000100",
        source_uri="https://northstar.slack.com/archives/C012-launch/p1711962000000100",
        title="Launch channel: retry behavior",
        content="We should make retries visible in the launch dashboard before enabling the new workflow.",
        author_identity=("slack", "U-MAYA"),
        occurred_at="2025-04-01T09:00:00+00:00",
        source_metadata={"channel_id": "C012-launch", "thread_ts": "1711962000.000100"},
    ),
    DemoArtifact(
        source_type="github_pull_request",
        source_external_id="github:northstar/workflow-api:pr:42",
        source_uri="https://github.com/northstar/workflow-api/pull/42",
        title="Add retry telemetry to workflow runs",
        content="Adds structured retry events and exposes retry counts to the dashboard API.",
        author_identity=("github", "druiz"),
        occurred_at="2025-04-02T14:30:00+00:00",
        project_context={"repository": "northstar/workflow-api", "pull_request_number": 42},
        source_metadata={"pull_request_number": 42, "state": "merged"},
    ),
    DemoArtifact(
        source_type="email_thread",
        source_external_id="email:<launch-retries@northstar.example>",
        source_uri="mailto:launch-retries@northstar.example",
        title="Decision: retry telemetry before launch",
        content="Decision recorded: launch is approved once retry telemetry is visible to support and product.",
        author_identity=("email", "maya@northstar.example"),
        occurred_at="2025-04-03T08:15:00+00:00",
        access_scope="restricted",
        source_metadata={"message_id": "<launch-retries@northstar.example>", "to": ["diego@northstar.example"]},
    ),
)


def validate_demo_data() -> None:
    """Fail before any remote write when demo records break the import contract."""
    identities = {
        (identity["provider"], identity["external_id"])
        for employee in DEMO_EMPLOYEES
        for identity in employee.identities
    }
    artifact_providers = set()
    for artifact in DEMO_ARTIFACTS:
        provider = artifact.source_type.split("_", maxsplit=1)[0]
        artifact_providers.add(provider)
        if provider not in PROVIDERS or artifact.author_identity not in identities:
            raise ValueError(f"Artifact {artifact.source_external_id} has an unknown author identity.")
        if artifact.access_scope not in ALLOWED_ACCESS_SCOPES:
            raise ValueError(f"Artifact {artifact.source_external_id} has an invalid access scope.")
        if not artifact.source_uri or not artifact.content:
            raise ValueError(f"Artifact {artifact.source_external_id} is missing provenance.")
        datetime.fromisoformat(artifact.occurred_at)
    if artifact_providers != PROVIDERS:
        raise ValueError("Demo import must include Slack, GitHub, and email artifacts.")


class SupabaseDemoImporter:
    def __init__(self, url: str, service_role_key: str) -> None:
        self.url = url.rstrip("/")
        self.headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation,resolution=merge-duplicates",
        }

    async def request(self, method: str, table: str, **kwargs: Any) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.url, timeout=15.0) as client:
            response = await client.request(method, f"/rest/v1/{table}", headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def upsert(self, table: str, payload: dict[str, Any], conflict_target: str) -> dict[str, Any]:
        rows = await self.request("POST", table, params={"on_conflict": conflict_target}, json=payload)
        return rows[0]

    async def import_demo_data(self) -> dict[str, int]:
        validate_demo_data()
        organization = await self.upsert("organizations", DEMO_ORGANIZATION, "slug")
        employee_ids: dict[str, str] = {}
        identity_ids: dict[tuple[str, str], str] = {}

        for employee in DEMO_EMPLOYEES:
            rows = await self.request(
                "GET",
                "employees",
                params={
                    "select": "id",
                    "organization_id": f"eq.{organization['id']}",
                    "display_name": f"eq.{employee.display_name}",
                    "limit": "1",
                },
            )
            if rows:
                employee_id = rows[0]["id"]
            else:
                employee_id = (
                    await self.request(
                        "POST",
                        "employees",
                        json={
                            "organization_id": organization["id"],
                            "display_name": employee.display_name,
                            "role": employee.role,
                            "department": employee.department,
                        },
                    )
                )[0]["id"]
            employee_ids[employee.key] = employee_id
            for identity in employee.identities:
                row = await self.upsert(
                    "employee_source_identities",
                    {"employee_id": employee_id, **identity},
                    "provider,external_id",
                )
                identity_ids[(identity["provider"], identity["external_id"])] = row["id"]

        for artifact in DEMO_ARTIFACTS:
            identity_id = identity_ids[artifact.author_identity]
            employee_key = next(
                employee.key
                for employee in DEMO_EMPLOYEES
                if any(
                    (identity["provider"], identity["external_id"]) == artifact.author_identity
                    for identity in employee.identities
                )
            )
            await self.upsert(
                "work_artifacts",
                {
                    "organization_id": organization["id"],
                    "author_employee_id": employee_ids[employee_key],
                    "author_source_identity_id": identity_id,
                    "source_type": artifact.source_type,
                    "source_external_id": artifact.source_external_id,
                    "source_uri": artifact.source_uri,
                    "title": artifact.title,
                    "content": artifact.content,
                    "project_context": artifact.project_context or {},
                    "source_metadata": artifact.source_metadata,
                    "access_scope": artifact.access_scope,
                    "occurred_at": artifact.occurred_at,
                },
                "organization_id,source_type,source_external_id",
            )
        return {"employees": len(employee_ids), "identities": len(identity_ids), "artifacts": len(DEMO_ARTIFACTS)}


async def main() -> None:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before importing demo data.")
    result = await SupabaseDemoImporter(settings.supabase_url, settings.supabase_service_role_key).import_demo_data()
    print(f"Imported {result['employees']} employees, {result['identities']} identities, and {result['artifacts']} artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
