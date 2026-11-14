"""Runtime conformance for the ten already-approved Hair dialogue scenarios.

All fixtures are synthetic. These tests validate dialogue invariants only;
they do not test or enable chemical advice, real-client data, persistence,
service execution, or customer-visible recommendation publication.
"""
import pytest

from app.domain.hair_dialogue_contract import (
    AdviceGate,
    ClientDecision,
    DialogueCaseState,
    accept_proposal,
    answer_question,
    apply_dependency_reassessment,
    attach_proposal,
    change_goal,
    evaluate_advice_gate,
    explain_reason,
    record_execution_consent,
    reject_proposal,
    resolve_required_data,
)


def _state():
    return DialogueCaseState(
        case_id="SYNTHETIC-DIALOGUE-REFERENCE-001",
        case_version="case-v1",
        goal_version="goal-v1",
    )


def _active_state():
    return attach_proposal(_state(), "SYNTHETIC-PROPOSAL-001")


def test_scenario_01_sequential_questions_preserve_case_versions_and_decisions():
    state = _active_state()
    first = answer_question(state, question="سؤال اول", answer="پاسخ اول")
    second = answer_question(first.state, question="سؤال دوم", answer="پاسخ دوم")

    assert first.state is state
    assert second.state is state
    assert first.decision_changed is False
    assert second.decision_changed is False
    assert second.state.case_version == "case-v1"
    assert second.state.goal_version == "goal-v1"
    assert second.state.client_decision == ClientDecision.NONE
    assert second.state.execution_consent_for_proposal_id is None


def test_scenario_02_reason_explanation_returns_only_client_safe_summary():
    safe_summary = "این نتیجه فقط به دلیل کافی‌بودن داده‌های کاتالوگی ارائه شده است."
    assert explain_reason(safe_summary) == safe_summary
    with pytest.raises(ValueError):
        explain_reason(" ")


def test_scenario_03_use_recorded_data_and_name_exact_missing_fields():
    result = resolve_required_data(
        {"brand": "Synthetic Brand", "shade_number": "1", "history": ""},
        ("brand", "shade_number", "history", "hair_history"),
    )

    assert result.known_values == (
        ("brand", "Synthetic Brand"),
        ("shade_number", "1"),
    )
    assert result.missing_fields == ("history", "hair_history")
    assert result.complete is False


def test_scenario_04_insufficient_required_data_withholds_definitive_advice():
    gate = evaluate_advice_gate(
        data_complete=False,
        safety_passed=True,
        rule_valid=True,
        evidence_valid=True,
    )
    assert gate == AdviceGate(False, ("DATA_GAP",))


def test_scenario_05_changed_goal_creates_new_version_and_clears_dependent_proposal():
    accepted = accept_proposal(_active_state(), "SYNTHETIC-PROPOSAL-001")
    changed = change_goal(accepted, "goal-v2")

    assert changed.goal_version == "goal-v2"
    assert changed.active_proposal_id is None
    assert changed.active_proposal_goal_version is None
    assert changed.client_decision == ClientDecision.NONE
    assert changed.execution_consent_for_proposal_id is None


def test_scenario_06_rejected_proposal_is_terminal_and_cannot_be_reactivated():
    rejected = reject_proposal(_active_state(), "SYNTHETIC-PROPOSAL-001")

    assert rejected.client_decision == ClientDecision.REJECTED
    assert rejected.active_proposal_id is None
    assert rejected.rejected_proposal_ids == ("SYNTHETIC-PROPOSAL-001",)
    with pytest.raises(ValueError, match="cannot be reactivated"):
        attach_proposal(rejected, "SYNTHETIC-PROPOSAL-001")
    alternative = attach_proposal(rejected, "SYNTHETIC-PROPOSAL-002")
    assert alternative.active_proposal_id == "SYNTHETIC-PROPOSAL-002"


def test_scenario_07_acceptance_does_not_create_execution_consent():
    accepted = accept_proposal(_active_state(), "SYNTHETIC-PROPOSAL-001")

    assert accepted.client_decision == ClientDecision.ACCEPTED
    assert accepted.execution_consent_for_proposal_id is None
    with pytest.raises(ValueError):
        record_execution_consent(
            accepted,
            "SYNTHETIC-PROPOSAL-001",
            explicit_consent=False,
        )
    consented = record_execution_consent(
        accepted,
        "SYNTHETIC-PROPOSAL-001",
        explicit_consent=True,
    )
    assert consented.execution_consent_for_proposal_id == "SYNTHETIC-PROPOSAL-001"


