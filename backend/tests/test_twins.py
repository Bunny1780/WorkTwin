from fastapi.testclient import TestClient

from app.main import app
from app.twins import get_twin_repository


class FakeTwinRepository:
    async def list_directory(self):
        return [
            {
                "id": "8d2e5c50-7b1c-4d6e-a7ec-33c5cc7f1c01",
                "display_name": "Maya Chen",
                "role": "Product Manager",
                "department": "Product",
                "employment_status": "active",
                "expertise": ["Launch readiness"],
                "source_artifact_count": 1,
            },
            {
                "id": "4a7c14d8-c77d-4713-b863-ec5d02c189a3",
                "display_name": "Priya Nair",
                "role": "Staff Engineer",
                "department": "Engineering",
                "employment_status": "departed",
                "departed_at": "2025-04-15T17:00:00Z",
                "expertise": ["Observability"],
                "source_artifact_count": 1,
            },
        ]


def test_twin_directory_distinguishes_active_and_departed_employees():
    app.dependency_overrides[get_twin_repository] = lambda: FakeTwinRepository()
    try:
        response = TestClient(app).get("/api/twins")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert [entry["employment_status"] for entry in payload] == ["active", "departed"]
    assert payload[1]["display_name"] == "Priya Nair"
    assert payload[1]["departed_at"] == "2025-04-15T17:00:00Z"
