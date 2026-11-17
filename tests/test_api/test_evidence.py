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



def test_get_product_knowledge_missing_row_is_read_only_and_returns_404(client, db_session):
    from app.models.product_knowledge import ProductKnowledge

    product = Product(
        product_id="P_KNOWLEDGE_MISSING",
        brand="TestBrand",
        product_name="No Knowledge Row",
        identity_status="VERIFIED",
        qa_verdict="VALID",
    )
    db_session.add(product)
    db_session.commit()
    token = create_access_token({"sub": "knowledge-reader"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/evidence/knowledge/P_KNOWLEDGE_MISSING",
        headers=headers,
    )

    assert response.status_code == 404, response.text
    assert db_session.query(ProductKnowledge).filter_by(
        product_id="P_KNOWLEDGE_MISSING"
    ).count() == 0


def test_get_product_knowledge_existing_row_does_not_mutate_it(client, db_session):
    from app.models.product_knowledge import ProductKnowledge

    product = Product(
        product_id="P_KNOWLEDGE_EXISTING",
        brand="TestBrand",
        product_name="Existing Knowledge",
        identity_status="VERIFIED",
        qa_verdict="VALID",
    )
    db_session.add(product)
    db_session.flush()
    knowledge = ProductKnowledge(
        product_knowledge_id="PK-P_KNOWLEDGE_EXISTING",
        product_id=product.product_id,
        ingredients="Water; Glycerin",
        other_attributes='{"texture":"gel"}',
        domain_evidence_status='{"ingredients":"SUPPORTED"}',
        evidence_status="SUPPORTED",
        knowledge_confidence=0.75,
    )
    db_session.add(knowledge)
    db_session.commit()
    before = {
        "ingredients": knowledge.ingredients,
        "other_attributes": knowledge.other_attributes,
        "domain_evidence_status": knowledge.domain_evidence_status,
        "evidence_status": knowledge.evidence_status,
        "knowledge_confidence": knowledge.knowledge_confidence,
        "updated_at": knowledge.updated_at,
    }
    token = create_access_token({"sub": "knowledge-reader-existing"})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(
        "/api/v1/evidence/knowledge/P_KNOWLEDGE_EXISTING",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    db_session.refresh(knowledge)
    assert {
        "ingredients": knowledge.ingredients,
        "other_attributes": knowledge.other_attributes,
        "domain_evidence_status": knowledge.domain_evidence_status,
        "evidence_status": knowledge.evidence_status,
        "knowledge_confidence": knowledge.knowledge_confidence,
        "updated_at": knowledge.updated_at,
    } == before
