import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token
from app.models.user_role import ROLE_ADMIN, UserRole


def _auth_headers():
    """ساخت هدر Authorization با توکن معتبر تست"""
    token = create_access_token({"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


class TestHealthCheck:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthEndpoints:
    def test_login_rejects_unknown_admin_credentials(self, client):
        response = client.post("/api/v1/auth/login", json={
            "username": "unknown-admin",
            "password": "wrong-password",
        })
        assert response.status_code == 401

    def test_refresh_with_invalid_token(self, client):
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401


class TestProductEndpoints:
    def test_list_products(self, client):
        response = client.get("/api/v1/products/")
        assert response.status_code == 200


class TestEvidenceEndpoints:
    def test_evidence_returns_200(self, client):
        response = client.get("/api/v1/evidence/", headers=_auth_headers())
        assert response.status_code == 200


class TestInventoryEndpoints:
    def test_get_inventory_not_found(self, client):
        response = client.get("/api/v1/inventory/999")
        assert response.status_code == 404

    def test_get_available_inventory(self, client, db_session):
        db_session.add(UserRole(user_role_id="BASIC-ADMIN-ROLE", subject_id="testuser", role=ROLE_ADMIN))
        db_session.commit()
        response = client.get("/api/v1/inventory/available", headers=_auth_headers())
        assert response.status_code == 200


class TestSalesEndpoints:
    def test_get_total_sales(self, client):
        response = client.get("/api/v1/sales/total", headers=_auth_headers())
        assert response.status_code == 200
