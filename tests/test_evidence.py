import pytest
from app.models.evidence import Evidence
from app.models.product import Product
from app.services.evidence_service import EvidenceService
from app.services.product_knowledge_service import ProductKnowledgeService
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


def test_add_evidence_rebuilds_product_knowledge_after_conflict(db_session):
    product_id = "P_EVIDENCE_CONFLICT_REBUILD"
    db_session.add(Product(
        product_id=product_id,
        brand="TestBrand",
        product_name="Conflict rebuild test",
        product_line="SKIN",
        identity_status="VERIFIED",
        qa_verdict="PENDING",
        status="DRAFT",
        market_region="UK",
    ))
    db_session.add(Evidence(
        evidence_id="EV-CONFLICT-REBUILD-BASE",
        product_id=product_id,
        claim_id="CL-CONFLICT-REBUILD-BASE",
        source_type="MANUFACTURER",
        source_reference="https://manufacturer.example/product",
        claim="The formula contains ingredient A.",
        field="ingredients",
        claim_type="MANUFACTURER_CLAIM",
        evidence_strength="STRONG",
        evidence_status="SUPPORTED",
        conflict_status="NONE",
        qa_status="VERIFIED",
        market_region="UK",
    ))
    db_session.commit()

    knowledge = ProductKnowledgeService(db_session).update_from_evidence(product_id)
    assert knowledge.ingredients == "The formula contains ingredient A."
    assert knowledge.evidence_status == "SUPPORTED"

    created = EvidenceService(db_session).add_evidence({
        "product_id": product_id,
        "source_type": "PEER_REVIEWED",
        "source_reference": "https://review.example/product",
        "claim": "The formula contains ingredient B.",
        "field": "ingredients",
        "claim_type": "FACT",
        "evidence_strength": "MODERATE",
        "evidence_status": "SUPPORTED",
        "qa_status": "VERIFIED",
        "market_region": "UK",
    })

    db_session.refresh(knowledge)
    rows = db_session.query(Evidence).filter_by(product_id=product_id).all()
    assert len(rows) == 2
    assert all(row.conflict_status == "CONFLICT" for row in rows)
    assert created.conflict_status == "CONFLICT"
    assert knowledge.ingredients is None
    assert knowledge.evidence_status == "CONFLICT"
