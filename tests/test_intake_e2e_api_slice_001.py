"""WP-INTAKE-E2E-API-SLICE-001 — Duplicate API coverage + single path to ACTIVE.

Tests only. Uses existing Master endpoints/services. No production changes.
"""
from __future__ import annotations

import pytest

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_PO, ROLE_REVIEWER_QA, ROLE_EDITOR, ROLE_ADMIN
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.services.stock_in_service import StockInService


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
        "product_line": extra.pop("product_line", "SKIN"),
        **extra,
    }
    r = client.post("/api/v1/products/", headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# A0) Physical Stock-In API path
# ---------------------------------------------------------------------------


def test_product_intake_requires_explicit_stock_in_api(client, db_session):
    editor = _auth(db_session, "intake_stock_editor", ROLE_EDITOR, ROLE_PO)
    admin = _auth(db_session, "intake_stock_admin", ROLE_ADMIN)
    pid = "INTAKE-STOCK-API-001"
    _create_product(
        client, editor, pid,
        brand="StockCo",
        product_name="Explicit Stock-In Product",
        product_line="SKIN",
    )

    inventory = db_session.query(Inventory).filter(Inventory.product_id == pid).one()
    assert inventory.quantity_available == 0
    assert inventory.stock_status == "OUT_OF_STOCK"
    assert db_session.query(StockMovement).filter(StockMovement.product_id == pid).count() == 0

    stock_in = client.post(
        "/api/v1/inventory/stock-in",
        headers=admin,
        json={
            "product_id": pid,
            "quantity": 3,
            "purchase_price_usd": 4.5,
            "fx_rate_usd_to_irr": 500000,
            "note": "explicit intake stock-in API test",
            "reference_type": "TEST",
            "reference_id": "INTAKE-STOCK-API-001",
        },
    )
    assert stock_in.status_code == 200, stock_in.text
    body = stock_in.json()
    assert body["before_quantity"] == 0
    assert body["inventory"]["quantity_available"] == 3
    assert body["movement"]["quantity_delta"] == 3
    assert body["movement"]["quantity_after"] == 3
    assert body["movement"]["movement_type"] == "STOCK_IN"


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

    # Product registration creates only an empty inventory ledger row, not stock.
    inventory = db_session.query(Inventory).filter(Inventory.product_id == pid).one()
    assert inventory.quantity_available == 0
    assert inventory.stock_status == "OUT_OF_STOCK"
    assert db_session.query(StockMovement).filter(StockMovement.product_id == pid).count() == 0

    # A physical receipt is a separate operation and must create a ledger movement.
    stock_result = StockInService(db_session).stock_in(
        product_id=pid,
        quantity=3,
        purchase_price_usd=2.5,
        fx_rate_usd_to_irr=500000,
        note="test physical receipt",
        reference_type="TEST",
        reference_id="INTAKE-E2E",
    )
    db_session.commit()
    db_session.refresh(inventory)
    assert stock_result["before_quantity"] == 0
    assert inventory.quantity_available == 3
    assert inventory.stock_status != "OUT_OF_STOCK"
    movement = db_session.query(StockMovement).filter(
        StockMovement.product_id == pid,
        StockMovement.movement_type == "STOCK_IN",
    ).one()
    assert movement.quantity_delta == 3
    assert movement.quantity_after == 3

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

    # WP-02: verified contraindications required for SKIN before APPROVE/ACTIVATE.
    safe = client.post(
        "/api/v1/evidence/",
        headers=po,
        json={
            "product_id": pid,
            "claim": "none known",
            "source_type": "MANUFACTURER",
            "source_reference": "test://slice-safety",
            "claim_type": "MANUFACTURER_CLAIM",
            "field": "contraindications",
        },
    )
    assert safe.status_code == 201, safe.text
    safe_id = safe.json()["evidence_id"]

    # EVIDENCE VERIFY — clear PENDING from research draft + approve new evidence
    # so EvidenceReadiness can pass (no PENDING/REJECTED left unresolved).
    for eid, verdict in ((draft_eid, "VERIFIED"), (evidence_id, "VERIFIED"), (safe_id, "VERIFIED")):
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


def test_editor_can_create_and_review_research_draft(client, db_session):
    """The Product Intake session can submit a source-traceable draft and review its evidence."""
    editor = _auth(db_session, "intake_research_editor", ROLE_EDITOR)
    pid = "INTAKE-RESEARCH-EDITOR-001"
    _create_product(
        client, editor, pid,
        brand="ResearchCo",
        product_name="Research Workflow Product",
        product_line="SKIN",
    )
    draft = client.post(
        f"/api/v1/products/{pid}/research-draft",
        headers=editor,
        json={"assertions": [
            {
                "claim": "Manufacturer states this is a moisturizer",
                "source_type": "MANUFACTURER",
                "source_reference": "https://example.test/product",
                "claim_type": "MANUFACTURER_CLAIM",
                "field": "claimed_benefits",
            },
            {
                "claim": "A clinical trial evaluated the stated outcome",
                "source_type": "CLINICAL_TRIAL",
                "source_reference": "trial-registry:TEST-001",
                "claim_type": "FACT",
                "field": "claimed_benefits",
            },
        ]},
    )
    assert draft.status_code == 200, draft.text
    assert len(draft.json()) == 2
    evidence_id = draft.json()[0]["evidence_id"]
    assert draft.json()[0]["qa_status"] == "PENDING"
    assert draft.json()[0]["evidence_status"] == "UNKNOWN"
    assert draft.json()[1]["claim_type"] == "FACT"
    assert draft.json()[1]["source_type"] == "CLINICAL_TRIAL"
    assert draft.json()[1]["qa_status"] == "PENDING"

    missing_reason = client.post(
        f"/api/v1/evidence/{evidence_id}/verify",
        headers=editor,
        json={"verdict": "VERIFIED"},
    )
    assert missing_reason.status_code == 422, missing_reason.text

    reviewed = client.post(
        f"/api/v1/evidence/{evidence_id}/verify",
        headers=editor,
        json={"verdict": "VERIFIED", "reason": "intake workflow test"},
    )
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["qa_status"] == "VERIFIED"
