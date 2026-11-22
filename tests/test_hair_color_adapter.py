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
        "contract_version": "0.3-draft",
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
    if value["operation"] == "ANSWER_QUESTION" and "question" not in value:
        value["question"] = "Synthetic-only question"
    return value


def candidate(rank=1, key=None, evidence_ref="EVIDENCE-MOCK-A"):
    key = key or f"CAND-SYN-{rank}"
    return {
        "candidate_key": key,
        "rank": rank,
        "summary": f"Synthetic candidate placeholder {rank}",
        "claims": [{
            "claim_ref": f"CLAIM-SYN-{rank}",
            "claim_text": "Synthetic placeholder claim; no domain assertion.",
            "rule_ref": f"RULE-SYN-{rank}",
            "evidence_refs": [evidence_ref],
            "support_status": "MOCK_SUPPORTED",
        }],
    }


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
        "options": [candidate()],
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
    assert result["options"] == [candidate()]


def test_s02_data_gap_withholds_dependent_options():
    result = run(
        request(),
        response(
            engine_state="NEEDS_MORE_INFORMATION",
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["DATA_GAP"],
            options=[],
            missing_information=["synthetic required field"],
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
            missing_information=["synthetic baseline data"],
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
        options=[candidate()],
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
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            reason_codes=["NO_VALID_OPTION"],
            options=[],
            summary="No valid option is supported under the synthetic constraints.",
        ),
    )
    assert result["options"] == []


def test_s09_adapter_accepts_two_candidate_objects_and_keeps_their_count():
    options = [candidate(1), candidate(2)]
    result = run(request(), response(options=options))
    assert len(result["options"]) == 2


def test_s10_adapter_preserves_exactly_one_candidate_without_fabricating_more():
    only_option = [candidate()]
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
        run(request(), response(options=[candidate(1), candidate(2), candidate(3), candidate(4)]))


def test_chemical_execution_fields_are_rejected_recursively():
    unsafe = response(options=[{**candidate(), "oxidant_percentage": 6}])
    with pytest.raises(AdapterContractError, match="prohibited field"):
        run(request(), unsafe)



def test_candidate_claim_evidence_must_be_in_response_level_evidence_refs():
    bad = candidate()
    bad["claims"][0]["evidence_refs"] = ["EVIDENCE-MOCK-A"]
    with pytest.raises(AdapterContractError, match="included in response evidence_refs"):
        run(request(), response(evidence_refs=[], options=[bad]))


def test_request_evidence_context_requires_unique_nonempty_reference_objects():
    for invalid in (
        [{"evidence_ref": "EVIDENCE-MOCK-A"}, {"evidence_ref": "EVIDENCE-MOCK-A"}],
        [{"evidence_ref": ""}],
        [None],
    ):
        with pytest.raises(AdapterContractError, match="evidence_context"):
            HairColorAdapter(lambda _request: response()).evaluate(request(evidence_context=invalid))


def test_data_gap_requires_explicit_missing_information():
    bad = response(engine_state="NEEDS_MORE_INFORMATION",
                   consultation_status="NEEDS_INFORMATION_OR_TEST",
                   reason_codes=["DATA_GAP"], options=[], missing_information=[])
    with pytest.raises(AdapterContractError, match="explicit missing_information"):
        run(request(), bad)


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



@pytest.mark.parametrize("bad_question", [None, "", "   "])
def test_answer_question_requires_nonblank_question_before_engine(bad_question):
    bad = request(operation="ANSWER_QUESTION", question=bad_question)
    with pytest.raises(AdapterContractError, match="question"):
        run(bad, response(options=[]))


@pytest.mark.parametrize("operation", ["EVALUATE_CASE", "REEVALUATE"])
def test_question_fields_are_rejected_on_non_question_operations(operation):
    bad = request(operation=operation, question="synthetic question")
    with pytest.raises(AdapterContractError, match="only for ANSWER_QUESTION"):
        run(bad, response(options=[]))


