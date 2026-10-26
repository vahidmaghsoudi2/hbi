"""WP-01 — Actual Intake Duplicate Gate on Product create path."""
from __future__ import annotations

from app.core.auth import create_access_token
from app.models.user_role import UserRole, ROLE_PO, ROLE_EDITOR


def _auth(db_session, subject="wp01_op", *roles):
    roles = roles or (ROLE_PO, ROLE_EDITOR)
    for role in roles:
        if not (
            db_session.query(UserRole)
            .filter(UserRole.subject_id == subject, UserRole.role == role)
            .first()
        ):
            db_session.add(
                UserRole(
                    user_role_id=f"UR-{subject}-{role}",
                    subject_id=subject,
                    role=role,
                )
            )
    db_session.commit()
    return {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}


def _create(client, headers, **body):
    body.setdefault("product_line", "SKIN")
    return client.post("/api/v1/products/", headers=headers, json=body)


def test_new_product_create_allowed(client, db_session):
    h = _auth(db_session)
    r = _create(
        client,
        h,
        product_id="WP01-NEW-001",
        brand="GateCo",
        product_name="Unique Serum",
        size_value=50,
        size_unit="ml",
        variant="clear",
    )
    assert r.status_code == 201, r.text
    assert r.json()["product_id"] == "WP01-NEW-001"
    assert r.json()["status"] == "DRAFT"


def test_backend_generates_product_id_when_omitted(client, db_session):
    h = _auth(db_session)
    r = _create(
        client,
        h,
        brand="AutoIdCo",
        product_name="System Assigned Serum",
        size_value=30,
        size_unit="ml",
        variant="clear",
    )
    assert r.status_code == 201, r.text
    product_id = r.json()["product_id"]
    assert product_id.startswith("HBI-PROD-")
    assert len(product_id) == len("HBI-PROD-") + 16
    assert r.json()["status"] == "DRAFT"
    assert r.json()["qa_verdict"] == "PENDING"
    assert r.json()["identity_status"] == "NEEDS_REVIEW"


def test_possible_match_without_id_pauses_only_until_snapshot_decision(client, db_session):
    h = _auth(db_session)
    first = _create(
        client, h, product_id="WP01-AUTO-PM-A", brand="AutoReviewCo",
        product_name="Shared Auto Serum", size_value=30, size_unit="ml", variant="clear",
    )
    assert first.status_code == 201, first.text
    identity = {
        "brand": "AutoReviewCo",
        "product_name": "Shared Auto Serum",
        "size_value": 30,
        "size_unit": "ml",
        "variant": "clear",
    }
    chk = client.post("/api/v1/products/duplicate-check/", headers=h, json=identity)
    assert chk.status_code == 200, chk.text
    assert chk.json()["result"] == "POSSIBLE_MATCH"
    check_id = chk.json()["check_id"]
    dec = client.post(
        f"/api/v1/products/duplicate-check/audit/{check_id}/decision",
        headers=h,
        json={"decision": "NEW", "reason": "identity reviewed as distinct"},
    )
    assert dec.status_code == 200, dec.text
    created = _create(client, h, **identity, duplicate_check_id=check_id)
    assert created.status_code == 201, created.text
    assert created.json()["product_id"].startswith("HBI-PROD-")


def test_exact_product_id_duplicate_blocks_create(client, db_session):
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-ID-001",
            brand="GateCo",
            product_name="First",
        ).status_code
        == 201
    )
    r = _create(
        client,
        h,
        product_id="WP01-ID-001",
        brand="Other",
        product_name="Second",
    )
    assert r.status_code == 409, r.text
    assert "EXISTING" in r.text or "already exists" in r.text


def test_exact_gtin_duplicate_blocks_create(client, db_session):
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-GTIN-A",
            brand="GateCo",
            product_name="Bottle A",
            barcode_gtin="5555555555555",
        ).status_code
        == 201
    )
    r = _create(
        client,
        h,
        product_id="WP01-GTIN-B",
        brand="GateCo",
        product_name="Bottle B",
        barcode_gtin="5555555555555",
    )
    assert r.status_code == 409, r.text
    assert "EXISTING" in r.text or "DuplicateCheck" in r.text


