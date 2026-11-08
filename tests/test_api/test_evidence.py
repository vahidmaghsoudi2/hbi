import pytest
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
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
    from app.models.user_role import UserRole, ROLE_REVIEWER_QA
    db_session.add(UserRole(user_role_id="UR_AUTH_001", subject_id="test_user", role=ROLE_REVIEWER_QA))
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "product_id": "P_AUTH_001",
        "source_type": "MANUFACTURER",
        "source_reference": "ref-001",
        "claim": "This is a claim",
    }
    response = client.post("/api/v1/evidence", json=payload, headers=headers)
    assert response.status_code in (200, 201, 422)



def test_get_product_knowledge_without_record_is_read_only(client, db_session):
    product = Product(
        product_id="P_PK_READONLY",
        brand="TestBrand",
        product_name="TestProduct",
        identity_status="VERIFIED",
        qa_verdict="VALID",
    )
    db_session.add(product)
    db_session.commit()
    token = create_access_token({"sub": "test_user"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/evidence/knowledge/P_PK_READONLY",
        headers=headers,
    )

    assert response.status_code == 404
    assert (
        db_session.query(ProductKnowledge)
        .filter_by(product_id="P_PK_READONLY")
        .first()
        is None
    )


def test_get_product_knowledge_returns_existing_record(client, db_session):
    product = Product(
        product_id="P_PK_EXISTING",
        brand="TestBrand",
        product_name="TestProduct",
        identity_status="VERIFIED",
        qa_verdict="VALID",
    )
    db_session.add(product)
    db_session.flush()
    db_session.add(
        ProductKnowledge(
            product_knowledge_id="PK-P_PK_EXISTING",
            product_id="P_PK_EXISTING",
            known_use_cases="sun protection",
            evidence_status="SUPPORTED",
        )
    )
    db_session.commit()
    token = create_access_token({"sub": "test_user"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/evidence/knowledge/P_PK_EXISTING",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["product_id"] == "P_PK_EXISTING"
    assert response.json()["known_use_cases"] == "sun protection"
