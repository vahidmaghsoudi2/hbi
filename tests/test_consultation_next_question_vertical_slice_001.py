"""Acceptance tests for HBI-CONSULTATION-NEXT-QUESTION-VERTICAL-SLICE-001."""
from __future__ import annotations

import json

from app.models.case import Case
from app.models.customer import Customer
from app.models.evidence import Evidence
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_knowledge import ProductKnowledge
from app.models.profile_fact import ProfileFact
from app.reasoning.scoring import MatchScoringEngine
from app.services.profile_fact_context_service import ProfileFactContextService
from app.services.skin_next_question_service import (
    FACTOR_KEY,
    QUESTION_ID,
    SkinNextQuestionService,
)


def _token(client, customer_id):
    response = client.post("/api/v1/auth/pilot-token", json={"customer_id": customer_id})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _setup_skin_case(db_session):
    customer = Customer(
        customer_id="CUST-NQ-001",
        name="Skin Next Question Customer",
        consent_to_store_data=1,
        concerns=None,
    )
    case = Case(
        case_id="CASE-NQ-001",
        customer_id=customer.customer_id,
        case_type="OPEN",
    )
    products = [
        ("PROD-NQ-HYDRATION", "hydration"),
        ("PROD-NQ-SUN", "sun protection"),
    ]
    db_session.add_all([customer, case])
    for product_id, use_case in products:
        product = Product(
            product_id=product_id,
            brand="HBI Test",
            product_name=product_id,
            identity_status="VERIFIED",
            identity_confidence=1.0,
            qa_verdict="VALID",
            status="ACTIVE",
        )
        knowledge = ProductKnowledge(
            product_knowledge_id=f"PK-{product_id}",
            product_id=product_id,
            known_use_cases=use_case,
            claimed_benefits=use_case,
            evidence_status="SUPPORTED",
            knowledge_confidence=1.0,
        )
        evidence = Evidence(
            evidence_id=f"EV-{product_id}",
            product_id=product_id,
            claim_id=f"CL-{product_id}",
            source_type="PEER_REVIEWED",
            source_reference=f"test://{product_id}",
            claim=f"approved {use_case} evidence",
            field="claimed_benefits",
            claim_type="FACT",
            evidence_strength="HIGH",
            evidence_status="SUPPORTED",
            qa_status="APPROVED",
            conflict_status="NONE",
        )
        inventory = Inventory(
            inventory_id=f"INV-{product_id}",
            product_id=product_id,
            quantity_available=10,
            quantity_reserved=0,
            quantity_damaged=0,
            stock_status="active",
            sale_price_usd=10.0,
        )
        db_session.add_all([product, knowledge, evidence])
        db_session.flush()
        db_session.add(inventory)
    db_session.commit()
    return customer, case


