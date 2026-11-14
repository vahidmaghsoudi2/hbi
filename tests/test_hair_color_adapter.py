"""Synthetic-only tests for the isolated hair-colour adapter boundary.

These tests validate adapter transport/contract invariants. They do not claim
scientific validity or implement Orchestrator, Case Store, decision ledger,
Workflow Engine, or hair-colour chemistry.
"""
from copy import deepcopy

import pytest

from app.hair_color.adapter import (
    AdapterContractError,
    EngineExecutionFailure,
    HairColorAdapter,
)


def request(**overrides):
    value = {
        "contract_version": "0.2-draft",
        "request_id": "REQ-SYN-001",
        "operation": "EVALUATE_CASE",
        "case_ref": "CASE-SYN-001",
        "case_version": 3,
        "target_version": 2,
        "case_context": {"client_goal": {"value": "GOAL-A", "knowledge_state": "KNOWN"}},
        "evidence_context": [{"evidence_ref": "EVIDENCE-MOCK-A"}],
        "policy_context": {"chemical_execution_instructions": "PROHIBITED"},
    }
    value.update(overrides)
    return value


def response(**overrides):
    value = {
        "request_id": "REQ-SYN-001",
        "case_ref": "CASE-SYN-001",
        "evaluated_case_version": 3,
        "evaluated_target_version": 2,
        "engine_state": "SUGGESTION_REVIEWABLE",
        "consultation_status": "SYSTEM_REASONED_SUGGESTION",
        "reason_codes": [],
        "summary": "Synthetic response only; not a hair-colour recommendation.",
        "options": [{}],
        "missing_information": [],
        "evidence_refs": ["EVIDENCE-MOCK-A"],
        "limitations": ["Synthetic fixture; no scientific evidence."],
        "next_step": {},
    }
    value.update(overrides)
    return value


def run(request_value, response_value):
    return HairColorAdapter(lambda _request: response_value).evaluate(request_value)


def test_s01_valid_synthetic_request_passes_adapter_boundary():
    result = run(request(), response())
    assert result["engine_state"] == "SUGGESTION_REVIEWABLE"
    assert result["options"] == [{}]


def test_s02_data_gap_withholds_dependent_options():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["DATA_GAP"],
            options=[],
        ),
    )
    assert result["options"] == []
    assert result["reason_codes"] == ["DATA_GAP"]


def test_s03_conflicting_data_is_not_silently_resolved_or_published():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["CONFLICTING_DATA"],
            options=[],
        ),
    )
    assert result["reason_codes"] == ["CONFLICTING_DATA"]
    assert result["options"] == []


def test_s04_image_limited_case_cannot_publish_a_candidate_without_required_data():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["DATA_GAP"],
            options=[],
            limitations=["Image input is not used to infer hidden chemical history."],
        ),
    )
    assert result["options"] == []
    assert "Image input is not used to infer hidden chemical history." in result["limitations"]


def test_s05_unresolved_product_identity_blocks_product_dependent_option():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["DATA_GAP"],
            options=[],
            missing_information=[{"field": "product_identity"}],
        ),
    )
    assert result["options"] == []
    assert result["missing_information"] == [{"field": "product_identity"}]


def test_s06_knowledge_gap_is_distinct_and_withholds_options():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["KNOWLEDGE_GAP"],
            options=[],
        ),
    )
    assert result["reason_codes"] == ["KNOWLEDGE_GAP"]
    assert result["options"] == []


def test_s07_safety_stop_is_fail_closed():
    result = run(
        request(),
        response(
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION",
            reason_codes=["SAFETY_CONCERN"],
            options=[],
        ),
    )
    assert result["options"] == []
    assert result["consultation_status"] == "SAFETY_STOP_NO_EXECUTION_SUGGESTION"


def test_specialist_review_status_withholds_candidate_options():
    unsafe = response(
        engine_state="SUGGESTION_REVIEWABLE",
        consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        options=[{}],
    )
    with pytest.raises(AdapterContractError, match="blocked consultation"):
        run(request(), unsafe)


def test_s07_rejects_safety_stop_with_any_candidate_option():
    unsafe = response(
        engine_state="STOP_OR_REFER_WITH_REASON",
        consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION",
        reason_codes=["SAFETY_CONCERN"],
        options=[{}],
    )
    with pytest.raises(AdapterContractError, match="blocked consultation"):
        run(request(), unsafe)


def test_s08_no_valid_alternative_is_returned_as_an_empty_option_set():
    result = run(
        request(),
        response(
            engine_state="STOP_OR_REFER_WITH_REASON",
            consultation_status="NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
            options=[],
            summary="No valid option is supported under the synthetic constraints.",
        ),
    )
    assert result["options"] == []


def test_s09_adapter_accepts_two_candidate_objects_and_keeps_their_count():
    options = [{}, {}]
    result = run(request(), response(options=options))
    assert len(result["options"]) == 2


def test_s10_adapter_preserves_exactly_one_candidate_without_fabricating_more():
    only_option = [{}]
    result = run(request(), response(options=only_option))
    assert result["options"] == only_option


