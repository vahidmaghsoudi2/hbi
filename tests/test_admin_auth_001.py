import os

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.admin_credential import AdminCredential
from app.models.user_role import UserRole, ROLE_ADMIN
from app.services.admin_auth_service import pwd_context


def provision_test_admin():
    db = SessionLocal()
    try:
        username = "test-admin"
        subject = "USR_TEST_ADMIN"
        credential = db.query(AdminCredential).filter(
            AdminCredential.username == username
        ).first()
        if credential is None:
            db.add(AdminCredential(
                credential_id="ADMIN-CRED-TEST",
                subject_id=subject,
                username=username,
                password_hash=pwd_context.hash("correct-password"),
            ))
        role = db.query(UserRole).filter(
            UserRole.subject_id == subject,
            UserRole.role == ROLE_ADMIN,
        ).first()
        if role is None:
            db.add(UserRole(
                user_role_id="UR-USR_TEST_ADMIN-Admin",
                subject_id=subject,
                role=ROLE_ADMIN,
            ))
        db.commit()
    finally:
        db.close()


def test_admin_login_success_and_bad_password():
    os.environ["HBI_ENV"] = "test"
    provision_test_admin()
    with TestClient(app) as client:
        ok = client.post("/api/v1/auth/login", json={
            "username": "test-admin",
            "password": "correct-password",
        })
        assert ok.status_code == 200
        assert ok.json()["access_token"]
        bad = client.post("/api/v1/auth/login", json={
            "username": "test-admin",
            "password": "wrong-password",
        })
        assert bad.status_code == 401