def test_missing_skin_input_produces_one_bounded_question(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)

    response = client.get(
        f"/api/v1/recommendations/next-question/{case.case_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "QUESTION_REQUIRED"
    question = body["question"]
    assert question["question_id"] == QUESTION_ID
    assert question["factor"] == FACTOR_KEY
    assert question["mode"] == "MISSING_INPUT"
    assert len(question["options"]) == 2
    assert {item["value"] for item in question["options"]} == {
        "hydration",
        "sun_protection",
    }
    assert question["evidence_gap"]["status"] == "MISSING"
    assert question["evidence_gap"]["gap_id"] == f"{case.case_id}:{QUESTION_ID}"


def test_known_skin_input_produces_no_question(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)

    response = client.get(
        f"/api/v1/recommendations/next-question/{case.case_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["status"] == "QUESTION_REQUIRED"

    # Current consultation input is the authoritative known value for this attempt.
    from app.services.skin_next_question_service import SkinNextQuestionService

    assert SkinNextQuestionService(db_session).get_question(
        case, {"concerns": "hydration"}
    ) is None


def test_answer_is_captured_in_case_and_not_profilefact(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        f"/api/v1/recommendations/next-question/{case.case_id}/answer",
        headers=headers,
        json={"question_id": QUESTION_ID, "answer": "hydration"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["source"] == "CURRENT_CASE_CONSULTATION"

    db_session.expire_all()
    persisted_case = db_session.get(Case, case.case_id)
    state = json.loads(persisted_case.evidence_gaps)
    assert state["answers"][-1]["value"] == "hydration"
    assert state["answers"][-1]["source"] == "CURRENT_CASE_CONSULTATION"
    assert state["gaps"][-1]["status"] == "RESOLVED"
    assert db_session.query(ProfileFact).filter_by(
        customer_id=customer.customer_id,
        attribute_key=FACTOR_KEY,
    ).count() == 0


def test_answer_a_and_b_rerun_existing_recommendation_with_observable_effect(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)
    headers = {"Authorization": f"Bearer {token}"}

    for answer, expected_product in [
        ("hydration", "PROD-NQ-HYDRATION"),
        ("sun_protection", "PROD-NQ-SUN"),
    ]:
        answered = client.post(
            f"/api/v1/recommendations/next-question/{case.case_id}/answer",
            headers=headers,
            json={"question_id": QUESTION_ID, "answer": answer},
        )
        assert answered.status_code == 200, answered.text

        generated = client.post(
            "/api/v1/recommendations/generate",
            headers=headers,
            json={"case_id": case.case_id, "customer_profile": {}},
        )
        assert generated.status_code == 200, generated.text
        body = generated.json()
        assert body
        assert [item["product_id"] for item in body] == [expected_product]
        assert body[0]["eligibility_status"] == "ELIGIBLE"
        assert body[0]["need_match_score"] == 1.0

    # The same Case has been re-evaluated with a different current answer.
    db_session.expire_all()
    rows = db_session.query(
        # Querying both product recommendations proves the prior decision was updated,
        # not that a second recommendation algorithm was introduced.
        __import__("app.models.recommendation", fromlist=["Recommendation"]).Recommendation
    ).filter_by(case_id=case.case_id).all()
    assert len(rows) == 2
    by_product = {row.product_id: row for row in rows}
    assert by_product["PROD-NQ-HYDRATION"].eligibility_status == "INELIGIBLE_PENDING_REVIEW"
    assert by_product["PROD-NQ-SUN"].eligibility_status == "ELIGIBLE"


def test_current_consultation_overrides_profile_fact_for_question_boundary(client, db_session):
    customer, case = _setup_skin_case(db_session)
    db_session.add(ProfileFact(
        profile_fact_id="PF-NQ-CONCERNS",
        customer_id=customer.customer_id,
        attribute_key="concerns",
        value="hydration",
        value_state="KNOWN",
        provenance="CUSTOMER",
        status="ACTIVE",
    ))
    db_session.commit()

    service = SkinNextQuestionService(db_session)
    assert service.get_question(case, {"concerns": "sun_protection"}) is None
    profile = ProfileFactContextService(db_session).build(
        case, {"concerns": "sun_protection"}
    )
    assert profile["concerns"] == "sun_protection"
    assert profile["_profile_fact_context"]["sources"]["concerns"]["source"] == "CURRENT_CONSULTATION"


def test_unknown_profile_fact_triggers_clarification_without_legacy_fallback(client, db_session):
    customer, case = _setup_skin_case(db_session)
    customer.concerns = "hydration"
    db_session.add(ProfileFact(
        profile_fact_id="PF-NQ-UNKNOWN",
        customer_id=customer.customer_id,
        attribute_key="concerns",
        value=None,
        value_state="UNKNOWN",
        provenance="CUSTOMER",
        status="ACTIVE",
    ))
    db_session.commit()

    question = SkinNextQuestionService(db_session).get_question(case)
    assert question["mode"] == "CLARIFICATION"
    assert question["evidence_gap"]["status"] == "UNKNOWN"
    profile = ProfileFactContextService(db_session).build(case, {})
    assert "concerns" not in profile
    assert profile["_profile_fact_context"]["unknowns"][0]["profile_fact_id"] == "PF-NQ-UNKNOWN"


def test_conflicting_active_profile_facts_trigger_clarification_boundary(client, db_session):
    customer, case = _setup_skin_case(db_session)
    db_session.add_all([
        ProfileFact(
            profile_fact_id="PF-NQ-CONFLICT-A",
            customer_id=customer.customer_id,
            attribute_key="concerns",
            value="hydration",
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ),
        ProfileFact(
            profile_fact_id="PF-NQ-CONFLICT-B",
            customer_id=customer.customer_id,
            attribute_key="concerns",
            value="sun protection",
            value_state="KNOWN",
            provenance="IMPORTED",
            status="ACTIVE",
        ),
    ])
    db_session.commit()

    question = SkinNextQuestionService(db_session).get_question(case)
    assert question["mode"] == "CLARIFICATION"
    assert question["evidence_gap"]["status"] == "CONFLICTED"
    assert set(question["evidence_gap"]["profile_fact_ids"]) == {
        "PF-NQ-CONFLICT-A",
        "PF-NQ-CONFLICT-B",
    }


def test_answer_rejects_unbounded_value(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)

    response = client.post(
        f"/api/v1/recommendations/next-question/{case.case_id}/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"question_id": QUESTION_ID, "answer": "invented_need"},
    )
    assert response.status_code == 422


def test_frozen_scoring_formula_is_unchanged():
    engine = MatchScoringEngine()
    result = engine.calculate(
        need_match=1.0,
        evidence_score=1.0,
        inventory_score=1.0,
    )
    assert result["final_score"] == 1.0
    assert result["confidence"] == 1.0
    assert result["eligibility"] == "ELIGIBLE"
