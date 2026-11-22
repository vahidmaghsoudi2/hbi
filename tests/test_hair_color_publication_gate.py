import pytest

from app.hair_color.publication_gate import evaluate_publication_gate


def triage_response(**overrides):
    result = {
        "request_id": "REQ-SYN-GATE",
        "case_ref": "CASE-SYN-GATE",
        "evaluated_case_version": 1,
        "evaluated_target_version": 1,
        "engine_state": "STOP_OR_REFER_WITH_REASON",
        "consultation_status": "NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW",
        "reason_codes": ["KNOWLEDGE_GAP"],
        "summary": "Synthetic referral only.",
        "options": [],
        "missing_information": [],
        "evidence_refs": [],
        "limitations": ["Synthetic test"],
        "next_step": {"action": "SPECIALIST_REVIEW"},
    }
    result.update(overrides)
    return result


def test_gate_allows_only_current_safe_triage_response():
    gate = evaluate_publication_gate(triage_response(), current_case_version=1, current_target_version=1)
    assert gate["publication_allowed"] is True
    assert gate["publication_kind"] == "TRIAGE_ONLY"
    assert gate["options"] == []
    assert gate["execution_authorized"] is False


@pytest.mark.parametrize("status", ["SYSTEM_REASONED_SUGGESTION", "UNRECOGNIZED"])
def test_gate_blocks_advice_and_unknown_status(status):
    response = triage_response(consultation_status=status, engine_state="SUGGESTION_REVIEWABLE")
    gate = evaluate_publication_gate(response, current_case_version=1, current_target_version=1)
    assert gate["publication_allowed"] is False
    assert gate["publication_kind"] == "BLOCKED"
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False


def test_gate_blocks_any_candidate_even_if_status_is_triage():
    gate = evaluate_publication_gate(triage_response(options=[{"synthetic": True}]), current_case_version=1, current_target_version=1)
    assert gate["publication_allowed"] is False
    assert "CANDIDATE_OUTPUT_DISABLED" in gate["reason_codes"]
    assert gate["safe_response"]["options"] == []


def test_gate_blocks_stale_case_or_target_snapshot():
    stale = evaluate_publication_gate(triage_response(), current_case_version=2, current_target_version=1)
    assert stale["publication_allowed"] is False
    assert "STALE_CASE_VERSION" in stale["reason_codes"]
    stale_target = evaluate_publication_gate(triage_response(), current_case_version=1, current_target_version=2)
    assert stale_target["publication_allowed"] is False
    assert "STALE_TARGET_VERSION" in stale_target["reason_codes"]


def test_gate_fails_closed_for_empty_or_unknown_reason_codes():
    empty = evaluate_publication_gate(triage_response(reason_codes=[]), current_case_version=1, current_target_version=1)
    unknown = evaluate_publication_gate(triage_response(reason_codes=["UNRECOGNIZED"]), current_case_version=1, current_target_version=1)
    assert not empty["publication_allowed"] and not unknown["publication_allowed"]
