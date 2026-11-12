"""Integration tests: all synthetic scenarios traverse HairColorAdapter.

These are boundary/injection tests only. S11/S12/S14 deliberately assert
non-ownership; they do not implement decision-ledger or workflow semantics.
"""
from copy import deepcopy

import pytest

from app.hair_color.adapter import (
    AdapterContractError,
    EngineExecutionFailure,
    HairColorAdapter,
)
from tests.support.hair_color_synthetic_engine import SyntheticHairColorEngine


def make_request(scenario_id, **overrides):
    value = {
        "contract_version": "0.2-draft",
        "request_id": f"REQ-{scenario_id}",
        "operation": "EVALUATE_CASE",
        "case_ref": f"CASE-{scenario_id}",
        "case_version": 3,
        "target_version": 2,
        "case_context": {"synthetic_scenario_id": scenario_id},
        "evidence_context": [{"evidence_ref": "EVIDENCE-MOCK-A"}],
        "policy_context": {"chemical_execution_instructions": "PROHIBITED"},
    }
    value.update(overrides)
    return value


@pytest.mark.parametrize(
    ("scenario_id", "expected_options", "expected_reason"),
    [
        ("S01", 1, None),
        ("S02", 0, "DATA_GAP"),
        ("S03", 0, "CONFLICTING_DATA"),
        ("S04", 0, "DATA_GAP"),
        ("S05", 0, "DATA_GAP"),
        ("S06", 0, "KNOWLEDGE_GAP"),
        ("S07", 0, "SAFETY_CONCERN"),
        ("S08", 0, None),
        ("S09", 2, None),
        ("S10", 1, None),
        ("S11", 0, None),
        ("S12", 0, None),
        ("S13", 1, None),
        ("S14", 0, None),
    ],
)
def test_s01_to_s14_synthetic_scenarios_pass_through_adapter(
    scenario_id, expected_options, expected_reason
):
    adapter = HairColorAdapter(SyntheticHairColorEngine())
    result = adapter.evaluate(make_request(scenario_id))

    assert len(result["options"]) == expected_options
    if expected_reason is not None:
        assert result["reason_codes"] == [expected_reason]
    assert result["request_id"] == f"REQ-{scenario_id}"
    assert "Synthetic fixture" in result["summary"] or scenario_id in {"S11", "S12", "S13", "S14"}


def test_s11_question_operation_does_not_change_client_decision_snapshot():
    snapshot = {
        "acceptance": "PENDING",
        "execution_consent": "NOT_GRANTED",
    }
    request = make_request(
        "S11",
        operation="ANSWER_QUESTION",
        question="Why is this only a synthetic candidate?",
        case_context={
            "synthetic_scenario_id": "S11",
            "client_decision_snapshot": snapshot,
        },
    )
    before = deepcopy(request)

    result = HairColorAdapter(SyntheticHairColorEngine()).evaluate(request)

    assert request == before
    assert result["options"] == []
    assert "acceptance" not in result
    assert "execution_consent" not in result


def test_s12_rejection_ledger_remains_outside_adapter_and_request_is_unchanged():
    request = make_request(
        "S12",
        case_context={
            "synthetic_scenario_id": "S12",
            "rejected_suggestion_ref": "SUGGESTION-SYN-OLD",
            "active_suggestion_refs": [],
        },
    )
    before = deepcopy(request)

    result = HairColorAdapter(SyntheticHairColorEngine()).evaluate(request)

    assert request == before
    assert result["options"] == []
    assert "rejection" not in result
    assert "decision_events" not in result


def test_s14_resume_check_is_rejected_and_fresh_reevaluation_is_allowed():
    adapter = HairColorAdapter(SyntheticHairColorEngine())

    with pytest.raises(AdapterContractError, match="unsupported operation"):
        adapter.evaluate(make_request("S14", operation="RESUME_CHECK"))

    fresh = adapter.evaluate(make_request("S14", operation="REEVALUATE"))
    assert fresh["options"] == []
    assert "no resume" in fresh["summary"]


def test_s15_synthetic_engine_failure_returns_no_consultation_result():
    adapter = HairColorAdapter(SyntheticHairColorEngine())

    with pytest.raises(EngineExecutionFailure) as caught:
        adapter.evaluate(make_request("S15"))

    assert caught.value.reason_code == "ENGINE_FAIL"


def test_unknown_synthetic_scenario_fails_closed():
    adapter = HairColorAdapter(SyntheticHairColorEngine())

    with pytest.raises(EngineExecutionFailure):
        adapter.evaluate(make_request("S99"))
