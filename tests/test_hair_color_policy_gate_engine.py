"""Tests for the production fail-closed Hair Color intake gate."""
from app.hair_color.adapter import HairColorAdapter
from app.hair_color.policy_gate_engine import PolicyGateEngine


def request(**overrides):
    value = {
        "contract_version": "0.3-draft",
        "request_id": "REQ-POLICY-SYN",
        "operation": "EVALUATE_CASE",
        "case_ref": "CASE-POLICY-SYN",
        "case_version": 1,
        "target_version": 1,
        "case_context": {},
        "evidence_context": [],
        "policy_context": {},
    }
    value.update(overrides)
    return value


def test_missing_intake_fields_routes_to_questions_without_candidates():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(case_context={"missing_fields": ["synthetic field A", "synthetic field B"]})
    )
    assert result["engine_state"] == "NEEDS_MORE_INFORMATION"
    assert result["reason_codes"] == ["DATA_GAP"]
    assert result["options"] == []
    assert len(result["missing_information"]) == 2


def test_conflicting_intake_routes_to_clarification():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(case_context={"conflicting_fields": ["synthetic field"]})
    )
    assert result["reason_codes"] == ["CONFLICTING_DATA"]
    assert result["options"] == []
    assert result["next_step"]["action"] == "CLARIFY_CONFLICTS"


def test_safety_flag_fail_closed():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(policy_context={"safety_concern": True})
    )
    assert result["consultation_status"] == "SAFETY_STOP_NO_EXECUTION_SUGGESTION"
    assert result["reason_codes"] == ["SAFETY_CONCERN"]
    assert result["options"] == []


def test_out_of_scope_request_stops():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(policy_context={"out_of_scope": True})
    )
    assert result["consultation_status"] == "OUT_OF_V1_SCOPE"
    assert result["reason_codes"] == ["OUT_OF_SCOPE"]
    assert result["options"] == []


def test_stale_case_snapshot_requires_fresh_evaluation():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(policy_context={"stale_snapshot": True})
    )
    assert result["reason_codes"] == ["STALE_CASE_VERSION"]
    assert result["options"] == []
    assert result["next_step"]["action"] == "FRESH_EVALUATION"


def test_answer_question_without_approved_evidence_is_knowledge_gap():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(operation="ANSWER_QUESTION", question="Synthetic question")
    )
    assert result["reason_codes"] == ["KNOWLEDGE_GAP"]
    assert result["options"] == []
    assert "cannot reliably answer" in result["summary"]


def test_complete_intake_still_does_not_unlock_unvalidated_domain_advice():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(request(case_context={"intake_complete": True}))
    assert result["reason_codes"] == ["KNOWLEDGE_GAP"]
    assert result["options"] == []
    assert "No color recommendation" in result["summary"]


def test_policy_gate_does_not_mutate_request():
    from copy import deepcopy
    value = request(case_context={"missing_fields": ["synthetic"]})
    before = deepcopy(value)
    HairColorAdapter(PolicyGateEngine()).evaluate(value)
    assert value == before

def test_public_consultation_entrypoint_is_callable_and_fails_closed():
    from app.hair_color.consultation import run_consultation

    result = run_consultation(request())
    assert result["options"] == []
    assert result["reason_codes"] == ["KNOWLEDGE_GAP"]
    assert result["engine_state"] == "STOP_OR_REFER_WITH_REASON"

def test_missing_and_conflicting_fields_are_reported_together():
    result = HairColorAdapter(PolicyGateEngine()).evaluate(
        request(case_context={
            "missing_fields": ["synthetic missing"],
            "conflicting_fields": ["synthetic conflict"],
        })
    )
    assert set(result["reason_codes"]) == {"DATA_GAP", "CONFLICTING_DATA"}
    assert len(result["missing_information"]) == 2
    assert result["options"] == []


def test_persian_public_callable_returns_raw_gate_and_ui_presentation():
    from app.hair_color.consultation import run_consultation_persian

    result = run_consultation_persian(request())
    assert result["consultation"]["options"] == []
    assert result["presentation"]["options"] == []
    assert result["execution_authorized"] is False
    assert result["presentation"]["execution_authorized"] is False
    assert "متخصص" in result["presentation"]["title"]
