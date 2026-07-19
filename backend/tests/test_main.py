from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app, get_openai_client


class FakeCompletions:
    async def create(self, **kwargs):
        assert kwargs["model"] == "test-model"
        assert kwargs["messages"] == [{"role": "user", "content": "Hello"}]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello from WorkTwin"))]
        )


class FakeChat:
    completions = FakeCompletions()


class FakeOpenAIClient:
    chat = FakeChat()


def test_health_does_not_expose_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "openai": "not_configured"}


def test_chat_uses_official_sdk_interface(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    get_settings.cache_clear()
    app.dependency_overrides[get_openai_client] = lambda: FakeOpenAIClient()

    try:
        response = TestClient(app).post("/api/chat", json={"message": "Hello"})
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()

    assert response.status_code == 200
    assert response.json() == {"model": "test-model", "reply": "Hello from WorkTwin"}

