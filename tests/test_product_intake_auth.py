"""Product Intake pilot authorization regression tests.

These tests prove the dev/pilot operator session is separate from the
roleless customer session and that Product creation remains server-governed.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db
from app.models import Base, UserRole


@pytest.fixture()
def api_env(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "development")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = Session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db
    client = TestClient(fastapi_app)

    yield client, db

    fastapi_app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_pilot_operator_token_grants_editor_and_product_create_is_draft(api_env):
    client, db = api_env

    token_response = client.post("/api/v1/auth/pilot-operator-token")
    assert token_response.status_code == 200, token_response.text
    token = token_response.json()["access_token"]

    role = (
        db.query(UserRole)
        .filter(
            UserRole.subject_id == "USR_PILOT_EDITOR",
            UserRole.role == "Editor",
        )
        .first()
    )
    assert role is not None

    response = client.post(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": "PILOT-AUTH-001",
            "brand": "HBI Test",
            "product_name": "Pilot Auth Product",
            "variant": "clear",
            "size_value": 50,
            "size_unit": "ml",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["product_id"] == "PILOT-AUTH-001"
    assert body["status"] == "DRAFT"
    assert body["identity_status"] == "NEEDS_REVIEW"
    assert body["qa_verdict"] == "PENDING"


def test_pilot_operator_token_disabled_in_production(api_env, monkeypatch):
    client, _ = api_env
    monkeypatch.setenv("HBI_ENV", "production")

    response = client.post("/api/v1/auth/pilot-operator-token")

    assert response.status_code == 403
    assert "disabled in production" in response.json()["detail"]