def test_possible_match_blocks_create_without_operator_decision(client, db_session):
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-PM-A",
            brand="NameCo",
            product_name="Shared Name",
            size_value=50,
            size_unit="ml",
            variant="clear",
        ).status_code
        == 201
    )
    r = _create(
        client,
        h,
        product_id="WP01-PM-B",
        brand="NameCo",
        product_name="Shared Name",
        size_value=50,
        size_unit="ml",
        variant="clear",
    )
    assert r.status_code == 422, r.text
    assert "POSSIBLE_MATCH" in r.text


def test_possible_match_allows_create_after_operator_decision_new(client, db_session):
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-PM2-A",
            brand="ReviewCo",
            product_name="Review Serum",
            size_value=30,
            size_unit="ml",
            variant="clear",
        ).status_code
        == 201
    )
    chk = client.post(
        "/api/v1/products/duplicate-check/",
        headers=h,
        json={
            "product_id": "WP01-PM2-B",
            "brand": "ReviewCo",
            "product_name": "Review Serum",
            "size_value": 30,
            "size_unit": "ml",
            "variant": "clear",
        },
    )
    assert chk.status_code == 200, chk.text
    body = chk.json()
    assert body["result"] == "POSSIBLE_MATCH"
    check_id = body["check_id"]
    dec = client.post(
        f"/api/v1/products/duplicate-check/audit/{check_id}/decision",
        headers=h,
        json={"decision": "NEW", "reason": "confirmed distinct SKU line"},
    )
    assert dec.status_code == 200, dec.text
    r = _create(
        client,
        h,
        product_id="WP01-PM2-B",
        brand="ReviewCo",
        product_name="Review Serum",
        size_value=30,
        size_unit="ml",
        variant="clear",
        duplicate_check_id=check_id,
    )
    assert r.status_code == 201, r.text
    assert r.json()["product_id"] == "WP01-PM2-B"


def test_size_or_variant_difference_allows_create(client, db_session):
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-VAR-A",
            brand="VarCo",
            product_name="Base Tint",
            size_value=50,
            size_unit="ml",
            variant="clear",
        ).status_code
        == 201
    )
    r = _create(
        client,
        h,
        product_id="WP01-VAR-B",
        brand="VarCo",
        product_name="Base Tint",
        size_value=100,
        size_unit="ml",
        variant="tinted",
    )
    assert r.status_code == 201, r.text


def test_possible_match_rejects_mismatched_snapshot(client, db_session):
    """NEW decision on check_id must not authorize a different create payload."""
    h = _auth(db_session)
    assert (
        _create(
            client,
            h,
            product_id="WP01-BIND-A",
            brand="BindCo",
            product_name="Bound Serum",
            size_value=30,
            size_unit="ml",
            variant="clear",
        ).status_code
        == 201
    )
    chk = client.post(
        "/api/v1/products/duplicate-check/",
        headers=h,
        json={
            "product_id": "WP01-BIND-B",
            "brand": "BindCo",
            "product_name": "Bound Serum",
            "size_value": 30,
            "size_unit": "ml",
            "variant": "clear",
        },
    )
    assert chk.status_code == 200, chk.text
    assert chk.json()["result"] == "POSSIBLE_MATCH"
    check_id = chk.json()["check_id"]
    dec = client.post(
        f"/api/v1/products/duplicate-check/audit/{check_id}/decision",
        headers=h,
        json={"decision": "NEW", "reason": "ok for BIND-B only"},
    )
    assert dec.status_code == 200, dec.text
    # Same name dimensions (still POSSIBLE_MATCH) but product_id differs from snapshot
    r = _create(
        client,
        h,
        product_id="WP01-BIND-C",
        brand="BindCo",
        product_name="Bound Serum",
        size_value=30,
        size_unit="ml",
        variant="clear",
        duplicate_check_id=check_id,
    )
    assert r.status_code == 422, r.text
    assert "input_snapshot" in r.text or "does not match" in r.text
