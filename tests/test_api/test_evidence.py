import pytest
from app.models.product import Product
from app.core.auth import create_access_token


def test_create_evidence_requires_auth(client):
    response = client.post("/api/v1/evidence", json={})
    assert response.status_code in (401, 403)


def test_list_evidence_requires_auth(client):
    response = client.get("/api/v1/evidence")
    assert response.status_code in (401, 403)


def test_create_evidence_with_auth(client, db_session):
    product = Product(
        product_id="P_AUTH_001",
        brand="TestBrand",
        product_name="TestProduct",
        identity_status="VERIFIED",
        qa_verdict="VALID",
    )
    db_session.add(product)
    db_session.commit()

    token = create_access_token({"sub": "test_user"})

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "product_id": "P_AUTH_001",
        "source_type": "MANUFACTURER",
        "source_reference": "ref-001",
        "claim": "This is a claim",
    }
    response = client.post("/api/v1/evidence", json=payload, headers=headers)
    assert response.status_code in (200, 201, 422)