def test_s11_question_operation_does_not_mutate_authoritative_request_context():
    query = request(operation="ANSWER_QUESTION", question="Why is this candidate shown?")
    before = deepcopy(query)
    result = run(
        query,
        response(
            options=[],
            summary="Synthetic explanation only; no client decision is recorded.",
        ),
    )
    assert query == before
    assert "acceptance" not in result
    assert "execution_consent" not in result


def test_s12_rejection_and_suggestion_ledger_remain_outside_adapter_authority():
    # The Adapter receives a snapshot and returns a candidate result only. It
    # has no ledger/store dependency and must not mutate the supplied snapshot.
    snapshot = request()
    before = deepcopy(snapshot)
    run(snapshot, response(options=[]))
    assert snapshot == before


def test_s13_response_for_a_different_case_or_target_version_is_rejected():
    stale = response(evaluated_target_version=3)
    with pytest.raises(AdapterContractError, match="target version"):
        run(request(), stale)


def test_s14_resume_check_is_not_an_operation_but_fresh_reevaluation_is():
    with pytest.raises(AdapterContractError, match="unsupported operation"):
        run(request(operation="RESUME_CHECK"), response(options=[]))

    fresh = request(operation="REEVALUATE")
    assert run(fresh, response(options=[]))["request_id"] == fresh["request_id"]


def test_s15_engine_exception_returns_no_consultation_result():
    def broken_engine(_request):
        raise TimeoutError("synthetic retrieval failure")

    with pytest.raises(EngineExecutionFailure) as caught:
        HairColorAdapter(broken_engine).evaluate(request())
    assert caught.value.reason_code == "ENGINE_FAIL"


def test_engine_failure_cannot_be_misreported_as_successful_consultation():
    failed = response(reason_codes=["ENGINE_FAIL"], options=[])
    with pytest.raises(EngineExecutionFailure):
        run(request(), failed)


@pytest.mark.parametrize(
    "bad_request",
    [
        request(contract_version="99.0"),
        request(operation="RESUME_CHECK"),
        request(case_version=0),
        request(target_version=True),
        request(case_context=[]),
        request(evidence_context={}),
        request(policy_context=[]),
    ],
)
def test_invalid_request_fails_closed_before_engine_invocation(bad_request):
    invoked = False

    def engine(_request):
        nonlocal invoked
        invoked = True
        return response()

    with pytest.raises(AdapterContractError):
        HairColorAdapter(engine).evaluate(bad_request)
    assert invoked is False


def test_response_with_version_or_identity_mismatch_is_rejected():
    with pytest.raises(AdapterContractError, match="request_id"):
        run(request(), response(request_id="REQ-OTHER"))
    with pytest.raises(AdapterContractError, match="case_ref"):
        run(request(), response(case_ref="CASE-OTHER"))
    with pytest.raises(AdapterContractError, match="case version"):
        run(request(), response(evaluated_case_version=4))


def test_unknown_states_reason_codes_and_more_than_three_options_are_rejected():
    with pytest.raises(AdapterContractError, match="unknown engine_state"):
        run(request(), response(engine_state="MADE_UP_STATE"))
    with pytest.raises(AdapterContractError, match="unknown consultation_status"):
        run(request(), response(consultation_status="MADE_UP_STATUS"))
    with pytest.raises(AdapterContractError, match="unknown or malformed"):
        run(request(), response(reason_codes=["MADE_UP_REASON"]))
    with pytest.raises(AdapterContractError, match="more than three"):
        run(request(), response(options=[{}, {}, {}, {}]))


def test_chemical_execution_fields_are_rejected_recursively():
    unsafe = response(options=[{"candidate_key": "A", "oxidant_percentage": 6}])
    with pytest.raises(AdapterContractError, match="prohibited field"):
        run(request(), unsafe)



def test_candidate_requires_evidence_refs_bound_to_the_request_context():
    with pytest.raises(AdapterContractError, match="require traceable evidence"):
        run(request(), response(evidence_refs=[]))
    with pytest.raises(AdapterContractError, match="absent from the request context"):
        run(request(), response(evidence_refs=["EVIDENCE-NOT-SUPPLIED"]))


def test_engine_cannot_emit_chemical_execution_instruction_payload():
    unsafe = response(chemical_execution_instructions="synthetic instruction")
    with pytest.raises(AdapterContractError, match="prohibited field"):
        run(request(), unsafe)

def test_adapter_does_not_mutate_or_expose_engine_owned_mutable_objects():
    engine_output = response()
    result = run(request(), engine_output)
    result["options"].clear()
    assert len(engine_output["options"]) == 1

def test_duplicate_reason_codes_and_evidence_refs_are_rejected():
    with pytest.raises(AdapterContractError, match="reason_codes must not contain duplicates"):
        run(request(), response(reason_codes=["DATA_GAP", "DATA_GAP"], options=[]))

    with pytest.raises(AdapterContractError, match="evidence_refs must not contain duplicates"):
        run(request(), response(evidence_refs=["EVIDENCE-MOCK-A", "EVIDENCE-MOCK-A"]))

