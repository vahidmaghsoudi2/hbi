import pytest

from app.domain.hair_consultation_engine import (
    HairCandidateOption,
    HairConsultationRequest,
    HairFact,
    HairProductEvidence,
    HairSpecialistRule,
    evaluate_hair_consultation,
)


def _fact(key, value="synthetic-value"):
    return HairFact(
        field_key=key,
        value=value,
        knowledge_state="KNOWN",
        source_ref=f"synthetic://case/{key}",
    )


def _evidence(**changes):
    values = {
        "evidence_ref": "SYNTHETIC-EVIDENCE-001",
        "source_ref": "synthetic://manufacturer/document/1",
        "status": "VERIFIED_APPLICABLE",
        "claim_id": "SYNTHETIC-CLAIM-001",
        "product_identity_ref": "SYNTHETIC-PRODUCT-001",
        "product_version": "product-v1",
        "market_region": "IR",
        "content_sha256": "a" * 64,
    }
    values.update(changes)
    return HairProductEvidence(**values)


def _rule(**changes):
    values = {
        "rule_ref": "SYNTHETIC-RULE-001",
        "rule_version": "rule-v1",
        "status": "ACTIVE",
        "scope": "HAIR_COLOR_RECOMMENDATION",
        "product_identity_ref": "SYNTHETIC-PRODUCT-001",
        "product_version": "product-v1",
        "market_region": "IR",
        "evidence_refs": ("SYNTHETIC-EVIDENCE-001",),
        "specialist_review_ref": "SYNTHETIC-SPECIALIST-REVIEW-001",
    }
    values.update(changes)
    return HairSpecialistRule(**values)


def _candidate(**changes):
    values = {
        "option_ref": "SYNTHETIC-OPTION-001",
        "summary": "Synthetic evidence-bound candidate label",
        "rank": 1,
        "rule_refs": ("SYNTHETIC-RULE-001",),
        "evidence_refs": ("SYNTHETIC-EVIDENCE-001",),
    }
    values.update(changes)
    return HairCandidateOption(**values)


def _request(**changes):
    values = {
        "case_id": "SYNTHETIC-HAIR-ENGINE-001",
        "synthetic_data": True,
        "case_version": "1",
        "target_version": "1",
        "service_kind": "CATALOG_READY",
        "required_fields": ("goal", "hair_history"),
        "facts": (_fact("goal"), _fact("hair_history")),
        "safety_state": "CLEAR",
        "product_identity_ref": "SYNTHETIC-PRODUCT-001",
        "product_version": "product-v1",
        "market_region": "IR",
        "evidence": (_evidence(),),
        "rules": (_rule(),),
        "candidates": (_candidate(),),
    }
    values.update(changes)
    return HairConsultationRequest(**values)


def test_valid_synthetic_candidate_is_reviewable_but_not_published_or_executable():
    result = evaluate_hair_consultation(_request())
    assert result.run_outcome == "SUCCESS"
    assert result.engine_state == "SUGGESTION_REVIEWABLE"
    assert result.consultation_status == "SYSTEM_REASONED_SUGGESTION"
    assert [item.option_ref for item in result.options] == ["SYNTHETIC-OPTION-001"]
    assert result.persistence == "COMPUTED_ONLY"
    assert result.publication_eligible is False
    assert not hasattr(result, "formula")
    assert not hasattr(result, "oxidant_percentage")
    assert not hasattr(result, "processing_time")


def test_engine_failure_has_no_consultation_state_or_options():
    result = evaluate_hair_consultation(_request(engine_ok=False))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)
    assert result.consultation_status is None
    assert result.options == ()


def test_real_case_is_blocked_by_synthetic_only_policy():
    result = evaluate_hair_consultation(_request(case_id="REAL-CLIENT-001", synthetic_data=False))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


def test_safety_stop_precedes_missing_data():
    result = evaluate_hair_consultation(
        _request(safety_state="STOP", facts=())
    )
    assert result.consultation_status == "SAFETY_STOP_NO_EXECUTION_SUGGESTION"
    assert result.reason_codes == ("SAFETY_CONCERN",)
    assert result.options == ()


def test_unknown_safety_status_is_a_data_gap_not_a_clearance():
    result = evaluate_hair_consultation(_request(safety_state="UNKNOWN"))
    assert result.consultation_status == "NEEDS_INFORMATION_OR_TEST"
    assert result.reason_codes == ("DATA_GAP",)
    assert "safety_status" in result.missing_information
    assert result.options == ()


def test_combination_consult_is_blocked_by_current_catalog_only_service_scope():
    result = evaluate_hair_consultation(_request(service_kind="COMBINATION_CONSULT"))
    assert result.consultation_status == "OUT_OF_V1_SCOPE"
    assert result.reason_codes == ("OUT_OF_SCOPE",)
    assert result.options == ()


