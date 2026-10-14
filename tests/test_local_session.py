import os

from fastapi.testclient import TestClient

from app.main import app


def test_local_session_issues_admin_tokens_only_when_enabled(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "development")
    monkeypatch.setenv("HBI_LOCAL_AUTO_LOGIN", "1")

    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.post("/api/v1/auth/local-session")

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"


def test_local_session_disabled_without_launcher_flag(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "development")
    monkeypatch.delenv("HBI_LOCAL_AUTO_LOGIN", raising=False)

    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.post("/api/v1/auth/local-session")

    assert response.status_code == 404


def test_local_session_disabled_in_production(monkeypatch):
    monkeypatch.setenv("HBI_ENV", "production")
    monkeypatch.setenv("HBI_LOCAL_AUTO_LOGIN", "1")

    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.post("/api/v1/auth/local-session")

    assert response.status_code == 403
