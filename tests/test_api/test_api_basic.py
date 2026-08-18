import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token

client = TestClient(app)


class TestHealthCheck:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestAuthEndpoints:
    def test_login_returns_501(self):
        response = client.post("/api/v1/auth/login", data={"username": "test", "password": "test"})
        assert response.status_code == 501

    def test_refresh_with_invalid_token(self):
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401


class TestProductEndpoints:
    def test_list_products(self):
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_product_not_found(self):
        response = client.get("/api/v1/products/NONEXISTENT")
        assert response.status_code == 404


class TestEvidenceEndpoints:
    def test_evidence_returns_200(self):
        """Evidence endpoints are now active (Phase 3 GATE 7-1)."""
        test_token = create_access_token({"sub": "test-customer-id"})
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.get("/api/v1/evidence/", headers=headers)
        assert response.status_code == 200


class TestInventoryEndpoints:
    def test_get_inventory_not_found(self):
        response = client.get("/api/v1/inventory/product/NONEXISTENT")
        assert response.status_code == 404

    def test_get_available_inventory(self):
        response = client.get("/api/v1/inventory/available")
        assert response.status_code == 200


class TestSalesEndpoints:
    def test_get_total_sales(self):
        test_token = create_access_token({"sub": "test-customer-id"})
        headers = {"Authorization": f"Bearer {test_token}"}
        response = client.get("/api/v1/sales/total", headers=headers)
        assert response.status_code == 200
