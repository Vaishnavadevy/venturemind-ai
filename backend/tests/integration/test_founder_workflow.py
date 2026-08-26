from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_application


def _payload() -> dict[str, object]:
    return {
        "startup_name": "Tea House",
        "industry": "Commerce",
        "country": "Sri Lanka",
        "target_audience": "elders",
        "problem_statement": "entertainment",
        "proposed_solution": "make tea shop",
        "business_model": "Local tea service for community gatherings.",
        "revenue_model": "Tea and snack sales at each gathering.",
        "development_stage": "idea",
        "budget_amount": 5000,
        "budget_currency": "USD",
        "competitors": [],
        "additional_notes": None,
    }


def _client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_session() -> Generator[Session, None, None]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app = create_application()
    app.dependency_overrides[get_db_session] = override_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def _register_and_login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test Founder", "email": email, "password": "correct-horse-123"},
    )
    assert response.status_code == 201
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "correct-horse-123"}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_founder_can_submit_view_and_export_an_evaluation() -> None:
    client = next(_client())
    headers = _register_and_login(client, "founder@example.com")
    created = client.post("/api/v1/projects", json=_payload(), headers=headers)
    assert created.status_code == 201
    data = created.json()["data"]

    projects = client.get("/api/v1/projects", headers=headers)
    assert projects.status_code == 200
    assert projects.json()["data"][0]["latest_score"] is not None

    evaluation = client.get(
        f"/api/v1/projects/{data['project']['id']}/evaluations/{data['evaluation_id']}", headers=headers
    )
    assert evaluation.status_code == 200
    assert len(evaluation.json()["data"]["scores"]) == 8

    report = client.post(
        f"/api/v1/projects/{data['project']['id']}/evaluations/{data['evaluation_id']}/report",
        headers=headers,
    )
    assert report.status_code == 200
    assert report.headers["content-type"] == "application/pdf"


def test_api_rejects_invalid_and_unauthorized_requests() -> None:
    client = next(_client())
    headers = _register_and_login(client, "owner@example.com")
    invalid = client.post("/api/v1/projects", json={"startup_name": "x"}, headers=headers)
    assert invalid.status_code == 422

    created = client.post("/api/v1/projects", json=_payload(), headers=headers).json()["data"]
    other_headers = _register_and_login(client, "other@example.com")
    denied = client.get(
        f"/api/v1/projects/{created['project']['id']}/evaluations/{created['evaluation_id']}",
        headers=other_headers,
    )
    assert denied.status_code == 404
    admin = client.get("/api/v1/admin/analytics", headers=headers)
    assert admin.status_code == 403
