import pytest

from app.core.auth import create_access_token
from app.models.evidence import Evidence
from app.models.product import Product
from app.models.product_problem_link import ProductProblemLink
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA


def _token(subject_id):
    return create_access_token({"sub": subject_id})


def _grant(db, subject_id, role):
    db.add(UserRole(
        user_role_id=f"TEST-{subject_id}-{role}",
        subject_id=subject_id,
        role=role,
    ))
    db.commit()


def _seed_product_and_evidence(db):
    product = Product(
        product_id="API-PPL-PRODUCT-1",
        brand="Test",
        product_name="Test skin product",
        identity_status="PARTIAL_IDENTITY",
        qa_verdict="PENDING",
        status="DRAFT",
    )
    db.add(product)
    db.flush()
    evidence = Evidence(
        evidence_id="API-PPL-EVIDENCE-1",
        product_id=product.product_id,
        claim_id="API-PPL-CLAIM-1",
        source_type="MANUFACTURER",
        source_reference="test-fixture",
        claim="A manufacturer-reported visible dark-spot claim.",
        claim_type="MANUFACTURER_CLAIM",
        evidence_status="UNKNOWN",
        evidence_strength="UNVERIFIED",
        qa_status="PENDING",
        conflict_status="NONE",
        market_region="MEXICO",
    )
    db.add(evidence)
    db.commit()
    return product, evidence


def _payload(product, evidence, **overrides):
    data = {
        "product_id": product.product_id,
        "evidence_id": evidence.evidence_id,
        "claim_id": evidence.claim_id,
        "problem_id": "P17",
        "problem_type": "Problem/presentation",
        "problem_definition_ref": "SKIN_PROBLEM_SPACE_MAP_V0.1.md#P17",
        "relationship_role": "presentation",
        "relationship_status": "CANDIDATE",
        "semantic_basis": "A visible dark-spot claim is a limited presentation-level candidate only.",
        "limitations": "Evidence is unverified and product identity is partial.",
        "decision_basis": "No SUPPORTED state or recommendation is permitted.",
        "problem_map_version": "SKIN_PROBLEM_SPACE_MAP_V0.1",
        "variant": "UNKNOWN",
        "market_region": "MEXICO",
    }
    data.update(overrides)
    return data


def test_product_problem_link_api_requires_authentication(client):
    response = client.get(
        "/api/v1/product-problem-links/",
        params={"problem_id": "P17"},
    )
    assert response.status_code == 401


def test_only_po_or_admin_can_create_product_problem_links(client, db_session):
    product, evidence = _seed_product_and_evidence(db_session)
    _grant(db_session, "api-editor", ROLE_EDITOR)

    response = client.post(
        "/api/v1/product-problem-links/",
        json=_payload(product, evidence),
        headers={"Authorization": f"Bearer {_token('api-editor')}"},
    )

    assert response.status_code == 403
    assert db_session.query(ProductProblemLink).count() == 0


def test_po_can_create_and_reviewer_qa_can_read_link(client, db_session):
    product, evidence = _seed_product_and_evidence(db_session)
    _grant(db_session, "api-po", ROLE_PO)
    _grant(db_session, "api-reviewer", ROLE_REVIEWER_QA)

    created = client.post(
        "/api/v1/product-problem-links/",
        json=_payload(product, evidence),
        headers={"Authorization": f"Bearer {_token('api-po')}"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["product_id"] == product.product_id
    assert body["problem_id"] == "P17"
    assert body["relationship_status"] == "CANDIDATE"
    assert body["claim_id"] == evidence.claim_id

    listed = client.get(
        "/api/v1/product-problem-links/",
        params={"product_id": product.product_id},
        headers={"Authorization": f"Bearer {_token('api-reviewer')}"},
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["link_id"] == body["link_id"]


def test_api_cannot_accept_supported_status_or_extra_fields(client, db_session):
    product, evidence = _seed_product_and_evidence(db_session)
    _grant(db_session, "api-po-negative", ROLE_PO)

    headers = {"Authorization": f"Bearer {_token('api-po-negative')}"}
    supported = client.post(
        "/api/v1/product-problem-links/",
        json=_payload(product, evidence, relationship_status="SUPPORTED"),
        headers=headers,
    )
    assert supported.status_code == 422

    extra = client.post(
        "/api/v1/product-problem-links/",
        json=_payload(product, evidence, recommendation_ready=True),
        headers=headers,
    )
    assert extra.status_code == 422
    assert db_session.query(ProductProblemLink).count() == 0


def test_read_api_requires_exactly_one_selector(client, db_session):
    _grant(db_session, "api-reviewer-selector", ROLE_REVIEWER_QA)
    headers = {"Authorization": f"Bearer {_token('api-reviewer-selector')}"}

    neither = client.get("/api/v1/product-problem-links/", headers=headers)
    both = client.get(
        "/api/v1/product-problem-links/",
        params={"product_id": "P1", "problem_id": "P17"},
        headers=headers,
    )
    assert neither.status_code == 422
    assert both.status_code == 422
