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
    employment_status: str = "active"
    departed_at: str | None = None


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
    DemoEmployee(
        key="priya",
        display_name="Priya Nair",
        role="Staff Engineer",
        department="Engineering",
        employment_status="departed",
        departed_at="2025-04-15T17:00:00+00:00",
        identities=(
            {"provider": "slack", "external_id": "U-PRIYA", "external_handle": "priya"},
            {"provider": "github", "external_id": "priya-nair", "external_handle": "priyanair"},
            {"provider": "email", "external_id": "priya@northstar.example", "email_address": "priya@northstar.example"},
        ),
    ),
)
DEMO_ARTIFACTS = (
    DemoArtifact(
        source_type="slack_thread",
        source_external_id="slack:C012-launch:1711962000.000100",
        source_uri="https://northstar.slack.com/archives/C012-launch/p1711962000000100",
        title="Launch channel: retry telemetry proposal",
        content="Before launch, we should make retry counts and failure reasons visible in the dashboard so support can diagnose workflow issues.",
        author_identity=("slack", "U-PRIYA"),
        occurred_at="2025-04-01T09:00:00+00:00",
        source_metadata={"channel_id": "C012-launch", "thread_ts": "1711962000.000100", "topic": "launch telemetry"},
    ),
    DemoArtifact(
        source_type="github_pull_request",
        source_external_id="github:northstar/workflow-api:pr:42",
        source_uri="https://github.com/northstar/workflow-api/pull/42",
        title="Add retry telemetry to workflow runs",
        content="Implements Priya's launch-telemetry proposal: structured retry events, failure reasons, and retry counts in the dashboard API.",
        author_identity=("github", "druiz"),
        occurred_at="2025-04-02T14:30:00+00:00",
        project_context={"repository": "northstar/workflow-api", "pull_request_number": 42},
        source_metadata={"pull_request_number": 42, "state": "merged"},
    ),
    DemoArtifact(
        source_type="email_thread",
        source_external_id="email:<launch-retries@northstar.example>",
        source_uri="mailto:launch-retries@northstar.example",
        title="Decision: require retry telemetry before launch",
        content="Decision recorded: launch is approved once Diego's PR makes Priya's retry telemetry visible to Support and Product.",
        author_identity=("email", "maya@northstar.example"),
        occurred_at="2025-04-03T08:15:00+00:00",
        access_scope="restricted",
        source_metadata={
            "message_id": "<launch-retries@northstar.example>",
            "to": ["diego@northstar.example", "priya@northstar.example"],
            "decision": "retry telemetry is a launch criterion",
        },
    ),
    DemoArtifact(
        source_type="slack_message",
        source_external_id="slack:C024-discovery:1712048400.000200",
        source_uri="https://northstar.slack.com/archives/C024-discovery/p1712048400000200",
        title="Discovery channel: activation metric question",
        content="I want the activation definition written before we instrument it: a workspace has connected a source, invited a teammate, and viewed its first evidence-backed answer. Otherwise we will optimize a vague number.",
        author_identity=("slack", "U-MAYA"),
        occurred_at="2025-04-02T09:00:00+00:00",
        source_metadata={"channel_id": "C024-discovery", "topic": "activation metric"},
    ),
    DemoArtifact(
        source_type="github_issue",
        source_external_id="github:northstar/worktwin-web:issue:18",
        source_uri="https://github.com/northstar/worktwin-web/issues/18",
        title="Define activation funnel events",
        content="Maya's acceptance criteria: name each event, state its user value, and include a dashboard query. Do not add events merely because they are easy to emit.",
        author_identity=("github", "maya-chen"),
        occurred_at="2025-04-04T10:20:00+00:00",
        project_context={"repository": "northstar/worktwin-web", "issue_number": 18},
        source_metadata={"issue_number": 18, "labels": ["product", "analytics"]},
    ),
    DemoArtifact(
        source_type="email_message",
        source_external_id="email:<activation-review@northstar.example>",
        source_uri="mailto:activation-review@northstar.example",
        title="Activation review: defer the vanity dashboard",
        content="Decision: ship the three activation events first and defer the executive dashboard. The goal is to learn where users stop, not to create a polished report before the data is trustworthy.",
        author_identity=("email", "maya@northstar.example"),
        occurred_at="2025-04-07T16:00:00+00:00",
        source_metadata={"message_id": "<activation-review@northstar.example>", "decision": "defer vanity dashboard"},
    ),
    DemoArtifact(
        source_type="slack_thread",
        source_external_id="slack:C031-platform:1712134800.000300",
        source_uri="https://northstar.slack.com/archives/C031-platform/p1712134800000300",
        title="Platform channel: import idempotency",
        content="The importer must treat source IDs as the durable key. A retry should converge on the same record; adding a client-side dedupe cache only hides the real contract.",
        author_identity=("slack", "U-DIEGO"),
        occurred_at="2025-04-03T11:00:00+00:00",
        source_metadata={"channel_id": "C031-platform", "topic": "idempotent imports"},
    ),
    DemoArtifact(
        source_type="github_review",
        source_external_id="github:northstar/workflow-api:pr:47:review:1",
        source_uri="https://github.com/northstar/workflow-api/pull/47#pullrequestreview-1",
        title="Review: preserve source identity on retries",
        content="Diego requested an upsert on organization, source type, and external ID, plus a regression test for replaying the same event. He rejected a timestamp-based duplicate heuristic as unsafe.",
        author_identity=("github", "druiz"),
        occurred_at="2025-04-05T13:40:00+00:00",
        project_context={"repository": "northstar/workflow-api", "pull_request_number": 47},
        source_metadata={"pull_request_number": 47, "state": "approved"},
    ),
    DemoArtifact(
        source_type="email_message",
        source_external_id="email:<import-slo@northstar.example>",
        source_uri="mailto:import-slo@northstar.example",
        title="Importer SLO and rollback notes",
        content="Diego documented the rollout gate: measure failed imports by provider, alert on sustained errors, and keep the previous importer path available until replay tests pass in production-like data.",
        author_identity=("email", "diego@northstar.example"),
        occurred_at="2025-04-08T15:10:00+00:00",
        source_metadata={"message_id": "<import-slo@northstar.example>", "topic": "reliability"},
    ),
    DemoArtifact(
        source_type="slack_message",
        source_external_id="slack:C031-platform:1712221200.000400",
        source_uri="https://northstar.slack.com/archives/C031-platform/p1712221200000400",
        title="Platform channel: failure-mode checklist",
        content="Before merging, list the failure mode, the observable signal, and the recovery path. If we cannot explain how an operator notices it, the feature is not ready.",
        author_identity=("slack", "U-DIEGO"),
        occurred_at="2025-04-04T12:00:00+00:00",
        source_metadata={"channel_id": "C031-platform", "topic": "operational readiness"},
    ),
    DemoArtifact(
        source_type="github_commit",
        source_external_id="github:northstar/memory-worker:commit:9f5c1a2",
        source_uri="https://github.com/northstar/memory-worker/commit/9f5c1a2",
        title="Chunk imports by decision boundary",
        content="Priya split long source records at decision boundaries and retained surrounding context. Her commit notes that retrieval quality suffers when a chunk mixes rationale, implementation, and a later status update.",
        author_identity=("github", "priya-nair"),
        occurred_at="2025-03-25T10:35:00+00:00",
        project_context={"repository": "northstar/memory-worker", "commit_sha": "9f5c1a2"},
        source_metadata={"commit_sha": "9f5c1a2"},
    ),
    DemoArtifact(
        source_type="email_thread",
        source_external_id="email:<citation-contract@northstar.example>",
        source_uri="mailto:citation-contract@northstar.example",
        title="Citation contract for Twin answers",
        content="Priya's proposal: every substantive answer should return the source type, timestamp, excerpt, and canonical URL. A confident answer without a source is a product defect, not a UX detail.",
        author_identity=("email", "priya@northstar.example"),
        occurred_at="2025-03-28T14:00:00+00:00",
        source_metadata={"message_id": "<citation-contract@northstar.example>", "topic": "evidence UX"},
    ),
    DemoArtifact(
        source_type="slack_thread",
        source_external_id="slack:C042-trust:1711702800.000500",
        source_uri="https://northstar.slack.com/archives/C042-trust/p1711702800000500",
        title="Trust channel: restricted email handling",
        content="Restricted email must not become retrievable merely because a related Slack thread is shared. Priya asked for scope enforcement in retrieval, not a warning after the model has already seen the content.",
        author_identity=("slack", "U-PRIYA"),
        occurred_at="2025-03-29T08:20:00+00:00",
        source_metadata={"channel_id": "C042-trust", "topic": "access scope"},
    ),
    DemoArtifact(
        source_type="github_pull_request",
        source_external_id="github:northstar/memory-worker:pr:31",
        source_uri="https://github.com/northstar/memory-worker/pull/31",
        title="Return citations with retrieval results",
        content="Priya implemented evidence citations alongside memory matches and added cases for missing URLs. The PR prioritizes an inspectable evidence trail over a more conversational but opaque response.",
        author_identity=("github", "priya-nair"),
        occurred_at="2025-04-01T16:45:00+00:00",
        project_context={"repository": "northstar/memory-worker", "pull_request_number": 31},
        source_metadata={"pull_request_number": 31, "state": "merged"},
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
    artifacts_by_employee = {
        employee.key: sum(
            artifact.author_identity in {(identity["provider"], identity["external_id"]) for identity in employee.identities}
            for artifact in DEMO_ARTIFACTS
        )
        for employee in DEMO_EMPLOYEES
    }
    if any(count < 4 for count in artifacts_by_employee.values()):
        raise ValueError("Each demo employee must have enough artifacts to establish a distinct evidence-backed voice.")


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
            employee_payload = {
                "organization_id": organization["id"],
                "display_name": employee.display_name,
                "role": employee.role,
                "department": employee.department,
                "employment_status": employee.employment_status,
                "departed_at": employee.departed_at,
            }
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
                        json=employee_payload,
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
