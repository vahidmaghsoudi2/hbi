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
    # Existing auth tests cover the pilot-token endpoint. This slice creates
    # signed test tokens directly so its cases do not consume the shared
    # pilot-token rate-limit budget used by the broader suite.
    from app.core.auth import create_access_token

    return create_access_token({"sub": customer_id})


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
    assert len(question["options"]) == 6
    assert {item["value"] for item in question["options"]} == {
        "ضدآفتاب",
        "آبرسان",
        "لک صورت",
        "پوست حساس",
        "ضدچروک",
        "کنترل چربی",
    }
    assert question["evidence_gap"]["status"] == "MISSING"
    assert question["evidence_gap"]["gap_id"] == f"{case.case_id}:{QUESTION_ID}"


def test_known_quick_intake_input_still_requires_case_owned_answer(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)

    response = client.get(
        f"/api/v1/recommendations/next-question/{case.case_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.json()["status"] == "QUESTION_REQUIRED"

    # A Quick Intake/profile value is not yet Case-owned evidence.
    # The explicit answer endpoint must persist it before recommendation.
    from app.services.skin_next_question_service import SkinNextQuestionService

    question = SkinNextQuestionService(db_session).get_question(
        case, {"concerns": "hydration"}
    )
    assert question is not None
    assert question["mode"] == "MISSING_INPUT"


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

    follow_up = client.get(
        f"/api/v1/recommendations/next-question/{case.case_id}",
        headers=headers,
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["status"] == "NO_QUESTION"


def test_answer_a_and_b_rerun_existing_recommendation_with_observable_effect(client, db_session):
    customer, case = _setup_skin_case(db_session)
    token = _token(client, customer.customer_id)
    headers = {"Authorization": f"Bearer {token}"}

    observed = []
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
        product_ids = [item["product_id"] for item in body]
        assert expected_product in product_ids
        assert all(item["eligibility_status"] == "ELIGIBLE" for item in body)
        selected = next(item for item in body if item["product_id"] == expected_product)
        assert selected["need_match_score"] == 1.0
        observed.append(expected_product)

    # The same Case was re-evaluated by the existing recommendation path with
    # a different current answer; the observable decision changed.
    assert observed == ["PROD-NQ-HYDRATION", "PROD-NQ-SUN"]


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
    # Current request input overrides the ProfileFact value for projection,
    # but it is not a persisted answer owned by this Case.
    question = service.get_question(case, {"concerns": "sun_protection"})
    assert question is not None
    assert question["mode"] == "MISSING_INPUT"
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


def test_structured_consultation_captures_all_eight_case_owned_answers(client, db_session):
    customer, case = _setup_skin_case(db_session)
    service = SkinNextQuestionService(db_session)
    answers = [
        (QUESTION_ID, ["آبرسان", "ضدآفتاب"]),
        ("skin.current_type.v1", ["خشک", "حساس"]),
        ("skin.duration.v1", "one_to_four_weeks"),
        ("skin.self_reported_severity.v1", "moderate"),
        ("skin.affected_area.v1", "face"),
        ("skin.aggravating_factors.v1", ["sun_exposure", "cosmetics"]),
        ("skin.product_history.v1", "مرطوب‌کننده و ضدآفتاب؛ واکنش گزارش‌شده: سوزش"),
        ("skin.additional_context.v1", "توضیح تکمیلی ثبت‌شده توسط مشتری"),
    ]

    for expected_question_id, answer in answers:
        question = service.get_question(case, include_details=True)
        assert question is not None
        assert question["question_id"] == expected_question_id
        result = service.capture_answer(case, expected_question_id, answer)
        assert result["source"] == "CURRENT_CASE_CONSULTATION"

    assert service.get_question(case, include_details=True) is None
    db_session.expire_all()
    persisted = db_session.get(Case, case.case_id)
    state = json.loads(persisted.evidence_gaps)
    by_question = {item["question_id"]: item for item in state["answers"]}

    assert by_question[QUESTION_ID]["value"] == ["آبرسان", "ضدآفتاب"]
    assert by_question["skin.current_type.v1"]["value"] == ["خشک", "حساس"]
    assert by_question["skin.duration.v1"]["value"] == "one_to_four_weeks"
    assert by_question["skin.self_reported_severity.v1"]["value"] == "moderate"
    assert by_question["skin.affected_area.v1"]["value"] == "face"
    assert by_question["skin.aggravating_factors.v1"]["value"] == ["sun_exposure", "cosmetics"]
    assert by_question["skin.product_history.v1"]["value"].startswith("مرطوب‌کننده")
    assert by_question["skin.additional_context.v1"]["value"].startswith("توضیح تکمیلی")
    current = SkinNextQuestionService.current_input_from_case(persisted)
    assert current["concerns"] == ["آبرسان", "ضدآفتاب"]
    assert current["skin_profile"] == ["خشک", "حساس"]


def test_structured_consultation_preserves_unknown_without_profile_fallback(client, db_session):
    customer, case = _setup_skin_case(db_session)
    customer.skin_profile = "خشک"
    db_session.commit()
    service = SkinNextQuestionService(db_session)
    service.capture_answer(case, QUESTION_ID, ["آبرسان"])
    result = service.capture_answer(case, "skin.current_type.v1", ["unknown"])
    assert result["value_state"] == "UNKNOWN"
    current = service.current_input_from_case(case)
    assert current["concerns"] == ["آبرسان"]
    assert current["skin_profile"] == ["unknown"]
    state = json.loads(case.evidence_gaps)
    assert state["answers"][-1]["value_state"] == "UNKNOWN"


def test_structured_primary_question_keeps_only_six_approved_homepage_options(client, db_session):
    _, case = _setup_skin_case(db_session)
    question = SkinNextQuestionService(db_session).get_question(case)
    assert question["question_id"] == QUESTION_ID
    assert {item["value"] for item in question["options"]} == {
        "ضدآفتاب", "آبرسان", "لک صورت", "پوست حساس", "ضدچروک", "کنترل چربی"
    }
