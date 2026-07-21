import asyncio
import json
from types import SimpleNamespace

from app.derived_profiles import DerivedProfileGenerator


class FakeRepository:
    def __init__(self):
        self.profiles = []

    async def list_employees(self):
        return [
            {"id": "maya", "display_name": "Maya Chen", "role": "Product Manager", "department": "Product"},
            {"id": "unlinked", "display_name": "No Evidence", "role": "Designer", "department": "Design"},
        ]

    async def list_artifacts(self, employee_id):
        if employee_id == "unlinked":
            return []
        return [
            {
                "id": "slack-1",
                "source_type": "slack_thread",
                "title": "Retry behavior",
                "content": "Make retry behavior visible before launch.",
                "occurred_at": "2025-04-01T09:00:00+00:00",
                "source_uri": "https://example.test/slack/1",
            }
        ]

    async def upsert_profile(self, payload):
        self.profiles.append(payload)


class FakeCompletions:
    last_request = None

    async def create(self, **kwargs):
        type(self).last_request = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(
                            {
                                "expertise": ["Launch readiness"],
                                "ownership": ["Product launch criteria"],
                                "working_patterns": {"decision_style": "Makes observable criteria explicit"},
                                "communication_summary": "Concise and outcome-oriented in the available evidence.",
                            }
                        )
                    )
                )
            ]
        )


class FakeOpenAIClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def test_profile_generator_uses_evidence_and_skips_employees_without_artifacts():
    repository = FakeRepository()
    result = asyncio.run(DerivedProfileGenerator(repository, FakeOpenAIClient(), "test-model").refresh_profiles())

    assert result == {"refreshed": 1, "skipped": 1}
    assert FakeCompletions.last_request["model"] == "test-model"
    assert FakeCompletions.last_request["response_format"] == {"type": "json_object"}
    assert "Retry behavior" in FakeCompletions.last_request["messages"][1]["content"]
    assert repository.profiles[0]["source_artifact_count"] == 1
    assert repository.profiles[0]["generation_metadata"]["artifact_ids"] == ["slack-1"]
