"""HBI-CONSULTATION-VERTICAL-SLICE-001 — HTTP acceptance matrix.

Contracts (Issue #214 / Phase 1 decisions on master):
- Customer + Case ownership via JWT (pilot-token in tests)
- Generate uses legacy Customer/consultation merge (not ProfileFact)
- Only ELIGIBLE recommendations are returned/persisted
- Empty list is a valid outcome (no fabricated Evidence Gap API)
- Optional Feedback path remains available

No Home redesign, no scoring changes, no new entities.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

TEST_DB = Path(__file__).resolve().parents[1] / "data" / "hbi_consultation_vs_001.db"


@pytest.fixture()
def client(monkeypatch):
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{TEST_DB}")
    monkeypatch.setenv("HBI_ENV", "development")

    import importlib
    import app.database as database

    importlib.reload(database)
    database.init_db()

    from app.core.deps import get_db
    from app.main import app
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.evidence import Evidence
    from app.models.product import Product
    from app.models.product_knowledge import ProductKnowledge
    from scripts.seed_products_from_records import seed

    Session = sessionmaker(bind=database.engine)
    session = Session()
    seed(session)

    product = session.query(Product).filter_by(product_id="ISDIN-FOTOUTRA100-50ML").one()
    product.status = "ACTIVE"
    product.qa_verdict = "VALID"
    product.identity_status = "VERIFIED"
    pk = session.query(ProductKnowledge).filter_by(
        product_id="ISDIN-FOTOUTRA100-50ML"
    ).one()
    pk.known_use_cases = "sun protection"
    session.add(
        Evidence(
            evidence_id="EV-CVS001-APPROVED",
            product_id="ISDIN-FOTOUTRA100-50ML",
            source_type="INDEPENDENT",
            source_reference="TEST-CVS-001",
            claim="approved support for sunscreen consultation slice",
            claim_type="FACT",
            evidence_status="SUPPORTED",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
    )
    session.add(
        Customer(
            customer_id="CUST-CVS-1",
            name="Consultation VS Owner",
            consent_to_store_data=1,
        )
    )
    session.add(
        Customer(
            customer_id="CUST-CVS-2",
            name="Consultation VS Other",
            consent_to_store_data=1,
        )
    )
    session.add(Case(case_id="CASE-CVS-FOREIGN", customer_id="CUST-CVS-2", case_type="OPEN"))
    session.commit()
    session.close()

    def _override_db():
        s = Session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    try:
        database.engine.dispose()
    except Exception:
        pass
    if TEST_DB.exists():
        try:
            TEST_DB.unlink()
        except PermissionError:
            pass


def _token(client: TestClient, customer_id: str) -> str:
    r = client.post("/api/v1/auth/pilot-token", json={"customer_id": customer_id})
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token
    return token


def test_unauthenticated_generate_returns_401(client):
    r = client.post(
        "/api/v1/recommendations/generate",
        json={"case_id": "CASE-ANY", "customer_profile": {"concerns": "ضدآفتاب"}},
    )
    assert r.status_code == 401


def test_foreign_case_generate_returns_403(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/recommendations/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "case_id": "CASE-CVS-FOREIGN",
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert r.status_code == 403


def test_missing_case_generate_returns_404(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/recommendations/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "case_id": "CASE-DOES-NOT-EXIST",
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert r.status_code == 404


def test_owned_case_consultation_generate_persist_retrieve_and_feedback(client):
    token = _token(client, "CUST-CVS-1")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": "CUST-CVS-1", "case_type": "OPEN"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["case_id"]
    assert created.json()["customer_id"] == "CUST-CVS-1"

    gen = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": case_id,
            "customer_profile": {"concerns": "ضدآفتاب"},
        },
    )
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    rec = body[0]
    assert rec["product_id"] == "ISDIN-FOTOUTRA100-50ML"
    assert rec.get("eligibility_status") == "ELIGIBLE"
    assert rec.get("case_id") == case_id
    assert rec.get("ranking_reasons")

    listed = client.get(f"/api/v1/recommendations/case/{case_id}", headers=headers)
    assert listed.status_code == 200, listed.text
    listed_body = listed.json()
    assert any(item.get("product_id") == "ISDIN-FOTOUTRA100-50ML" for item in listed_body)

    fb = client.post(
        "/api/v1/specialist/feedback",
        headers=headers,
        json={
            "case_id": case_id,
            "source": "CUSTOMER",
            "outcome": "ACCEPTED",
            "recommendation_id": rec.get("recommendation_id"),
            "comment": "consultation-vs-001",
        },
    )
    assert fb.status_code == 200, fb.text
    assert fb.json().get("case_id") == case_id
    assert fb.json().get("source") == "CUSTOMER"


def test_no_eligible_product_returns_empty_list(client):
    """non-matching concern → 200 → [] → no persisted recommendation for the case."""
    token = _token(client, "CUST-CVS-1")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": "CUST-CVS-1", "case_type": "OPEN"},
    )
    assert created.status_code == 201, created.text
    case_id = created.json()["case_id"]

    # Concerns that do not map to the seeded sunscreen use-case surface.
    gen = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": case_id,
            "customer_profile": {"concerns": "xyz-noncanonical-need-99"},
        },
    )
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert isinstance(body, list)
    # Strict: no eligible product must yield an empty generate payload.
    # Do not allow a non-empty ELIGIBLE list to satisfy this test.
    assert body == [], (
        "expected no recommendations for non-matching concern; "
        f"got {len(body)} item(s): {body!r}"
    )

    listed = client.get(f"/api/v1/recommendations/case/{case_id}", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json() == [], (
        "expected no persisted recommendations for case after empty generate; "
        f"got {listed.json()!r}"
    )


def test_create_case_for_other_customer_returns_403(client):
    token = _token(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/cases/",
        headers={"Authorization": f"Bearer {token}"},
        json={"customer_id": "CUST-CVS-2", "case_type": "OPEN"},
    )
    assert r.status_code == 403


def _runtime_session():
    import app.database as database
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=database.engine)()


def _customer_auth_headers(customer_id: str):
    from app.core.auth import create_access_token
    token = create_access_token({"sub": customer_id})
    return {"Authorization": f"Bearer {token}"}


def _create_owned_case(client, customer_id: str):
    headers = _customer_auth_headers(customer_id)
    created = client.post(
        "/api/v1/cases/",
        headers=headers,
        json={"customer_id": customer_id, "case_type": "OPEN"},
    )
    assert created.status_code == 201, created.text
    return headers, created.json()["case_id"]


def test_profile_fact_concerns_supplies_recommendation_and_trace(client):
    from app.models.profile_fact import ProfileFact

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        db.add(ProfileFact(
            profile_fact_id="PF-VS002-CONCERNS",
            customer_id="CUST-CVS-1",
            attribute_key="concerns",
            value="ضدآفتاب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={"case_id": case_id, "customer_profile": {}},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body) >= 1
    reasons = body[0]["ranking_reasons"]
    assert "PF-VS002-CONCERNS" in reasons
    assert "PROFILE_FACT" in reasons


def test_current_consultation_overrides_profile_fact(client):
    from app.models.profile_fact import ProfileFact

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        db.add(ProfileFact(
            profile_fact_id="PF-VS002-CURRENT-OVERRIDE",
            customer_id="CUST-CVS-1",
            attribute_key="concerns",
            value="ضدآفتاب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={
            "case_id": case_id,
            "customer_profile": {"concerns": "xyz-noncanonical-current"},
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_profile_fact_overrides_legacy_customer_field(client):
    from app.models.customer import Customer
    from app.models.profile_fact import ProfileFact

    db = _runtime_session()
    try:
        customer = db.get(Customer, "CUST-CVS-1")
        customer.concerns = "xyz-noncanonical-legacy"
        db.add(ProfileFact(
            profile_fact_id="PF-VS002-LEGACY-OVERRIDE",
            customer_id=customer.customer_id,
            attribute_key="concerns",
            value="ضدآفتاب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        db.commit()
    finally:
        db.close()

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    response = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={"case_id": case_id, "customer_profile": {}},
    )
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 1


def test_profile_fact_non_trusted_lifecycle_states_are_excluded(client):
    from app.models.profile_fact import ProfileFact
    from app.services.profile_fact_context_service import ProfileFactContextService

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        for index, state in enumerate(["REVOKED", "SUPERSEDED", "STALE", "CONFLICTED"]):
            db.add(ProfileFact(
                profile_fact_id=f"PF-VS002-EXCLUDED-{index}",
                customer_id="CUST-CVS-1",
                attribute_key="concerns",
                value=f"excluded-{index}",
                value_state="KNOWN",
                provenance="CUSTOMER",
                status=state,
            ))
        db.commit()
        case = db.get(__import__("app.models.case", fromlist=["Case"]).Case, case_id)
        profile = ProfileFactContextService(db).build(case, {})
        assert "concerns" not in profile
        excluded_ids = {
            item["profile_fact_id"]
            for item in profile["_profile_fact_context"]["excluded"]
        }
        assert excluded_ids == {
            "PF-VS002-EXCLUDED-0",
            "PF-VS002-EXCLUDED-1",
            "PF-VS002-EXCLUDED-2",
            "PF-VS002-EXCLUDED-3",
        }
    finally:
        db.close()


@pytest.mark.parametrize("value_state", ["UNKNOWN", "PREFER_NOT_TO_SAY", "NOT_APPLICABLE"])
def test_profile_fact_unknown_family_is_preserved_without_legacy_fallback(client, value_state):
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.profile_fact import ProfileFact
    from app.services.profile_fact_context_service import ProfileFactContextService

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        customer = db.get(Customer, "CUST-CVS-1")
        customer.concerns = "legacy-value-must-not-be-used"
        fact_id = f"PF-VS002-{value_state}"
        db.add(ProfileFact(
            profile_fact_id=fact_id,
            customer_id=customer.customer_id,
            attribute_key="concerns",
            value=None,
            value_state=value_state,
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        db.commit()
        case = db.get(Case, case_id)
        profile = ProfileFactContextService(db).build(case, {})
        assert profile.get("concerns") is None
        source = profile["_profile_fact_context"]["sources"]["concerns"]
        assert source["profile_fact_id"] == fact_id
        assert source["value_state"] == value_state
        assert profile["_profile_fact_context"]["unknowns"][0]["profile_fact_id"] == fact_id
    finally:
        db.close()


def test_duplicate_active_profile_facts_are_visible_conflict_and_unresolved(client):
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.profile_fact import ProfileFact
    from app.services.profile_fact_context_service import ProfileFactContextService

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        customer = db.get(Customer, "CUST-CVS-1")
        customer.concerns = "legacy-must-not-win"
        db.add_all([
            ProfileFact(
                profile_fact_id="PF-VS002-DUP-1",
                customer_id=customer.customer_id,
                attribute_key="concerns",
                value="ضدآفتاب",
                value_state="KNOWN",
                provenance="CUSTOMER",
                status="ACTIVE",
            ),
            ProfileFact(
                profile_fact_id="PF-VS002-DUP-2",
                customer_id=customer.customer_id,
                attribute_key="concerns",
                value="xyz-conflict",
                value_state="KNOWN",
                provenance="IMPORTED",
                status="ACTIVE",
            ),
        ])
        db.commit()
        case = db.get(Case, case_id)
        profile = ProfileFactContextService(db).build(case, {})
        assert "concerns" not in profile
        conflicts = profile["_profile_fact_context"]["conflicts"]
        assert len(conflicts) == 1
        assert conflicts[0]["state"] == "CONFLICTED"
        assert set(conflicts[0]["profile_fact_ids"]) == {
            "PF-VS002-DUP-1",
            "PF-VS002-DUP-2",
        }
    finally:
        db.close()


def test_current_consultation_trace_does_not_claim_profile_fact_usage(client):
    from app.models.profile_fact import ProfileFact

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        db.add(ProfileFact(
            profile_fact_id="PF-VS002-OVERRIDDEN-TRACE",
            customer_id="CUST-CVS-1",
            attribute_key="concerns",
            value="ضدآفتاب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/recommendations/generate",
        headers=headers,
        json={"case_id": case_id, "customer_profile": {"concerns": "xyz-current"}},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_profile_fact_read_respects_withdrawn_consent(client):
    from app.models.case import Case
    from app.models.customer import Customer
    from app.models.profile_fact import ProfileFact
    from app.services.profile_fact_context_service import ProfileFactContextService

    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        customer = db.get(Customer, "CUST-CVS-1")
        db.add(ProfileFact(
            profile_fact_id="PF-VS002-CONSENT-WITHDRAWN",
            customer_id=customer.customer_id,
            attribute_key="concerns",
            value="ضدآفتاب",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
        customer.consent_to_store_data = 0
        db.commit()
        case = db.get(Case, case_id)
        profile = ProfileFactContextService(db).build(case, {})
        assert "concerns" not in profile
        assert profile["_profile_fact_context"]["excluded"][-1]["reason"] == "customer_consent_not_active"
    finally:
        db.close()


def test_customer_response_requires_authentication(client):
    r = client.post(
        "/api/v1/specialist/feedback/customer-response",
        json={
            "case_id": "CASE-ANY",
            "recommendation_id": "REC-ANY",
            "outcome": "ACCEPTED",
        },
    )
    assert r.status_code == 401


def test_customer_response_rejects_foreign_case(client):
    headers = _customer_auth_headers("CUST-CVS-1")
    r = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": "CASE-CVS-FOREIGN",
            "recommendation_id": "REC-ANY",
            "outcome": "ACCEPTED",
        },
    )
    assert r.status_code == 403


def test_customer_response_requires_existing_recommendation(client):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    r = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": "REC-DOES-NOT-EXIST",
            "outcome": "ACCEPTED",
        },
    )
    assert r.status_code == 422
    assert "Recommendation not found" in r.text


def test_customer_response_rejects_recommendation_from_other_case(client):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    _, other_case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        from app.models.recommendation import Recommendation
        db.add(Recommendation(
            recommendation_id="REC-CUSTOMER-RESPONSE-FOREIGN",
            case_id=other_case_id,
            product_id="ISDIN-FOTOUTRA100-50ML",
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
        ))
        db.commit()
    finally:
        db.close()

    r = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": "REC-CUSTOMER-RESPONSE-FOREIGN",
            "outcome": "REJECTED",
        },
    )
    assert r.status_code == 422
    assert "does not belong to the given case" in r.text


@pytest.mark.parametrize("outcome", ["ACCEPTED", "REJECTED", "PARTIAL", "FOLLOW_UP_NEEDED"])
def test_customer_response_accepts_documented_outcome_values(client, outcome):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        from app.models.recommendation import Recommendation
        db.add(Recommendation(
            recommendation_id=f"REC-CUSTOMER-OUTCOME-{outcome}",
            case_id=case_id,
            product_id="ISDIN-FOTOUTRA100-50ML",
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": f"REC-CUSTOMER-OUTCOME-{outcome}",
            "outcome": outcome.lower(),
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["outcome"] == outcome


def test_customer_response_allows_omitted_outcome(client):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        from app.models.recommendation import Recommendation
        db.add(Recommendation(
            recommendation_id="REC-CUSTOMER-OUTCOME-OMITTED",
            case_id=case_id,
            product_id="ISDIN-FOTOUTRA100-50ML",
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": "REC-CUSTOMER-OUTCOME-OMITTED",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["outcome"] is None


def test_customer_response_rejects_invalid_outcome(client):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        from app.models.recommendation import Recommendation
        db.add(Recommendation(
            recommendation_id="REC-CUSTOMER-OUTCOME-INVALID",
            case_id=case_id,
            product_id="ISDIN-FOTOUTRA100-50ML",
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": "REC-CUSTOMER-OUTCOME-INVALID",
            "outcome": "PURCHASED",
        },
    )
    assert response.status_code == 422, response.text
    assert "Expected one of" in response.text


def test_customer_response_persists_customer_source_and_is_retrievable(client):
    headers, case_id = _create_owned_case(client, "CUST-CVS-1")
    db = _runtime_session()
    try:
        from app.models.recommendation import Recommendation
        db.add(Recommendation(
            recommendation_id="REC-CUSTOMER-RESPONSE-001",
            case_id=case_id,
            product_id="ISDIN-FOTOUTRA100-50ML",
            eligibility_status="ELIGIBLE",
            ranking_score=1.0,
        ))
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/specialist/feedback/customer-response",
        headers=headers,
        json={
            "case_id": case_id,
            "recommendation_id": "REC-CUSTOMER-RESPONSE-001",
            "outcome": "ACCEPTED",
            "comment": "customer-response-001",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "CUSTOMER"
    assert body["case_id"] == case_id
    assert body["recommendation_id"] == "REC-CUSTOMER-RESPONSE-001"
    assert body["outcome"] == "ACCEPTED"

    listed = client.get(
        f"/api/v1/specialist/feedback/case/{case_id}",
        headers=headers,
    )
    assert listed.status_code == 200, listed.text
    assert any(
        item["feedback_id"] == body["feedback_id"]
        and item["source"] == "CUSTOMER"
        and item["recommendation_id"] == "REC-CUSTOMER-RESPONSE-001"
        for item in listed.json()
    )
