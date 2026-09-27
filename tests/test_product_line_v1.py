"""Product Line V1 — required on create, operator-controlled change, no inference."""
from __future__ import annotations

import pytest

from app.core.auth import create_access_token
from app.core.governance import PRODUCT_LINE_VALUES
from app.models.product import Product
from app.models.user_role import UserRole, ROLE_PO, ROLE_EDITOR
from app.services.product_service import ProductService
from app.core.exceptions import ValidationError


def _auth(db_session, subject="pl_op", *roles):
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


def _base(**extra):
    body = {
        "product_id": extra.pop("product_id", "PL-V1-001"),
        "brand": extra.pop("brand", "LineBrand"),
        "product_name": extra.pop("product_name", "Line Product"),
        "product_line": extra.pop("product_line", "SKIN"),
    }
    body.update(extra)
    return body


@pytest.mark.parametrize("line", sorted(PRODUCT_LINE_VALUES))
def test_create_accepts_each_allowed_line(client, db_session, line):
    h = _auth(db_session)
    r = client.post(
        "/api/v1/products/",
        headers=h,
        json=_base(product_id=f"PL-OK-{line}", product_line=line),
    )
    assert r.status_code == 201, r.text
    assert r.json()["product_line"] == line
    assert r.json()["status"] == "DRAFT"


def test_create_rejects_missing_product_line(client, db_session):
    h = _auth(db_session)
    body = {
        "product_id": "PL-MISS",
        "brand": "B",
        "product_name": "N",
    }
    r = client.post("/api/v1/products/", headers=h, json=body)
    assert r.status_code in (400, 422), r.text


def test_create_rejects_invalid_product_line(client, db_session):
    h = _auth(db_session)
    r = client.post(
        "/api/v1/products/",
        headers=h,
        json=_base(product_id="PL-BAD", product_line="BOOST"),
    )
    assert r.status_code in (400, 422), r.text
    # BOOST must not be stored as SKIN or any line
    assert db_session.get(Product, "PL-BAD") is None


def test_create_does_not_infer_line_from_category_id(client, db_session):
    h = _auth(db_session)
    # category_id is not on ProductCreate; even if smuggled, must not satisfy line
    body = {
        "product_id": "PL-NOCAT",
        "brand": "B",
        "product_name": "N",
        "category_id": "HAIR",
    }
    r = client.post("/api/v1/products/", headers=h, json=body)
    assert r.status_code in (400, 422), r.text
    assert db_session.get(Product, "PL-NOCAT") is None


def test_service_rejects_empty_line(db_session):
    with pytest.raises(ValidationError, match="product_line"):
        ProductService(db_session).create_product_with_inventory(
            {
                "product_id": "PL-EMPTY",
                "brand": "B",
                "product_name": "N",
                "product_line": "  ",
            },
            actor_id="u1",
            roles={ROLE_EDITOR},
        )


def test_legacy_product_without_line_still_readable(db_session):
    """Legacy rows may have NULL product_line; no auto-backfill in this WP."""
    db_session.add(
        Product(
            product_id="PL-LEGACY",
            brand="Old",
            product_name="Legacy",
            identity_status="NEEDS_REVIEW",
            qa_verdict="PENDING",
            status="DRAFT",
            product_line=None,
        )
    )
    db_session.commit()
    row = db_session.get(Product, "PL-LEGACY")
    assert row is not None
    assert row.product_line is None


def test_patch_product_line_operator_controlled(client, db_session):
    h = _auth(db_session)
    r = client.post(
        "/api/v1/products/",
        headers=h,
        json=_base(product_id="PL-PATCH", product_line="SKIN"),
    )
    assert r.status_code == 201, r.text
    r2 = client.patch(
        "/api/v1/products/PL-PATCH",
        headers=h,
        json={"product_line": "HAIR"},
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["product_line"] == "HAIR"
    row = db_session.get(Product, "PL-PATCH")
    assert row.product_line == "HAIR"


def test_patch_rejects_invalid_product_line(client, db_session):
    h = _auth(db_session)
    assert (
        client.post(
            "/api/v1/products/",
            headers=h,
            json=_base(product_id="PL-PATCH-BAD", product_line="TOOLS"),
        ).status_code
        == 201
    )
    r = client.patch(
        "/api/v1/products/PL-PATCH-BAD",
        headers=h,
        json={"product_line": "NOT_A_LINE"},
    )
    assert r.status_code in (400, 422), r.text
    db_session.refresh(db_session.get(Product, "PL-PATCH-BAD"))
    assert db_session.get(Product, "PL-PATCH-BAD").product_line == "TOOLS"
