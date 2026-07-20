from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.agents import AgentProfile, AgentProfileCreate, AgentProfileUpdate, get_agents_repository
from app.config import get_settings
from app.main import app, get_openai_client


class FakeCompletions:
    last_request = None

    async def create(self, **kwargs):
        self.last_request = kwargs
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Hello from WorkTwin"))]
        )


class FakeChat:
    completions = FakeCompletions()


class FakeOpenAIClient:
    chat = FakeChat()


class FakeAgentsRepository:
    profile = AgentProfile(
        id="8d2e5c50-7b1c-4d6e-a7ec-33c5cc7f1c01",
        name="Maya Chen",
        role="Product Manager",
        department="Product",
        seniority="Senior",
        expertise=["Roadmaps"],
        personality={"communication_style": "Concise"},
        working_style={"planning_process": "Outcome-first"},
    )

    async def list_profiles(self):
        return [self.profile]

    async def get_profile(self, agent_id):
        return self.profile if agent_id == self.profile.id else None

    async def update_profile(self, agent_id, update: AgentProfileUpdate):
        if agent_id != self.profile.id:
            return None
        return self.profile.model_copy(update=update.model_dump(exclude_none=True))

    async def create_profile(self, profile: AgentProfileCreate):
        return self.profile.model_copy(update=profile.model_dump())


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
    assert FakeOpenAIClient.chat.completions.last_request == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Hello"}],
    }


def test_frontend_origin_can_call_chat_api():
    response = TestClient(app).options(
        "/api/chat",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_agent_profiles_can_be_created_listed_and_updated():
    repository = FakeAgentsRepository()
    app.dependency_overrides[get_agents_repository] = lambda: repository

    try:
        create_response = TestClient(app).post(
            "/api/agents",
            json={
                "name": "Maya Chen",
                "role": "Product Manager",
                "department": "Product",
                "seniority": "Senior",
                "expertise": ["Roadmaps"],
            },
        )
        list_response = TestClient(app).get("/api/agents")
        update_response = TestClient(app).patch(
            f"/api/agents/{repository.profile.id}",
            json={"role": "Principal Product Manager", "expertise": ["Roadmaps", "Discovery"]},
        )
    finally:
        app.dependency_overrides.clear()

    assert create_response.status_code == 201
    assert create_response.json()["name"] == "Maya Chen"
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Maya Chen"
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "Principal Product Manager"
    assert update_response.json()["expertise"] == ["Roadmaps", "Discovery"]


def test_chat_uses_selected_agent_profile(monkeypatch):
    repository = FakeAgentsRepository()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    get_settings.cache_clear()
    app.dependency_overrides[get_openai_client] = lambda: FakeOpenAIClient()
    monkeypatch.setattr("app.main.get_agents_repository", lambda settings: repository)

    try:
        response = TestClient(app).post(
            "/api/chat",
            json={"message": "Hello", "agent_id": str(repository.profile.id)},
        )
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()

    assert response.status_code == 200
    messages = FakeOpenAIClient.chat.completions.last_request["messages"]
    assert messages[0]["role"] == "system"
    assert "Maya Chen" in messages[0]["content"]
    assert "Concise" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "Hello"}


def test_agents_api_requires_supabase_configuration(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    get_settings.cache_clear()

    response = TestClient(app).get("/api/agents")

    get_settings.cache_clear()
    assert response.status_code == 503
    assert response.json()["detail"].startswith("Supabase is not configured")
