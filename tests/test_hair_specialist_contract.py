import pytest

from app.domain.hair_specialist_contract import (
    EvidenceRef,
    GateStatus,
    MotorState,
    ResponseType,
    ReviewDecision,
    SpecialistOutput,
    evaluate_specialist_output,
    record_specialist_review,
    rejected_proposal_may_be_reactivated,
    revision_requires_new_proposal_id,
)


def _evidence(kind):
    return EvidenceRef(
        evidence_id=f"EV-{kind}",
        evidence_type=kind,
        source_reference=f"synthetic://evidence/{kind}",
        verification_status="VERIFIED",
        content_sha256="a" * 64,
        scope="synthetic-test-scope",
    )


def _output(**changes):
    values = {
        "case_id": "SYNTHETIC-ROW69-CONTRACT-001",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "run_id": "SYNTHETIC-RUN-001",
        "proposal_id": "SYNTHETIC-PROPOSAL-001",
        "response_type": ResponseType.REVIEWABLE_SUGGESTION,
        "motor_state": MotorState.REVIEWABLE_SUGGESTION,
        "data_complete": True,
        "evidence": (
            _evidence("PRODUCT_IDENTITY"),
            _evidence("PRODUCT_DOCUMENTATION"),
            _evidence("APPLICABLE_RULE_SOURCE"),
            _evidence("RULE_VALIDATION"),
        ),
    }
    values.update(changes)
    return SpecialistOutput(**values)


def _review(output, gate, **changes):
    values = {
        "reviewer_id": "synthetic-specialist-reviewer",
        "reviewer_role": "HAIR_DOMAIN_EXPERT",
        "professional_qualification_verified": True,
        "decision": ReviewDecision.APPROVE,
        "reason": "Synthetic contract test decision",
        "reviewed_case_version": output.case_version,
        "reviewed_goal_version": output.goal_version,
    }
    values.update(changes)
    return record_specialist_review(output, gate, **values)


def test_complete_evidence_opens_internal_review_only():
    gate = evaluate_specialist_output(_output())
    assert gate.status == GateStatus.READY_FOR_SPECIALIST_REVIEW
    assert gate.publishable_to_internal_review is True


def test_missing_required_data_is_data_gap_not_knowledge_gap():
    output = _output(
        data_complete=False,
        missing_data_fields=("hair_history",),
    )
    gate = evaluate_specialist_output(output)
    assert gate.status == GateStatus.DATA_GAP
    assert gate.publishable_to_internal_review is False


def test_missing_or_unverified_product_evidence_is_knowledge_gap():
    output = _output(evidence=(_evidence("PRODUCT_IDENTITY"),))
    gate = evaluate_specialist_output(output)
    assert gate.status == GateStatus.KNOWLEDGE_GAP
    assert set(gate.missing_evidence_types) == {
        "PRODUCT_DOCUMENTATION", "APPLICABLE_RULE_SOURCE", "RULE_VALIDATION"
    }


def test_invalid_hash_or_unverified_evidence_does_not_satisfy_gate():
    bad = EvidenceRef(
        evidence_id="EV-BAD",
        evidence_type="PRODUCT_IDENTITY",
        source_reference="synthetic://bad",
        verification_status="UNVERIFIED",
        content_sha256="not-a-sha",
        scope="synthetic-test-scope",
    )
    gate = evaluate_specialist_output(_output(evidence=(bad,)))
    assert gate.status == GateStatus.KNOWLEDGE_GAP


def test_engine_failure_is_fail_closed_and_takes_precedence():
    gate = evaluate_specialist_output(_output(data_complete=False), engine_ok=False)
    assert gate.status == GateStatus.ENGINE_FAIL
    assert gate.publishable_to_internal_review is False


def test_non_synthetic_case_is_blocked_even_with_synthetic_data_flag():
    gate = evaluate_specialist_output(_output(case_id="CASE-REAL-001"))
    assert gate.status == GateStatus.ENGINE_FAIL