def test_question_about_requires_exact_suggestion_ref_and_positive_version():
    valid = request(operation="ANSWER_QUESTION", question_about={
        "suggestion_ref": "SUG-MOCK-01", "suggestion_version": 1,
    })
    assert run(valid, response(options=[]))["options"] == []
    invalid = request(operation="ANSWER_QUESTION", question_about={
        "suggestion_ref": "", "suggestion_version": 0,
    })
    with pytest.raises(AdapterContractError, match="question_about"):
        run(invalid, response(options=[]))


def test_state_reason_status_matrix_rejects_incompatible_pairs():
    with pytest.raises(AdapterContractError, match="compatibility"):
        run(request(), response(engine_state="SUGGESTION_REVIEWABLE",
                                consultation_status="NEEDS_INFORMATION_OR_TEST",
                                reason_codes=["DATA_GAP"], options=[]))
    with pytest.raises(AdapterContractError, match="compatibility"):
        run(request(), response(engine_state="STOP_OR_REFER_WITH_REASON",
                                consultation_status="OUT_OF_V1_SCOPE",
                                reason_codes=["KNOWLEDGE_GAP"], options=[]))


def test_s08_no_valid_option_reason_is_typed_and_requires_empty_options():
    valid = response(engine_state="STOP_OR_REFER_WITH_REASON",
                     consultation_status="NEEDS_INFORMATION_OR_TEST",
                     reason_codes=["NO_VALID_OPTION"], options=[])
    assert run(request(), valid)["reason_codes"] == ["NO_VALID_OPTION"]
    with pytest.raises(AdapterContractError, match="compatibility"):
        run(request(), {**valid, "options": [candidate()]})


def test_answer_question_missing_question_is_rejected():
    missing = request(operation="ANSWER_QUESTION")
    missing.pop("question")
    with pytest.raises(AdapterContractError, match="question"):
        run(missing, response(options=[]))


def test_question_about_is_rejected_on_non_question_operation():
    bad = request(operation="EVALUATE_CASE", question_about={
        "suggestion_ref": "SUG-MOCK-01", "suggestion_version": 1,
    })
    with pytest.raises(AdapterContractError, match="only for ANSWER_QUESTION"):
        run(bad, response())


@pytest.mark.parametrize(
    ("options", "error"),
    [
        ([candidate(1, key="DUP"), candidate(2, key="DUP")], "candidate_key values must be unique"),
        ([candidate(1), candidate(1, key="CAND-SYN-OTHER")], "candidate ranks must be unique, contiguous, and ordered"),
        ([candidate(2)], "candidate ranks must be unique, contiguous, and ordered"),
        ([{"candidate_key": "C", "rank": 1, "summary": "missing claims"}], "candidate missing required structural fields"),
        ([{**candidate(), "claims": []}], "candidate claims must be a non-empty array"),
        ([{**candidate(), "claims": [{**candidate()["claims"][0], "evidence_refs": ["EVIDENCE-ABSENT"]}]}], "candidate claim references evidence absent from request context"),
        ([{**candidate(), "extra_field": "not allowed"}], "candidate contains unexpected structural fields"),
        ([{**candidate(), "claims": [{**candidate()["claims"][0], "extra": "not allowed"}]}], "candidate claim contains unexpected structural fields"),
        ([{**candidate(), "claims": [{**candidate()["claims"][0], "support_status": "UNVERIFIED"}]}], "support_status must be MOCK_SUPPORTED"),
    ],
)
def test_candidate_structure_uniqueness_and_claim_evidence_are_fail_closed(options, error):
    with pytest.raises(AdapterContractError, match=error):
        run(request(), response(options=options))


def test_candidate_rank_sequence_must_match_ordered_options():
    options = [candidate(2), candidate(1)]
    with pytest.raises(AdapterContractError, match="ordered starting at 1"):
        run(request(), response(options=options))
