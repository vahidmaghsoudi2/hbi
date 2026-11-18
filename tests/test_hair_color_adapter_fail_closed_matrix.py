"""Synthetic-only fail-closed matrix for the Hair Color Adapter boundary.

The matrix exercises existing contract invariants; it does not add domain
rules, chemistry, persistence, customer-data handling, or production semantics.
"""
from copy import deepcopy

import pytest

from app.hair_color.adapter import AdapterContractError, HairColorAdapter


def make_request(**overrides):
    value = {
        "contract_version": "0.2-draft",
        "request_id": "REQ-SYN-MATRIX-01",
        "operation": "EVALUATE_CASE",
        "case_ref": "CASE-SYN-MATRIX-01",
        "case_version": 1,
        "target_version": 1,
        "case_context": {"synthetic_case": True},
        "evidence_context": [{"evidence_ref": "EVIDENCE-SYN-01"}],
        "policy_context": {"scope": "SYNTHETIC_ONLY"},
    }
    value.update(overrides)
    return value


def make_response(**overrides):
    value = {
        "request_id": "REQ-SYN-MATRIX-01",
        "case_ref": "CASE-SYN-MATRIX-01",
        "evaluated_case_version": 1,
        "evaluated_target_version": 1,
        "engine_state": "SUGGESTION_REVIEWABLE",
        "consultation_status": "SYSTEM_REASONED_SUGGESTION",
        "reason_codes": [],
        "summary": "Synthetic contract fixture; not a recommendation.",
        "options": [{"candidate_ref": "CANDIDATE-SYN-01"}],
        "missing_information": [],
        "evidence_refs": ["EVIDENCE-SYN-01"],
        "limitations": ["No product chemistry or result prediction."],
        "next_step": {},
    }
    value.update(overrides)
    return value


def evaluate(request=None, response=None):
    return HairColorAdapter(lambda _request: response).evaluate(request or make_request())


@pytest.mark.parametrize(
    "consultation_status",
    [
        "NEEDS_INFORMATION_OR_TEST",
        "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        "SAFETY_STOP_NO_EXECUTION_SUGGESTION",
        "OUT_OF_V1_SCOPE",
    ],
)
def test_every_non_suggestion_consultation_status_blocks_candidates(consultation_status):
    with pytest.raises(AdapterContractError, match="blocked consultation"):
        evaluate(response=make_response(consultation_status=consultation_status))


@pytest.mark.parametrize(
    "engine_state",
    ["NEEDS_MORE_INFORMATION", "STOP_OR_REFER_WITH_REASON"],
)
def test_non_reviewable_engine_states_block_candidates(engine_state):
    with pytest.raises(AdapterContractError, match="blocked consultation"):
        evaluate(response=make_response(engine_state=engine_state))


@pytest.mark.parametrize(
    "reason_code",
    [
        "DATA_GAP",
        "KNOWLEDGE_GAP",
        "CONFLICTING_DATA",
        "SAFETY_CONCERN",
        "OUT_OF_SCOPE",
        "STALE_CASE_VERSION",
    ],
)
def test_each_blocking_reason_code_independently_blocks_candidates(reason_code):
    with pytest.raises(AdapterContractError, match="blocked consultation"):
        evaluate(response=make_response(reason_codes=[reason_code]))


def test_conditional_suggestion_remains_a_motor_state_not_a_new_response_label():
    result = evaluate(response=make_response(engine_state="CONDITIONAL_SUGGESTION"))
    assert result["engine_state"] == "CONDITIONAL_SUGGESTION"
    assert result["consultation_status"] == "SYSTEM_REASONED_SUGGESTION"


@pytest.mark.parametrize(
    "nested_payload",
    [
        {"history": [{"formula": "synthetic"}]},
        {"nested": {"oxidant_percentage": 6}},
        {"steps": [{"processing_time": 20}]},
    ],
)
def test_nested_chemical_execution_fields_are_rejected_before_engine_call(nested_payload):
    invoked = False

    def engine(_request):
        nonlocal invoked
        invoked = True
        return make_response()

    request = make_request(case_context=nested_payload)
    with pytest.raises(AdapterContractError, match="prohibited field"):
        HairColorAdapter(engine).evaluate(request)
    assert invoked is False


@pytest.mark.parametrize(
    "bad_response",
    [
        {"summary": " "},
        {"options": "not-an-array"},
        {"missing_information": {}},
        {"evidence_refs": [" "]},
        {"next_step": []},
        {"options": [None]},
    ],
)
def test_malformed_response_shapes_fail_closed(bad_response):
    response = make_response()
    response.update(bad_response)
    with pytest.raises(AdapterContractError):
        evaluate(response=response)


def test_response_cannot_claim_an_evidence_ref_not_supplied_in_request():
    with pytest.raises(AdapterContractError, match="absent from the request context"):
        evaluate(response=make_response(evidence_refs=["EVIDENCE-SYN-UNKNOWN"]))


def test_response_cannot_smuggle_client_or_workflow_decisions_in_nested_payload():
    unsafe = make_response(options=[{"metadata": {"execution_consent": "GRANTED"}}])
    with pytest.raises(AdapterContractError, match="prohibited field"):
        evaluate(response=unsafe)


def test_request_and_engine_response_are_isolated_from_mutation():
    request = make_request()
    response = make_response()
    request_before = deepcopy(request)
    response_before = deepcopy(response)

    result = evaluate(request=request, response=response)
    result["options"].clear()

    assert request == request_before
    assert response == response_before
    assert len(response["options"]) == 1


def test_engine_failure_reason_is_not_accepted_as_a_normal_response():
    from app.hair_color.adapter import EngineExecutionFailure

    with pytest.raises(EngineExecutionFailure):
        evaluate(response=make_response(reason_codes=["ENGINE_FAIL"], options=[]))
