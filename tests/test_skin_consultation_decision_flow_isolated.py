"""Isolated regression tests for consultation source, line and evidence boundaries."""

import json

from app.models.case import Case
from app.models.customer import Customer
from app.models.profile_fact import ProfileFact
from app.services.profile_fact_context_service import ProfileFactContextService
from app.services.recommendation_service import RecommendationService
from app.services.skin_next_question_service import SkinNextQuestionService


def _customer_case(db_session, *, case_type="SKIN", **customer_fields):
    customer = Customer(
        customer_id="CUST-SKIN-DECISION-001",
        name="Isolated Decision Customer",
        consent_to_store_data=1,
        **customer_fields,
    )
    case = Case(
        case_id="CASE-SKIN-DECISION-001",
        customer_id=customer.customer_id,
        case_type=case_type,
    )
    db_session.add_all([customer, case])
    db_session.commit()
    return customer, case


def test_profile_dimensions_do_not_contaminate_skin_concerns(db_session):
    customer, case = _customer_case(
        db_session,
        concerns="آبرسان",
        skin_profile="sensitive",
        hair_profile="خشکی مو",
        scalp_profile="چربی پوست سر",
    )

    profile = ProfileFactContextService(db_session).build(case, {})
    state = RecommendationService(db_session)._build_decision_state(case.case_id, profile)

    assert profile["concerns"] == "آبرسان"
    assert profile["skin_profile"] == "sensitive"
    assert profile["hair_profile"] == "خشکی مو"
    assert profile["scalp_profile"] == "چربی پوست سر"
    assert [factor["value"] for factor in state["factors"]] == ["آبرسان"]


def test_profile_fact_context_projects_all_supported_profile_keys_separately(db_session):
    customer, case = _customer_case(db_session)
    facts = [
        ("skin_profile", "sensitive"),
        ("hair_profile", "dry hair"),
        ("scalp_profile", "oily scalp"),
        ("age_range", "25-34"),
        ("concerns", "hydration"),
    ]
    for index, (key, value) in enumerate(facts):
        db_session.add(ProfileFact(
            profile_fact_id=f"PF-SKIN-DECISION-{index}",
            customer_id=customer.customer_id,
            attribute_key=key,
            value=value,
            value_state="KNOWN",
            provenance="CUSTOMER",
            status="ACTIVE",
        ))
    db_session.commit()

    profile = ProfileFactContextService(db_session).build(case, {})

    assert profile["skin_profile"] == "sensitive"
    assert profile["hair_profile"] == "dry hair"
    assert profile["scalp_profile"] == "oily scalp"
    assert profile["age_range"] == "25-34"
    assert profile["concerns"] == "hydration"
    sources = profile["_profile_fact_context"]["sources"]
    assert all(sources[key]["source"] == "PROFILE_FACT" for key, _ in facts)


def test_skin_consultation_answer_cannot_authorize_an_unanswered_need(db_session):
    _, case = _customer_case(db_session)
    SkinNextQuestionService(db_session).capture_answer(
        case, "skin.primary_need.v1", "hydration"
    )
    service = RecommendationService(db_session)

    assert service._has_minimum_consultation_evidence(case.case_id, ["hydration"])
    assert not service._has_minimum_consultation_evidence(
        case.case_id, ["hydration", "acne care"]
    )
    assert not service._has_minimum_consultation_evidence(case.case_id, ["acne care"])


def test_latest_case_answer_is_the_only_consultation_evidence(db_session):
    _, case = _customer_case(db_session)
    question = SkinNextQuestionService(db_session)
    question.capture_answer(case, "skin.primary_need.v1", "hydration")
    question.capture_answer(case, "skin.primary_need.v1", "sun_protection")
    service = RecommendationService(db_session)

    assert service._has_minimum_consultation_evidence(
        case.case_id, ["sun protection"]
    )
    assert not service._has_minimum_consultation_evidence(
        case.case_id, ["hydration"]
    )


def test_persisted_operator_notes_remain_visible_to_medical_context_detection(db_session):
    _, case = _customer_case(db_session, operator_notes="pregnancy context")
    profile = ProfileFactContextService(db_session).build(
        case, {"medical_notes": "routine note"}
    )

    active, _ = RecommendationService(db_session)._detect_medical_context(profile, [])

    assert profile["operator_notes"] == "pregnancy context"
    assert active is True