def test_scenario_08_predecision_question_does_not_force_acceptance_or_rejection():
    state = _active_state()
    reply = answer_question(
        state,
        question="پیش از تصمیم، دلیل این وضعیت چیست؟",
        answer="این یک توضیح است و تصمیم مشتری ثبت نمی‌کند.",
    )

    assert reply.state is state
    assert reply.state.client_decision == ClientDecision.NONE
    assert reply.state.active_proposal_id == "SYNTHETIC-PROPOSAL-001"
    assert reply.state.execution_consent_for_proposal_id is None


def test_scenario_09_missing_evidence_is_explicit_knowledge_gap_not_a_guess():
    gate = evaluate_advice_gate(
        data_complete=True,
        safety_passed=True,
        rule_valid=True,
        evidence_valid=False,
    )
    assert gate.advice_allowed is False
    assert gate.reason_codes == ("KNOWLEDGE_GAP",)


def test_scenario_10_effective_or_unresolved_change_invalidates_dependent_decisions():
    accepted = record_execution_consent(
        accept_proposal(_active_state(), "SYNTHETIC-PROPOSAL-001"),
        "SYNTHETIC-PROPOSAL-001",
        explicit_consent=True,
    )

    preserved = apply_dependency_reassessment(accepted, "PRESERVE")
    assert preserved.status == "PRESERVED"
    assert preserved.state is accepted

    invalidated = apply_dependency_reassessment(accepted, "INVALIDATE")
    assert invalidated.status == "INVALIDATED"
    assert invalidated.state.active_proposal_id is None
    assert invalidated.state.client_decision == ClientDecision.NONE
    assert invalidated.state.execution_consent_for_proposal_id is None

    unresolved = apply_dependency_reassessment(accepted, "UNRESOLVED")
    assert unresolved.status == "REASSESSMENT_REQUIRED"
    assert unresolved.state.active_proposal_id is None
    assert unresolved.state.execution_consent_for_proposal_id is None


def test_dialogue_contract_rejects_non_synthetic_case_state():
    invalid = DialogueCaseState(
        case_id="REAL-CLIENT-001",
        case_version="case-v1",
        goal_version="goal-v1",
    )
    with pytest.raises(ValueError, match="synthetic"):
        answer_question(invalid, question="question", answer="answer")


def test_advice_gate_uses_fail_closed_priority():
    gate = evaluate_advice_gate(
        data_complete=False,
        safety_passed=False,
        rule_valid=False,
        evidence_valid=False,
        engine_ok=False,
    )
    assert gate.advice_allowed is False
    assert gate.reason_codes == ("ENGINE_FAIL",)



def test_dialogue_contract_rejects_wrong_state_type():
    with pytest.raises(TypeError):
        answer_question(object(), question="question", answer="answer")


def test_question_and_answer_must_both_be_non_empty():
    state = _state()
    with pytest.raises(ValueError):
        answer_question(state, question=" ", answer="answer")
    with pytest.raises(ValueError):
        answer_question(state, question="question", answer=" ")


def test_required_data_resolver_rejects_malformed_field_contracts():
    with pytest.raises(TypeError):
        resolve_required_data([], ())
    with pytest.raises(ValueError):
        resolve_required_data({}, ["brand"])
    with pytest.raises(ValueError):
        resolve_required_data({}, ("brand", "brand"))


def test_safety_gate_prevents_advice_even_when_other_gates_pass():
    gate = evaluate_advice_gate(
        data_complete=True,
        safety_passed=False,
        rule_valid=True,
        evidence_valid=True,
    )
    assert gate.advice_allowed is False
    assert gate.reason_codes == ("SAFETY_STOP",)


def test_only_synthetic_proposal_identifiers_can_be_attached():
    with pytest.raises(ValueError):
        attach_proposal(_state(), "PROPOSAL-REAL-001")


def test_acceptance_and_rejection_must_target_current_active_proposal():
    state = _active_state()
    with pytest.raises(ValueError):
        accept_proposal(state, "SYNTHETIC-OTHER-PROPOSAL")
    with pytest.raises(ValueError):
        reject_proposal(state, "SYNTHETIC-OTHER-PROPOSAL")


def test_goal_change_requires_a_distinct_non_empty_version():
    state = _state()
    with pytest.raises(ValueError):
        change_goal(state, " ")
    with pytest.raises(ValueError):
        change_goal(state, "goal-v1")


def test_unknown_dependency_status_fails_closed_and_clears_decisions():
    state = accept_proposal(_active_state(), "SYNTHETIC-PROPOSAL-001")
    result = apply_dependency_reassessment(state, "UNRECOGNIZED_IMPACT")
    assert result.status == "ENGINE_FAIL_CLOSED"
    assert result.state.active_proposal_id is None
    assert result.state.client_decision == ClientDecision.NONE
    assert result.state.execution_consent_for_proposal_id is None