def test_conditional_suggestion_is_motor_state_not_sixth_response_type():
    output = _output(motor_state=MotorState.CONDITIONAL_SUGGESTION)
    assert output.response_type == ResponseType.REVIEWABLE_SUGGESTION
    assert evaluate_specialist_output(output).status == GateStatus.READY_FOR_SPECIALIST_REVIEW


def test_safety_stop_and_out_of_scope_never_open_review_gate():
    safety = _output(
        response_type=ResponseType.SAFETY_STOP,
        motor_state=MotorState.STOP_OR_REFER,
        reason_code="SYNTHETIC_SAFETY_BLOCK",
    )
    out_scope = _output(
        response_type=ResponseType.OUT_OF_SCOPE,
        motor_state=MotorState.STOP_OR_REFER,
        reason_code="SYNTHETIC_OUT_OF_SCOPE",
    )
    assert evaluate_specialist_output(safety).status == GateStatus.SAFETY_STOP
    assert evaluate_specialist_output(out_scope).status == GateStatus.OUT_OF_SCOPE


def test_technical_qa_role_cannot_record_professional_specialist_review():
    output = _output()
    gate = evaluate_specialist_output(output)
    with pytest.raises(PermissionError):
        _review(output, gate, reviewer_role="Reviewer/QA", professional_qualification_verified=False)


def test_review_is_bound_to_exact_case_and_goal_versions():
    output = _output()
    gate = evaluate_specialist_output(output)
    with pytest.raises(ValueError):
        _review(output, gate, reviewed_goal_version="goal-v2")


def test_review_does_not_create_client_acceptance_consent_or_persistence():
    output = _output()
    review = _review(output, evaluate_specialist_output(output))
    assert review.client_acceptance is False
    assert review.execution_consent is False
    assert review.client_visible is False
    assert review.execution_authorized is False
    assert review.persisted is False


def test_rejected_proposal_cannot_be_reactivated():
    output = _output()
    rejected = _review(
        output,
        evaluate_specialist_output(output),
        decision=ReviewDecision.REJECT,
        reason="Synthetic rejection reason",
    )
    assert rejected_proposal_may_be_reactivated(output.proposal_id, (rejected,)) is False
    assert rejected_proposal_may_be_reactivated("SYNTHETIC-NEW-PROPOSAL", (rejected,)) is True


def test_revision_request_requires_a_new_proposal_identifier():
    output = _output()
    revision = _review(
        output,
        evaluate_specialist_output(output),
        decision=ReviewDecision.REQUEST_REVISION,
    )
    assert revision_requires_new_proposal_id(revision, "SYNTHETIC-PROPOSAL-002") is True
    assert revision_requires_new_proposal_id(revision, "SYNTHETIC-PROPOSAL-001") is False
    with pytest.raises(ValueError):
        revision_requires_new_proposal_id(
            _review(output, evaluate_specialist_output(output)), "SYNTHETIC-PROPOSAL-002"
        )


def test_information_request_is_a_response_type_with_motor_request_state():
    output = _output(
        response_type=ResponseType.NEEDS_MORE_INFORMATION,
        motor_state=MotorState.REQUEST_MORE_INFORMATION,
        data_complete=False,
        missing_data_fields=("history",),
        evidence=(),
    )
    gate = evaluate_specialist_output(output)
    assert gate.status == GateStatus.DATA_GAP
    assert gate.publishable_to_internal_review is False



def test_in_person_review_is_not_misclassified_as_a_data_gap():
    output = _output(
        response_type=ResponseType.NEEDS_IN_PERSON_REVIEW,
        motor_state=MotorState.STOP_OR_REFER,
        reason_code="SYNTHETIC_IN_PERSON_ASSESSMENT_REQUIRED",
        data_complete=False,
        missing_data_fields=("in_person_assessment",),
        evidence=(),
    )
    assert evaluate_specialist_output(output).status == GateStatus.REQUIRES_IN_PERSON_REVIEW


