"""Isolated regression tests for consultation source, line and evidence boundaries."""

from app.models.case import Case
from app.models.customer import Customer
from app.models.profile_fact import ProfileFact
from app.services.profile_fact_context_service import ProfileFactContextService
from app.services.recommendation_service import RecommendationService
from app.services.skin_next_question_service import (
    CONTRACT_VERSION,
    LEGACY_QUESTION_ID,
    OPTIONS,
    QUESTION_ID,
    SkinNextQuestionService,
)


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


def test_need_factor_keeps_customer_legacy_provenance(db_session):
    _, case = _customer_case(db_session, concerns="آبرسان")
    profile = ProfileFactContextService(db_session).build(case, {})
    state = RecommendationService(db_session)._build_decision_state(case.case_id, profile)

    assert state["factors"][0]["source"] == "customer_legacy"


def test_need_factor_keeps_current_consultation_provenance(db_session):
    _, case = _customer_case(db_session)
    profile = ProfileFactContextService(db_session).build(
        case, {"concerns": "آبرسان"}
    )
    state = RecommendationService(db_session)._build_decision_state(case.case_id, profile)

    assert state["factors"][0]["source"] == "customer_input"


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
    state = RecommendationService(db_session)._build_decision_state(case.case_id, profile)
    assert state["factors"][0]["source"] == "profile_fact"


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


def test_zero_need_match_remains_eligible_for_skin_case(db_session):
    _, case = _customer_case(db_session)
    SkinNextQuestionService(db_session).capture_answer(
        case, "skin.primary_need.v1", "hydration"
    )
    decision_state = {
        "case_id": case.case_id,
        "needs": ["hydration"],
        "unknowns": [],
        "consultation_evidence_ready": True,
        "medical_context_active": False,
    }
    engine_result = {
        "claim_boundary_violations": [],
        "conflicts": [],
    }

    eligibility = RecommendationService(db_session)._map_eligibility(
        engine_result,
        decision_state,
        need_match=0.0,
        evidence_score=1.0,
    )

    assert eligibility == "ELIGIBLE"


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
    assert profile["_profile_fact_context"]["sources"]["operator_notes"]["source"] == "CUSTOMER_LEGACY"
    assert active is True


def test_current_operator_and_medical_notes_have_consultation_provenance(db_session):
    _, case = _customer_case(db_session)
    profile = ProfileFactContextService(db_session).build(
        case,
        {
            "operator_notes": "pregnancy context",
            "medical_notes": "routine note",
        },
    )

    sources = profile["_profile_fact_context"]["sources"]
    assert sources["operator_notes"]["source"] == "CURRENT_CONSULTATION"
    assert sources["medical_notes"]["source"] == "CURRENT_CONSULTATION"
    assert sources["operator_notes"]["value"] == "pregnancy context"
    assert sources["medical_notes"]["value"] == "routine note"

    active, _ = RecommendationService(db_session)._detect_medical_context(profile, [])
    assert active is True



def test_six_need_question_contract_is_v2_and_legacy_v1_answers_remain_readable(db_session):
    import json

    _, case = _customer_case(db_session)
    service = SkinNextQuestionService(db_session)

    question = service.get_question(case)
    assert QUESTION_ID == "skin.primary_need.v2"
    assert LEGACY_QUESTION_ID == "skin.primary_need.v1"
    assert CONTRACT_VERSION == "2"
    assert question["question_id"] == QUESTION_ID
    assert len(OPTIONS) == 6
    assert len(question["options"]) == 6

    # Historical v1 clients may still submit the two original canonical values.
    legacy_result = service.capture_answer(case, LEGACY_QUESTION_ID, "hydration")
    state = json.loads(case.evidence_gaps)
    assert state["version"] == "2"
    assert legacy_result["question_id"] == LEGACY_QUESTION_ID
    assert service.current_input_from_case(case) == {"concerns": ["hydration"]}
    assert RecommendationService(db_session)._has_minimum_consultation_evidence(
        case.case_id, ["hydration"]
    )

    # A new v2 answer upgrades the same Case envelope and replaces the old answer.
    service.capture_answer(case, QUESTION_ID, ["آبرسان", "لک صورت"])
    upgraded = json.loads(case.evidence_gaps)
    assert upgraded["version"] == "2"
    assert len(upgraded["answers"]) == 1
    assert upgraded["answers"][0]["question_id"] == QUESTION_ID
    assert upgraded["answers"][0]["value"] == ["آبرسان", "لک صورت"]
    assert len(upgraded["gaps"]) == 1
    assert upgraded["gaps"][0]["question_id"] == QUESTION_ID
    assert service.current_input_from_case(case) == {"concerns": ["آبرسان", "لک صورت"]}

    # The old contract cannot silently submit one of the newly introduced v2 labels.
    try:
        service.capture_answer(case, LEGACY_QUESTION_ID, "لک صورت")
    except ValueError:
        pass
    else:
        raise AssertionError("Legacy v1 contract unexpectedly accepted a v2-only option")


def test_explicit_generate_input_keeps_precedence_but_mismatch_fails_evidence_gate(db_session):
    _, case = _customer_case(db_session)
    question_service = SkinNextQuestionService(db_session)
    question_service.capture_answer(case, QUESTION_ID, ["آبرسان"])

    # PR #226 explicitly preserves request input as the highest-precedence
    # current-consultation value. A mismatch must therefore fail the Case
    # evidence subset gate rather than silently authorize another Need.
    profile = ProfileFactContextService(db_session).build(
        case, {"concerns": "لک صورت"}
    )
    recommendation_service = RecommendationService(db_session)
    decision_state = recommendation_service._build_decision_state(
        case.case_id, profile
    )
    generated_needs = recommendation_service._generate_needs_from_decision_state(
        decision_state
    )

    assert generated_needs == ["brightening"]
    assert decision_state["consultation_evidence_ready"] is False
    assert not recommendation_service._has_minimum_consultation_evidence(
        case.case_id, generated_needs
    )
