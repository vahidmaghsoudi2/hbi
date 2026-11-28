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


@pytest.mark.parametrize(
    "field,value",
    [
        ("consultation_status", ["NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW"]),
        ("engine_state", ["STOP_OR_REFER_WITH_REASON"]),
        ("reason_codes", [["KNOWLEDGE_GAP"]]),
    ],
)
def test_gate_blocks_malformed_unhashable_values_without_crashing(field, value):
    gate = evaluate_publication_gate(
        triage_response(**{field: value}), current_case_version=1, current_target_version=1
    )
    assert gate["publication_allowed"] is False
    assert gate["publication_kind"] == "BLOCKED"
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False


def test_gate_rejects_status_reason_mismatch_and_gap_without_details():
    mismatch = evaluate_publication_gate(
        triage_response(consultation_status="SAFETY_STOP_NO_EXECUTION_SUGGESTION"),
        current_case_version=1, current_target_version=1,
    )
    assert not mismatch["publication_allowed"]
    assert "STATUS_REASON_MISMATCH" in mismatch["reason_codes"]

    gap = evaluate_publication_gate(
        triage_response(
            consultation_status="NEEDS_INFORMATION_OR_TEST",
            engine_state="NEEDS_MORE_INFORMATION",
            reason_codes=["DATA_GAP"],
            missing_information=[],
        ),
        current_case_version=1, current_target_version=1,
    )
    assert not gap["publication_allowed"]
    assert "DATA_GAP_WITHOUT_DETAILS" in gap["reason_codes"]


def test_gate_rejects_duplicate_reason_codes_and_invalid_version_types():
    duplicate = evaluate_publication_gate(
        triage_response(reason_codes=["KNOWLEDGE_GAP", "KNOWLEDGE_GAP"]),
        current_case_version=1, current_target_version=1,
    )
    assert not duplicate["publication_allowed"]
    assert "DUPLICATE_REASON_CODES" in duplicate["reason_codes"]

    invalid = evaluate_publication_gate(
        triage_response(evaluated_case_version=True),
        current_case_version=1, current_target_version=1,
    )
    assert not invalid["publication_allowed"]
    assert "INVALID_VERSION_FIELD" in invalid["reason_codes"]



@pytest.mark.parametrize(
    "field,value,expected_reason",
    [
        ("missing_information", "not-an-array", "INVALID_MISSING_INFORMATION"),
        ("missing_information", [None], "INVALID_MISSING_INFORMATION"),
        ("missing_information", [{"field": "hair_history"}], "INVALID_MISSING_INFORMATION"),
        ("evidence_refs", "not-an-array", "INVALID_EVIDENCE_REFS"),
        ("evidence_refs", ["", "EV-1"], "INVALID_EVIDENCE_REFS"),
        ("evidence_refs", ["EV-1", "EV-1"], "DUPLICATE_EVIDENCE_REFS"),
        ("limitations", [], "INVALID_LIMITATIONS"),
        ("limitations", ["  "], "INVALID_LIMITATIONS"),
        ("next_step", None, "INVALID_NEXT_STEP"),
        ("next_step", {"action": ""}, "INVALID_NEXT_STEP"),
        ("next_step", {"action": "SPECIALIST_REVIEW", "reason": []}, "INVALID_NEXT_STEP"),
    ],
)
def test_gate_blocks_malformed_publication_structure(field, value, expected_reason):
    gate = evaluate_publication_gate(
        triage_response(**{field: value}), current_case_version=1, current_target_version=1
    )
    assert gate["publication_allowed"] is False
    assert gate["publication_kind"] == "BLOCKED"
    assert expected_reason in gate["reason_codes"]
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False


@pytest.mark.parametrize("value", [True, 1.0, "1", 0, -1])
def test_gate_rejects_invalid_evaluated_versions_even_when_comparable(value):
    gate = evaluate_publication_gate(
        triage_response(evaluated_case_version=value),
        current_case_version=1,
        current_target_version=1,
    )
    assert gate["publication_allowed"] is False
    assert "INVALID_VERSION_FIELD" in gate["reason_codes"]
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False


@pytest.mark.parametrize("value", [True, 1.0, "1", 0, -1])
def test_gate_rejects_invalid_current_versions(value):
    gate = evaluate_publication_gate(
        triage_response(),
        current_case_version=value,
        current_target_version=1,
    )
    assert gate["publication_allowed"] is False
    assert "INVALID_CURRENT_VERSION" in gate["reason_codes"]
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False


@pytest.mark.parametrize(
    "response,current_case,current_target,expected_reason",
    [
        (triage_response(evaluated_case_version=2), 1, 1, "STALE_CASE_VERSION"),
        (triage_response(evaluated_target_version=2), 1, 1, "STALE_TARGET_VERSION"),
        (triage_response(evaluated_case_version=1), 2, 1, "STALE_CASE_VERSION"),
        (triage_response(evaluated_target_version=1), 1, 2, "STALE_TARGET_VERSION"),
    ],
)
def test_gate_rejects_mismatched_versions(response,current_case,current_target,expected_reason):
    gate = evaluate_publication_gate(
        response, current_case_version=current_case, current_target_version=current_target
    )
    assert gate["publication_allowed"] is False
    assert expected_reason in gate["reason_codes"]
    assert gate["safe_response"]["options"] == []
    assert gate["execution_authorized"] is False



def test_gate_accepts_policy_engine_missing_information_object_shape():
    response = triage_response(
        engine_state="NEEDS_MORE_INFORMATION",
        consultation_status="NEEDS_INFORMATION_OR_TEST",
        reason_codes=["DATA_GAP"],
        missing_information=[
            {"field": "current_hair_state", "reason": "Required intake field not supplied."}
        ],
        next_step={
            "action": "ASK_AND_CLARIFY",
            "missing_fields": ["current_hair_state"],
            "conflicting_fields": [],
        },
    )
    gate = evaluate_publication_gate(response, current_case_version=1, current_target_version=1)
    assert gate["publication_allowed"] is True
    assert gate["publication_kind"] == "TRIAGE_ONLY"
    assert gate["safe_response"]["missing_information"] == response["missing_information"]
    assert gate["execution_authorized"] is False
