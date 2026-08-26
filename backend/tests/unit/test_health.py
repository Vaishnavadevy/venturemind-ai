"""Smoke test for the initial HTTP architecture."""

from fastapi.testclient import TestClient

from app.main import create_application


def test_health_endpoint_returns_standard_envelope() -> None:
    client = TestClient(create_application())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