def test_safety_stop_precedes_generic_data_gap():
    output = _output(
        response_type=ResponseType.SAFETY_STOP,
        motor_state=MotorState.STOP_OR_REFER,
        reason_code="SYNTHETIC_SAFETY_BLOCK",
        data_complete=False,
        missing_data_fields=("history",),
        evidence=(),
    )
    assert evaluate_specialist_output(output).status == GateStatus.SAFETY_STOP


def test_unknown_response_type_fails_closed():
    output = _output(response_type="UNRECOGNIZED_RESPONSE")
    gate = evaluate_specialist_output(output)
    assert gate.status == GateStatus.ENGINE_FAIL
    assert gate.publishable_to_internal_review is False



def test_unrecognized_review_decision_is_rejected():
    output = _output()
    with pytest.raises(ValueError):
        _review(output, evaluate_specialist_output(output), decision="APPROVE")



def test_non_contract_object_is_rejected():
    with pytest.raises(TypeError):
        evaluate_specialist_output({"case_id": "SYNTHETIC-001"})


@pytest.mark.parametrize("field", ["case_version", "goal_version", "run_id", "proposal_id"])
def test_missing_version_or_run_identifier_is_data_gap(field):
    gate = evaluate_specialist_output(_output(**{field: ""}))
    assert gate.status == GateStatus.DATA_GAP


def test_safety_stop_with_invalid_motor_contract_fails_closed():
    output = _output(
        response_type=ResponseType.SAFETY_STOP,
        motor_state=MotorState.REVIEWABLE_SUGGESTION,
        reason_code="SYNTHETIC_SAFETY_BLOCK",
    )
    assert evaluate_specialist_output(output).status == GateStatus.ENGINE_FAIL


def test_out_of_scope_with_invalid_motor_contract_fails_closed():
    output = _output(
        response_type=ResponseType.OUT_OF_SCOPE,
        motor_state=MotorState.REVIEWABLE_SUGGESTION,
        reason_code="SYNTHETIC_OUT_OF_SCOPE",
    )
    assert evaluate_specialist_output(output).status == GateStatus.ENGINE_FAIL


def test_in_person_review_without_reason_fails_closed():
    output = _output(
        response_type=ResponseType.NEEDS_IN_PERSON_REVIEW,
        motor_state=MotorState.STOP_OR_REFER,
        reason_code=None,
    )
    assert evaluate_specialist_output(output).status == GateStatus.ENGINE_FAIL


def test_information_request_without_declared_missing_fields_is_data_gap():
    output = _output(
        response_type=ResponseType.NEEDS_MORE_INFORMATION,
        motor_state=MotorState.REQUEST_MORE_INFORMATION,
        data_complete=False,
        missing_data_fields=(),
        evidence=(),
    )
    gate = evaluate_specialist_output(output)
    assert gate.status == GateStatus.DATA_GAP
    assert gate.reason_codes == ("REQUIRED_MISSING_DATA_FIELDS_NOT_DECLARED",)


def test_reviewable_response_with_stop_motor_state_fails_closed():
    output = _output(motor_state=MotorState.STOP_OR_REFER)
    assert evaluate_specialist_output(output).status == GateStatus.ENGINE_FAIL


def test_raw_recommendation_payload_is_never_accepted_by_contract():
    output = _output(recommendation_payload={"chemical_formula": "FORBIDDEN"})
    assert evaluate_specialist_output(output).status == GateStatus.ENGINE_FAIL


def test_ineligible_output_cannot_receive_specialist_review():
    output = _output()
    ineligible = evaluate_specialist_output(output, engine_ok=False)
    with pytest.raises(ValueError):
        _review(output, ineligible)


def test_missing_reviewer_identity_cannot_be_recorded():
    output = _output()
    gate = evaluate_specialist_output(output)
    with pytest.raises(ValueError):
        _review(output, gate, reviewer_id="")
