from app.core.auth import create_access_token
from app.models.product import Product
from app.models.user_role import UserRole, ROLE_EDITOR


def _headers(subject="wp258-editor"):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject})}"}


def _role(db, subject="wp258-editor"):
    db.add(UserRole(user_role_id=f"UR-{subject}", subject_id=subject, role=ROLE_EDITOR))
    db.flush()


def _product(db, pid, name="Hydra Cream", brand="HBI", variant="clear", size=50, unit="ml", barcode=None, packaging="v1"):
    p = Product(product_id=pid, brand=brand, product_name=name, variant=variant,
                size_value=size, size_unit=unit, barcode_gtin=barcode,
                packaging_version=packaging, identity_status="NEEDS_REVIEW",
                qa_verdict="PENDING", status="DRAFT")
    db.add(p)
    db.flush()
    return p


def test_exact_barcode_is_existing_and_is_audited(client, db_session):
    _role(db_session)
    _product(db_session, "P258-BAR", barcode="6260000000012")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Other Entry",
        "barcode_gtin": "6260000000012", "variant": "clear", "size_value": 50, "size_unit": "ml"
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["result"] == "EXISTING"
    assert body["reason"] == "EXACT_BARCODE"
    audit = client.get("/api/v1/products/duplicate-check/audit", headers=_headers())
    assert audit.status_code == 200
    assert audit.json()[0]["check_id"] == body["check_id"]


def test_different_size_is_not_existing(client, db_session):
    _role(db_session)
    _product(db_session, "P258-SIZE", size=50)
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydra Cream",
        "variant": "clear", "size_value": 100, "size_unit": "ml"
    })
    assert r.status_code == 200
    assert r.json()["result"] == "NEW"
    assert r.json()["candidates"] == []


def test_different_variant_is_not_existing(client, db_session):
    _role(db_session)
    _product(db_session, "P258-VAR", variant="clear")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydra Cream",
        "variant": "tinted", "size_value": 50, "size_unit": "ml"
    })
    assert r.status_code == 200
    assert r.json()["result"] == "NEW"
    assert r.json()["candidates"] == []


def test_packaging_change_keeps_same_business_product_as_review_candidate(client, db_session):
    _role(db_session)
    _product(db_session, "P258-PACK", packaging="v1")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydra Cream",
        "variant": "clear", "size_value": 50, "size_unit": "ml", "packaging_version": "v2"
    })
    assert r.status_code == 200
    assert r.json()["result"] == "POSSIBLE_MATCH"
    assert r.json()["candidates"][0]["conflicting_fields"] == []


def test_exact_name_is_operator_review_and_names_are_alphabetical(client, db_session):
    _role(db_session)
    _product(db_session, "P258-Z", name="Zeta")
    _product(db_session, "P258-A", name="Alpha")
    _product(db_session, "P258-H", name="Hydra Cream")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydra Cream",
        "variant": "clear", "size_value": 50, "size_unit": "ml"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["result"] == "POSSIBLE_MATCH"
    assert [x["product_name"] for x in body["naming_reference"]] == ["Alpha", "Hydra Cream", "Zeta"]
    assert body["operator_decision_required"] is True


def test_no_fuzzy_match_and_no_candidate_is_new(client, db_session):
    _role(db_session)
    _product(db_session, "P258-NEW", name="Hydra Cream")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydr Creamx",
        "variant": "clear", "size_value": 50, "size_unit": "ml"
    })
    assert r.status_code == 200
    assert r.json()["result"] == "NEW"
    assert r.json()["provenance"]["fuzzy_matching"] is False
