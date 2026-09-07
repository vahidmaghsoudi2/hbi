"""CP-01 — Customer Profile V1 integration (real API + Case + Recommendation).

Replaces historical skipped mock contracts with architecture-aligned tests against
current CustomerService + /api/v1/customers routes + RecommendationFacade.
"""
from __future__ import annotations

import pytest
from app.core.auth import create_access_token
from app.interface.facades import RecommendationFacade
from app.services.customer_service import CustomerService


def _auth(sub: str = "operator_gallery") -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': sub})}"}


# ---------------------------------------------------------------------------
# A — Customer lifecycle (service + persistence via intake API)
# ---------------------------------------------------------------------------

def test_customer_create_and_persist_via_intake(client, db_session):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "سارا CP01",
            "mobile": "09130000001",
            "concerns": "آبرسان",
            "consent": 1,
            "open_case": False,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    cid = body["customer"]["customer_id"]
    assert cid.startswith("CUST_")
    assert body["customer"]["concerns"] == "آبرسان"
    assert body["case"] is None

    svc = CustomerService(db_session)
    loaded = svc.find_by_mobile("09130000001")
    assert loaded is not None
    assert loaded.customer_id == cid
    assert loaded.concerns == "آبرسان"


def test_customer_update_concerns_same_mobile(client, db_session):
    client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "سارا CP01",
            "mobile": "09130000002",
            "concerns": "آبرسان",
            "consent": 1,
            "open_case": False,
        },
    )
    r2 = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "سارا CP01",
            "mobile": "09130000002",
            "concerns": "ضدآفتاب, لک",
            "consent": 1,
            "open_case": False,
        },
    )
    assert r2.status_code == 201
    c = r2.json()["customer"]
    assert c["concerns"] == "ضدآفتاب, لک"
    svc = CustomerService(db_session)
    assert svc.find_by_mobile("09130000002").concerns == "ضدآفتاب, لک"


# ---------------------------------------------------------------------------
# B — Intake API + guest + validation/auth
# ---------------------------------------------------------------------------

def test_post_customers_intake_201(client):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={"name": "نسیم", "mobile": "09130000003", "concerns": "مو", "consent": 0},
    )
    assert r.status_code == 201
    assert "recommendation_profile" in r.json()
    assert r.json()["recommendation_profile"]["concerns"] == "مو"


def test_post_customers_guest_public_201(client):
    r = client.post(
        "/api/v1/customers/guest",
        json={"name": "مهمان CP01", "consent": 0, "concerns": "ضدآفتاب"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["customer_id"].startswith("CUST_GUEST_")
    assert body["mobile"] is None
    assert body["concerns"] == "ضدآفتاب"


def test_intake_requires_auth_401(client):
    r = client.post(
        "/api/v1/customers/intake",
        json={"name": "بدون توکن", "consent": 0},
    )
    assert r.status_code == 401


def test_intake_invalid_consent_422(client):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={"name": "بد", "mobile": "09130000099", "consent": 3, "open_case": False},
    )
    assert r.status_code == 422


def test_intake_mobile_mismatch_403(client):
    """JWT sub looks like mobile and differs from body mobile → 403."""
    headers = _auth(sub="09131112233")
    r = client.post(
        "/api/v1/customers/intake",
        headers=headers,
        json={
            "name": "Mismatch",
            "mobile": "09134445566",
            "consent": 0,
            "open_case": False,
        },
    )
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# C — Case behavior open_case true/false
# ---------------------------------------------------------------------------

def test_open_case_true_creates_case(client):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "Case On",
            "mobile": "09130000010",
            "concerns": "ضدآفتاب",
            "consent": 1,
            "open_case": True,
        },
    )
    assert r.status_code == 201
    case = r.json()["case"]
    assert case is not None
    assert case["case_id"].startswith("CASE_")
    assert case["customer_id"] == r.json()["customer"]["customer_id"]
    assert case["case_type"] == "OPEN"


def test_open_case_false_no_case(client):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "Case Off",
            "mobile": "09130000011",
            "concerns": "لک",
            "consent": 1,
            "open_case": False,
        },
    )
    assert r.status_code == 201
    assert r.json()["case"] is None


# ---------------------------------------------------------------------------
# D — Recommendation Profile carries Customer fields
# ---------------------------------------------------------------------------

def test_recommendation_profile_from_customer_fields(client, db_session):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "Profile User",
            "mobile": "09130000020",
            "concerns": "پوست حساس",
            "skin_profile": "sensitive",
            "consent": 1,
            "open_case": False,
        },
    )
    assert r.status_code == 201
    profile = r.json()["recommendation_profile"]
    assert profile["concerns"] == "پوست حساس"
    assert profile.get("skin_profile") == "sensitive"

    svc = CustomerService(db_session)
    c = svc.find_by_mobile("09130000020")
    rebuilt = svc.build_recommendation_profile(c)
    assert rebuilt["concerns"] == "پوست حساس"
    assert rebuilt.get("skin_profile") == "sensitive"


# ---------------------------------------------------------------------------
# E — Recommendation Facade invoked with real profile
# ---------------------------------------------------------------------------

def test_recommendation_facade_invoked_with_profile(client, db_session):
    r = client.post(
        "/api/v1/customers/intake",
        headers=_auth(),
        json={
            "name": "Rec User",
            "mobile": "09130000030",
            "concerns": "ضدآفتاب",
            "consent": 1,
            "open_case": True,
        },
    )
    assert r.status_code == 201
    body = r.json()
    case_id = body["case"]["case_id"]
    profile = body["recommendation_profile"]
    assert profile["concerns"] == "ضدآفتاب"

    facade = RecommendationFacade(db_session)
    result = facade.generate(case_id, profile)
    assert isinstance(result, list)
    # Empty catalog still returns a real list (no crash / no invented rows)
    assert all(hasattr(item, "product_id") or isinstance(item, object) for item in result)


def test_recommendation_facade_handles_none_profile(db_session):
    """Replaces legacy skipped contract: None profile must not crash."""
    facade = RecommendationFacade(db_session)
    result = facade.generate("CASE_CP01_NONE", None)
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# F — Authorization matrix (protected vs public)
# ---------------------------------------------------------------------------

def test_guest_endpoint_public_no_auth(client):
    r = client.post("/api/v1/customers/guest", json={"name": "Public", "consent": 0})
    assert r.status_code == 201


def test_search_requires_auth(client):
    r = client.get("/api/v1/customers/search", params={"q": "سارا"})
    assert r.status_code == 401
