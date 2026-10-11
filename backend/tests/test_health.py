from fastapi.testclient import TestClient

from backend.main import app


def test_health_responds_even_without_database():
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
