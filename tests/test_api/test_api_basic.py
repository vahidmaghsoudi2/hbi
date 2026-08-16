import pytest
from fastapi.testclient import TestClient
from app.main import app

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
    def test_evidence_returns_501(self):
        response = client.get("/api/v1/evidence/")
        assert response.status_code == 501


class TestInventoryEndpoints:
    def test_get_inventory_not_found(self):
        response = client.get("/api/v1/inventory/product/NONEXISTENT")
        assert response.status_code == 404

    def test_get_available_inventory(self):
        response = client.get("/api/v1/inventory/available")
        assert response.status_code == 200


class TestSalesEndpoints:
    def test_get_total_sales(self):
        response = client.get("/api/v1/sales/total")
        assert response.status_code == 200
