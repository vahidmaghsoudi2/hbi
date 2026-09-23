import os

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.admin_credential import AdminCredential
from app.models.user_role import UserRole, ROLE_ADMIN
from app.services.admin_auth_service import (
    ensure_admin_account,
    pwd_context,
    verify_admin_password,
)
from app.core.brute_force import clear_failures


def provision_test_admin(username: str, subject: str, password: str = "correct-password"):
    db = SessionLocal()
    try:
        credential = db.query(AdminCredential).filter(
            AdminCredential.username == username
        ).first()
        if credential is None:
            db.add(AdminCredential(
                credential_id=f"ADMIN-CRED-{subject}",
                subject_id=subject,
                username=username,
                password_hash=pwd_context.hash(password),
            ))
        role = db.query(UserRole).filter(
            UserRole.subject_id == subject,
            UserRole.role == ROLE_ADMIN,
        ).first()
        if role is None:
            db.add(UserRole(
                user_role_id=f"UR-{subject}-Admin",
                subject_id=subject,
                role=ROLE_ADMIN,
            ))
        db.commit()
    finally:
        db.close()


def test_admin_login_success_bad_password_and_refresh():
    os.environ["HBI_ENV"] = "test"
    username = "test-admin"
    subject = "USR_TEST_ADMIN"
    provision_test_admin(username, subject)

    with TestClient(app) as client:
        ok = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "correct-password",
        })
        assert ok.status_code == 200
        tokens = ok.json()
        assert tokens["access_token"]
        assert tokens["refresh_token"]

        refreshed = client.post("/api/v1/auth/refresh", json={
            "refresh_token": tokens["refresh_token"],
        })
        assert refreshed.status_code == 200
        assert refreshed.json()["access_token"]

        bad = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "wrong-password",
        })
        assert bad.status_code == 401


def test_admin_login_brute_force_lockout():
    os.environ["HBI_ENV"] = "test"
    username = "lockout-admin"
    subject = "USR_LOCKOUT_ADMIN"
    provision_test_admin(username, subject)
    clear_failures("testclient|lockout-admin")

    with TestClient(app) as client:
        for _ in range(4):
            response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": "wrong-password",
            })
            assert response.status_code == 401

        locked = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "wrong-password",
        })
        assert locked.status_code == 429
        assert locked.headers.get("Retry-After")

    clear_failures("testclient|lockout-admin")


def test_admin_login_requires_admin_role():
    os.environ["HBI_ENV"] = "test"
    username = "roleless-admin"
    subject = "USR_ROLELESS_ADMIN"
    db = SessionLocal()
    try:
        existing = db.query(AdminCredential).filter(
            AdminCredential.username == username
        ).first()
        if existing is None:
            db.add(AdminCredential(
                credential_id="ADMIN-CRED-ROLELESS",
                subject_id=subject,
                username=username,
                password_hash=pwd_context.hash("correct-password"),
            ))
            db.commit()
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json={
            "username": username,
            "password": "correct-password",
        })
        assert response.status_code == 403


def test_admin_bootstrap_stores_hash_and_assigns_role(monkeypatch):
    monkeypatch.setenv("HBI_ADMIN_USERNAME", "bootstrap-admin")
    monkeypatch.setenv("HBI_ADMIN_PASSWORD", "bootstrap-secret")
    monkeypatch.setenv("HBI_ADMIN_SUBJECT", "USR_BOOTSTRAP_ADMIN")

    db = SessionLocal()
    try:
        credential = ensure_admin_account(db)
        assert credential is not None
        assert credential.password_hash != "bootstrap-secret"
        assert verify_admin_password(credential, "bootstrap-secret")
        assert db.query(UserRole).filter(
            UserRole.subject_id == "USR_BOOTSTRAP_ADMIN",
            UserRole.role == ROLE_ADMIN,
        ).first() is not None
    finally:
        db.close()
