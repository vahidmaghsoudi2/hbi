"""WP-INTAKE-E2E-API-SLICE-001 — Duplicate API coverage + single path to ACTIVE.

Tests only. Uses existing Master endpoints/services. No production changes.
"""
from __future__ import annotations

import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR
from app.models.product import Product


def _auth(db_session, subject: str, *roles: str) -> dict:
    for role in roles:
        exists = (
            db_session.query(UserRole)
            .filter(UserRole.subject_id == subject, UserRole.role == role)
            .first()
        )
        if not exists:
            db_session.add(
                UserRole(
                    user_role_id=f"UR-{subject}-{role}",
                    subject_id=subject,
                    role=role,
                )
            )
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}


def _create_product(client, headers, product_id, **extra):
    body = {
        "product_id": product_id,
        "brand": extra.pop("brand", "SliceBrand"),
        "product_name": extra.pop("product_name", "Slice Serum"),
        **extra,
    }
    r = client.post("/api/v1/products/", headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# A) Duplicate Check API
# ---------------------------------------------------------------------------


def test_duplicate_exact_product_id_returns_existing(client, db_session):
    headers = _auth(db_session, "dup_editor", ROLE_EDITOR, ROLE_PO)
    _create_product(
        client,
        headers,
        "DUP-ID-001",
        brand="DupCo",
        product_name="Exact Id Product",
        barcode_gtin="1111111111111",
        size_value=50,
        size_unit="ml",
    )
    r = client.post(
        "/api/v1/products/duplicate-check/",
        headers=headers,
        json={
            "product_id": "DUP-ID-001",
            "brand": "Other",
            "product_name": "Other Name",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "EXISTING"
    assert body["reason"] == "EXACT_PRODUCT_ID"
    assert any(c.get("product_id") == "DUP-ID-001" for c in body.get("candidates", []))


def test_duplicate_exact_barcode_gtin_returns_existing(client, db_session):
    headers = _auth(db_session, "dup_editor2", ROLE_EDITOR, ROLE_PO)
    _create_product(
        client,
        headers,
        "DUP-BC-001",
        brand="DupCo",
        product_name="Barcode Product",
        barcode_gtin="2222222222222",
        size_value=30,
        size_unit="ml",
    )
    r = client.post(
        "/api/v1/products/duplicate-check/",
        headers=headers,
        json={
            "product_id": "DUP-BC-NEW",
            "barcode_gtin": "2222222222222",
            "brand": "DupCo",
            "product_name": "Different Name Same Barcode",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "EXISTING"
    assert body["reason"] == "EXACT_BARCODE"


def test_duplicate_exact_name_same_size_returns_possible_match(client, db_session):
    headers = _auth(db_session, "dup_editor3", ROLE_EDITOR, ROLE_PO)
    _create_product(
        client,
        headers,
        "DUP-NAME-001",
        brand="NameCo",
        product_name="Shared Serum Name",
        size_value=50,
        size_unit="ml",
        variant="clear",
    )
    r = client.post(
        "/api/v1/products/duplicate-check/",
        headers=headers,
        json={
            "product_id": "DUP-NAME-NEW",
            "brand": "NameCo",
            "product_name": "Shared Serum Name",
            "size_value": 50,
            "size_unit": "ml",
            "variant": "clear",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "POSSIBLE_MATCH"
    assert body["reason"] == "EXACT_NAME_REQUIRES_OPERATOR_REVIEW"


def test_duplicate_different_variant_or_size_is_distinct_not_possible_match(
    client, db_session
):
    headers = _auth(db_session, "dup_editor4", ROLE_EDITOR, ROLE_PO)
    _create_product(
        client,
        headers,
        "DUP-VAR-001",
        brand="VarCo",
        product_name="Variant Base",
        size_value=50,
        size_unit="ml",
        variant="clear",
    )
    r = client.post(
        "/api/v1/products/duplicate-check/",
        headers=headers,
        json={
            "product_id": "DUP-VAR-NEW",
            "brand": "VarCo",
            "product_name": "Variant Base",
            "size_value": 100,
            "size_unit": "ml",
            "variant": "tinted",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # Size/variant difference => not a duplicate candidate (algorithm unchanged)
    assert body["result"] == "NEW"
    assert body.get("candidates") in (None, [])


# ---------------------------------------------------------------------------
# B) Single vertical slice CREATE → … → ACTIVE
# ---------------------------------------------------------------------------


def test_intake_api_vertical_slice_reaches_active(client, db_session):
    """CREATE → DUPLICATE → RESEARCH DRAFT → EVIDENCE → VERIFY → SUBMIT →
    QA VALID → IDENTITY VERIFIED → APPROVE → ACTIVATE → ACTIVE.
    """
    po = _auth(db_session, "slice_po", ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR)
    pid = "SLICE-E2E-001"

    # CREATE
    created = _create_product(
        client,
        po,
        pid,
        brand="SliceCo",
        product_name="Vertical Slice Hydrator",
        barcode_gtin="3333333333333",
        size_value=50,
        size_unit="ml",
        variant="clear",
    )
    assert created["status"] == "DRAFT"

    # DUPLICATE CHECK (same product_id → EXISTING / EXACT_PRODUCT_ID)
    dup = client.post(
        "/api/v1/products/duplicate-check/",
        headers=po,
        json={
            "product_id": pid,
            "brand": "OtherBrand",
            "product_name": "Unrelated Product",
        },
    )
    assert dup.status_code == 200, dup.text
    dup_body = dup.json()
    assert dup_body["result"] == "EXISTING"
    assert dup_body["reason"] == "EXACT_PRODUCT_ID"
    assert any(
        candidate.get("product_id") == pid
        for candidate in dup_body.get("candidates", [])
    )

    # RESEARCH DRAFT (PENDING evidence)
    draft = client.post(
        f"/api/v1/products/{pid}/research-draft",
        headers=po,
        json={
            "assertions": [
                {
                    "claim": "dry_skin_care",
                    "source_type": "MANUFACTURER",
                    "source_reference": "test://slice-research",
                    "claim_type": "MANUFACTURER_CLAIM",
                    "field": "known_use_cases",
                }
            ]
        },
    )
    assert draft.status_code == 200, draft.text
    draft_rows = draft.json()
    assert isinstance(draft_rows, list) and len(draft_rows) >= 1
    draft_eid = draft_rows[0]["evidence_id"]

    # EVIDENCE CREATE (additional claim-level evidence for D3/readiness path)
    ev = client.post(
        "/api/v1/evidence/",
        headers=po,
        json={
            "product_id": pid,
            "claim": "hydration benefit",
            "source_type": "PEER_REVIEWED",
            "source_reference": "test://slice-evidence",
            "claim_type": "BENEFIT",
            "field": "claimed_benefits",
            "evidence_strength": "HIGH",
        },
    )
    assert ev.status_code == 201, ev.text
    evidence_id = ev.json()["evidence_id"]

    # EVIDENCE VERIFY — clear PENDING from research draft + approve new evidence
    # so EvidenceReadiness can pass (no PENDING/REJECTED left unresolved).
    for eid, verdict in ((draft_eid, "VERIFIED"), (evidence_id, "VERIFIED")):
        v = client.post(
            f"/api/v1/evidence/{eid}/verify",
            headers=po,
            json={"verdict": verdict, "reason": "slice verification"},
        )
        assert v.status_code == 200, v.text
        assert v.json()["qa_status"] in ("VERIFIED", "APPROVED")

    # SUBMIT → QA_REVIEW
    assert client.post(f"/api/v1/products/{pid}/submit", headers=po).status_code == 200
    assert (
        client.post(f"/api/v1/products/{pid}/enter-qa-review", headers=po).status_code
        == 200
    )

    # QA VALID (D3 + readiness enforced by transition service)
    qa = client.post(
        f"/api/v1/products/{pid}/qa",
        headers=po,
        json={"verdict": "VALID", "notes": "slice qa"},
    )
    assert qa.status_code == 200, qa.text
    assert qa.json()["qa_verdict"] == "VALID"

    # IDENTITY VERIFIED
    ident = client.post(
        f"/api/v1/products/{pid}/verify-identity",
        headers=po,
        json={
            "identity_status": "VERIFIED",
            "source_refs": "test://slice-identity",
            "confidence": 1.0,
        },
    )
    assert ident.status_code == 200, ident.text
    assert ident.json()["identity_status"] == "VERIFIED"

    # APPROVE → ACTIVATE
    ap = client.post(f"/api/v1/products/{pid}/approve", headers=po)
    assert ap.status_code == 200, ap.text
    assert ap.json()["status"] == "APPROVED"

    act = client.post(f"/api/v1/products/{pid}/activate", headers=po)
    assert act.status_code == 200, act.text
    assert act.json()["status"] == "ACTIVE"

    # Final explicit assert against persisted Product.status (DTO GET omits status)
    assert act.json()["status"] == "ACTIVE"
    db_session.expire_all()
    product = db_session.query(Product).filter(Product.product_id == pid).one()
    assert product.status == "ACTIVE"
