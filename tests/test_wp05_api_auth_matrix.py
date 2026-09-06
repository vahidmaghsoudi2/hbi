"""WP-05: API authorization matrix — missing §16 cells (Issue #19).

Reality sources (master c451725b89dcfbc3f563c03ea658a982cdcfa33a):
- Contract §16 permission table
- app/api/routers/products.py require_any_role → HTTP 403
- app/core/authorization.py
- Roles: Editor, Reviewer/QA, PO, Admin

Deny-cases assert exact status_code == 403 at HTTP boundary.
"""
from __future__ import annotations

from app.models.product import Product
from app.models.user_role import UserRole, ROLE_EDITOR, ROLE_PO, ROLE_REVIEWER_QA, ROLE_ADMIN
from app.core.auth import create_access_token


def _seed_role(db, subject_id, role, rid):
    db.add(UserRole(user_role_id=rid, subject_id=subject_id, role=role))
    db.flush()


def _auth_header(subject_id):
    return {"Authorization": f"Bearer {create_access_token({'sub': subject_id})}"}


def _make_product(db, pid, status="DRAFT", **kwargs):
    p = Product(
        product_id=pid,
        brand=kwargs.get("brand", "BrandX"),
        product_name=kwargs.get("product_name", "NameY"),
        identity_status=kwargs.get("identity_status", "NEEDS_REVIEW"),
        qa_verdict=kwargs.get("qa_verdict", "PENDING"),
        status=status,
    )
    db.add(p)
    db.flush()
    return p


def test_api_editor_cannot_submit_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_SUB")
    _seed_role(db_session, "ed_wp05", ROLE_EDITOR, "UR_WP05_ED1")
    r = client.post("/api/v1/products/P_WP05_ED_SUB/submit", headers=_auth_header("ed_wp05"))
    assert r.status_code == 403


def test_api_editor_cannot_enter_qa_review_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_EQA", status="SUBMITTED")
    _seed_role(db_session, "ed_wp05b", ROLE_EDITOR, "UR_WP05_ED2")
    r = client.post("/api/v1/products/P_WP05_ED_EQA/enter-qa-review", headers=_auth_header("ed_wp05b"))
    assert r.status_code == 403


def test_api_editor_cannot_approve_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_AP", status="QA_REVIEW")
    _seed_role(db_session, "ed_wp05c", ROLE_EDITOR, "UR_WP05_ED3")
    r = client.post("/api/v1/products/P_WP05_ED_AP/approve", headers=_auth_header("ed_wp05c"))
    assert r.status_code == 403


def test_api_editor_cannot_activate_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_ACT", status="APPROVED")
    _seed_role(db_session, "ed_wp05d", ROLE_EDITOR, "UR_WP05_ED4")
    r = client.post("/api/v1/products/P_WP05_ED_ACT/activate", headers=_auth_header("ed_wp05d"))
    assert r.status_code == 403


def test_api_editor_cannot_reject_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_RJ", status="QA_REVIEW")
    _seed_role(db_session, "ed_wp05e", ROLE_EDITOR, "UR_WP05_ED5")
    r = client.post(
        "/api/v1/products/P_WP05_ED_RJ/reject",
        json={"reason": "not allowed for editor"},
        headers=_auth_header("ed_wp05e"),
    )
    assert r.status_code == 403


def test_api_editor_cannot_archive_403(client, db_session):
    _make_product(db_session, "P_WP05_ED_AR", status="ACTIVE")
    _seed_role(db_session, "ed_wp05f", ROLE_EDITOR, "UR_WP05_ED6")
    r = client.post(
        "/api/v1/products/P_WP05_ED_AR/archive",
        json={"reason": "not allowed"},
        headers=_auth_header("ed_wp05f"),
    )
    assert r.status_code == 403


def test_api_reviewer_cannot_approve_403(client, db_session):
    _make_product(db_session, "P_WP05_RV_AP", status="QA_REVIEW")
    _seed_role(db_session, "rv_wp05", ROLE_REVIEWER_QA, "UR_WP05_RV1")
    r = client.post("/api/v1/products/P_WP05_RV_AP/approve", headers=_auth_header("rv_wp05"))
    assert r.status_code == 403


def test_api_reviewer_cannot_activate_403(client, db_session):
    _make_product(db_session, "P_WP05_RV_ACT", status="APPROVED")
    _seed_role(db_session, "rv_wp05b", ROLE_REVIEWER_QA, "UR_WP05_RV2")
    r = client.post("/api/v1/products/P_WP05_RV_ACT/activate", headers=_auth_header("rv_wp05b"))
    assert r.status_code == 403


def test_api_reviewer_cannot_archive_403(client, db_session):
    _make_product(db_session, "P_WP05_RV_AR", status="ACTIVE")
    _seed_role(db_session, "rv_wp05c", ROLE_REVIEWER_QA, "UR_WP05_RV3")
    r = client.post(
        "/api/v1/products/P_WP05_RV_AR/archive",
        json={"reason": "not allowed"},
        headers=_auth_header("rv_wp05c"),
    )
    assert r.status_code == 403


def test_api_admin_cannot_approve_403(client, db_session):
    _make_product(db_session, "P_WP05_AD_AP", status="QA_REVIEW")
    _seed_role(db_session, "ad_wp05", ROLE_ADMIN, "UR_WP05_AD1")
    r = client.post("/api/v1/products/P_WP05_AD_AP/approve", headers=_auth_header("ad_wp05"))
    assert r.status_code == 403


def test_api_admin_cannot_activate_403(client, db_session):
    _make_product(db_session, "P_WP05_AD_ACT", status="APPROVED")
    _seed_role(db_session, "ad_wp05b", ROLE_ADMIN, "UR_WP05_AD2")
    r = client.post("/api/v1/products/P_WP05_AD_ACT/activate", headers=_auth_header("ad_wp05b"))
    assert r.status_code == 403


def test_api_admin_cannot_reject_403(client, db_session):
    _make_product(db_session, "P_WP05_AD_RJ", status="QA_REVIEW")
    _seed_role(db_session, "ad_wp05c", ROLE_ADMIN, "UR_WP05_AD3")
    r = client.post(
        "/api/v1/products/P_WP05_AD_RJ/reject",
        json={"reason": "admin must not reject"},
        headers=_auth_header("ad_wp05c"),
    )
    assert r.status_code == 403


def test_api_admin_cannot_archive_403(client, db_session):
    _make_product(db_session, "P_WP05_AD_AR", status="ACTIVE")
    _seed_role(db_session, "ad_wp05d", ROLE_ADMIN, "UR_WP05_AD4")
    r = client.post(
        "/api/v1/products/P_WP05_AD_AR/archive",
        json={"reason": "admin must not archive"},
        headers=_auth_header("ad_wp05d"),
    )
    assert r.status_code == 403
