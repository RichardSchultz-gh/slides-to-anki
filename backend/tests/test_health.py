from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from backend.db import get_session
from backend.main import app


class FakeSession:
    """Ersetzt die echte DB-Session, damit beide Fälle unabhängig von Docker geprüft werden."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    async def execute(self, statement: object) -> None:
        if self.error is not None:
            raise self.error


@pytest.fixture
def client() -> Iterator[TestClient]:
    yield TestClient(app)
    app.dependency_overrides.clear()


def use_session(session: FakeSession) -> None:
    async def override() -> FakeSession:
        return session

    app.dependency_overrides[get_session] = override


def test_live_responds_without_touching_database(client: TestClient) -> None:
    use_session(FakeSession(error=OperationalError("SELECT 1", {}, Exception("refused"))))

    response = client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_when_database_reachable(client: TestClient) -> None:
    use_session(FakeSession())

    response = client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": True}


def test_ready_returns_503_when_database_unreachable(client: TestClient) -> None:
    use_session(FakeSession(error=OperationalError("SELECT 1", {}, Exception("refused"))))

    response = client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": False}