def test_missing_required_case_fact_is_data_gap():
    result = evaluate_hair_consultation(_request(facts=(_fact("goal"),)))
    assert result.consultation_status == "NEEDS_INFORMATION_OR_TEST"
    assert result.reason_codes == ("DATA_GAP",)
    assert result.missing_information == ("hair_history",)


def test_conflicting_or_non_known_fact_does_not_count_as_complete():
    fact = HairFact("hair_history", None, "CONFLICT", "synthetic://conflict")
    result = evaluate_hair_consultation(_request(facts=(_fact("goal"), fact)))
    assert result.reason_codes == ("DATA_GAP",)
    assert result.missing_information == ("hair_history",)


def test_in_person_assessment_is_not_downgraded_to_routine_data_gap():
    result = evaluate_hair_consultation(_request(specialist_assessment_required=True))
    assert result.consultation_status == "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW"
    assert result.reason_codes == ("DATA_GAP",)
    assert result.options == ()


def test_missing_product_identity_is_data_gap():
    result = evaluate_hair_consultation(_request(product_identity_ref=None))
    assert result.consultation_status == "NEEDS_INFORMATION_OR_TEST"
    assert result.reason_codes == ("DATA_GAP",)
    assert "product_identity_ref" in result.missing_information


def test_unverified_retailer_only_evidence_is_knowledge_gap():
    evidence = _evidence(status="SECONDARY_ONLY")
    result = evaluate_hair_consultation(_request(evidence=(evidence,)))
    assert result.consultation_status == "NEEDS_INFORMATION_OR_TEST"
    assert result.reason_codes == ("KNOWLEDGE_GAP",)
    assert result.options == ()


def test_evidence_for_another_market_or_product_does_not_satisfy_gate():
    evidence = _evidence(market_region="EU")
    result = evaluate_hair_consultation(_request(evidence=(evidence,)))
    assert result.reason_codes == ("KNOWLEDGE_GAP",)
    assert result.options == ()


def test_rule_must_be_active_and_bound_to_specialist_review():
    rule = _rule(status="REVIEWED")
    result = evaluate_hair_consultation(_request(rules=(rule,)))
    assert result.reason_codes == ("KNOWLEDGE_GAP",)
    assert result.options == ()


def test_rule_without_specialist_review_reference_fails_closed():
    rule = _rule(specialist_review_ref="")
    result = evaluate_hair_consultation(_request(rules=(rule,)))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


def test_invalid_evidence_digest_fails_closed():
    evidence = _evidence(content_sha256="not-a-digest")
    result = evaluate_hair_consultation(_request(evidence=(evidence,)))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


@pytest.mark.parametrize(
    ("cause", "status", "reason"),
    [
        ("NEEDS_INFORMATION", "NEEDS_INFORMATION_OR_TEST", "KNOWLEDGE_GAP"),
        ("NEEDS_IN_PERSON_REVIEW", "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW", "DATA_GAP"),
        ("NOT_FEASIBLE_REQUIRES_SPECIALIST", "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW", "DATA_GAP"),
        ("SAFETY_CONCERN", "SAFETY_STOP_NO_EXECUTION_SUGGESTION", "SAFETY_CONCERN"),
        ("OUT_OF_SCOPE", "OUT_OF_V1_SCOPE", "OUT_OF_SCOPE"),
    ],
)
def test_no_option_scenario_maps_by_actual_cause(cause, status, reason):
    result = evaluate_hair_consultation(
        _request(candidates=(), no_option_cause=cause)
    )
    assert result.consultation_status == status
    assert result.reason_codes == (reason,)
    assert result.options == ()


def test_no_candidate_without_explicit_reason_is_engine_failure():
    result = evaluate_hair_consultation(_request(candidates=(), no_option_cause=None))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


def test_candidate_and_no_option_cause_cannot_coexist():
    result = evaluate_hair_consultation(_request(no_option_cause="NEEDS_INFORMATION"))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.options == ()


def test_candidate_rank_must_be_sequential_and_unique():
    result = evaluate_hair_consultation(_request(candidates=(_candidate(rank=2),)))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


def test_candidate_must_reference_only_verified_evidence_and_active_rules():
    candidate = _candidate(evidence_refs=("SYNTHETIC-UNVERIFIED-EVIDENCE",))
    result = evaluate_hair_consultation(_request(candidates=(candidate,)))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.reason_codes == ("ENGINE_FAIL",)


def test_more_than_three_candidates_is_engine_failure():
    candidates = tuple(
        _candidate(
            option_ref=f"SYNTHETIC-OPTION-{index}",
            rank=index,
        )
        for index in range(1, 5)
    )
    result = evaluate_hair_consultation(_request(candidates=candidates))
    assert result.run_outcome == "ENGINE_FAILURE"
    assert result.options == ()


def test_question_or_acceptance_state_is_not_part_of_engine_output():
    result = evaluate_hair_consultation(_request())
    assert not hasattr(result, "client_decision")
    assert not hasattr(result, "execution_consent")
    assert not hasattr(result, "workflow_state")
