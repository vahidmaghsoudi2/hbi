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


def test_operator_decision_is_persisted_and_visible(client, db_session):
    _role(db_session)
    _product(db_session, "P258-OP", name="Hydra Cream")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Hydra Cream",
        "variant": "clear", "size_value": 50, "size_unit": "ml"
    })
    assert r.status_code == 200
    check_id = r.json()["check_id"]

    d = client.post(f"/api/v1/products/duplicate-check/audit/{check_id}/decision",
                     headers=_headers(),
                     json={"decision": "RENAME", "final_product_name": "Hydra Cream New",
                           "reason": "Accounting naming convention"})
    assert d.status_code == 200, d.text
    assert d.json()["operator_decision"]["decision"] == "RENAME"

    audit = client.get("/api/v1/products/duplicate-check/audit", headers=_headers())
    assert audit.status_code == 200
    row = next(x for x in audit.json() if x["check_id"] == check_id)
    assert row["operator_decision"] is not None
    assert row["operator_decision"]["final_product_name"] == "Hydra Cream New"


def test_exact_product_id_is_existing(client, db_session):
    _role(db_session)
    _product(db_session, "P258-ID")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-ID", "brand": "HBI", "product_name": "Hydra Cream",
    })
    assert r.status_code == 200, r.text
    assert r.json()["result"] == "EXISTING"
    assert r.json()["reason"] == "EXACT_PRODUCT_ID"


def test_duplicate_check_without_token_is_401(client, db_session):
    _product(db_session, "P258-AUTH")
    r = client.post("/api/v1/products/duplicate-check/", json={
        "product_id": "P258-AUTH",
    })
    assert r.status_code == 401


def test_duplicate_check_with_unauthorized_role_is_403(client, db_session):
    subject = "wp258-unauthorized"
    db_session.add(UserRole(
        user_role_id=f"UR-{subject}",
        subject_id=subject,
        role="CUSTOMER",
    ))
    db_session.flush()
    r = client.post("/api/v1/products/duplicate-check/",
                    headers=_headers(subject),
                    json={"product_id": "P258-AUTH"})
    assert r.status_code == 403


def test_p4_governance_fields_are_preserved_through_check_and_decision(client, db_session):
    _role(db_session)
    product = _product(db_session, "P258-P4")
    before = (product.status, product.identity_status, product.qa_verdict)

    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-P4",
        "brand": "HBI",
        "product_name": "Hydra Cream",
    })
    assert r.status_code == 200, r.text

    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "EXISTING", "selected_product_id": "P258-P4",
              "reason": "Exact Product ID"},
    )
    assert d.status_code == 200, d.text
    db_session.refresh(product)
    after = (product.status, product.identity_status, product.qa_verdict)
    assert after == before


def test_audit_completeness_has_required_fields_and_decision(client, db_session):
    _role(db_session)
    _product(db_session, "P258-AUDIT")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "NEW-ID", "brand": "HBI", "product_name": "Other Entry",
    })
    assert r.status_code == 200, r.text
    check_id = r.json()["check_id"]

    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{check_id}/decision",
        headers=_headers(),
        json={"decision": "RENAME", "final_product_name": "Other Entry New",
              "reason": "Audit evidence"},
    )
    assert d.status_code == 200, d.text

    audit = client.get("/api/v1/products/duplicate-check/audit", headers=_headers())
    assert audit.status_code == 200, audit.text
    row = next(x for x in audit.json() if x["check_id"] == check_id)
    for key in ("check_id", "timestamp", "actor_id", "actor_role", "result",
                "product_id", "input_snapshot", "candidates", "operator_decision"):
        assert row[key] is not None
    assert row["check_id"] == check_id
    assert row["actor_id"] == "wp258-editor"
    assert row["actor_role"] == ROLE_EDITOR
    assert row["result"] == "NEW"
    assert row["product_id"] == "NEW-ID"
    assert row["input_snapshot"]["product_name"] == "Other Entry"
    assert isinstance(row["candidates"], list)
    assert row["operator_decision"]["decision"] == "RENAME"
    assert row["operator_decision"]["final_product_name"] == "Other Entry New"


def test_operator_existing_without_selected_product_id_is_rejected(client, db_session):
    _role(db_session)
    _product(db_session, "P258-EXISTING")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-EXISTING",
    })
    assert r.status_code == 200
    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "EXISTING"},
    )
    assert d.status_code == 422


def test_operator_existing_with_selected_product_id_is_accepted(client, db_session):
    _role(db_session)
    _product(db_session, "P258-EXISTING-OK")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-EXISTING-OK",
    })
    assert r.status_code == 200
    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "EXISTING", "selected_product_id": "P258-EXISTING-OK"},
    )
    assert d.status_code == 200
    assert d.json()["operator_decision"]["decision"] == "EXISTING"


def test_operator_rename_without_final_product_name_is_rejected(client, db_session):
    _role(db_session)
    _product(db_session, "P258-RENAME")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-RENAME",
    })
    assert r.status_code == 200
    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "RENAME"},
    )
    assert d.status_code == 422


def test_operator_rename_with_final_product_name_is_accepted(client, db_session):
    _role(db_session)
    _product(db_session, "P258-RENAME-OK")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-RENAME-OK",
    })
    assert r.status_code == 200
    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "RENAME", "final_product_name": "Hydra Cream Renamed"},
    )
    assert d.status_code == 200
    assert d.json()["operator_decision"]["decision"] == "RENAME"


def test_invalid_operator_decision_is_rejected(client, db_session):
    _role(db_session)
    _product(db_session, "P258-INVALID")
    r = client.post("/api/v1/products/duplicate-check/", headers=_headers(), json={
        "product_id": "P258-INVALID",
    })
    assert r.status_code == 200
    d = client.post(
        f"/api/v1/products/duplicate-check/audit/{r.json()['check_id']}/decision",
        headers=_headers(),
        json={"decision": "INVALID"},
    )
    assert d.status_code == 422
