"""Integrated lifecycle transition matrix for the synthetic Hair dialogue runtime.

These tests exercise chained state transitions and invariant preservation only.
They do not claim replay protection: the HTTP runtime is stateless and does not
persist or serialize concurrent case updates.
"""
import pytest

from app.domain.hair_dialogue_contract import (
    ClientDecision,
    DialogueCaseState,
    accept_proposal,
    answer_question,
    apply_dependency_reassessment,
    attach_proposal,
    change_goal,
    record_execution_consent,
    reject_proposal,
    validate_dialogue_state,
)


def _empty_state():
    return DialogueCaseState(
        case_id="SYNTHETIC-RUNTIME-MATRIX-001",
        case_version="case-v1",
        goal_version="goal-v1",
    )


def _assert_valid(state):
    validate_dialogue_state(state)
    if state.active_proposal_id is None:
        assert state.active_proposal_case_version is None
        assert state.active_proposal_goal_version is None
        assert state.client_decision != ClientDecision.ACCEPTED
        assert state.execution_consent_for_proposal_id is None
    else:
        assert state.active_proposal_case_version == state.case_version
        assert state.active_proposal_goal_version == state.goal_version
    if state.execution_consent_for_proposal_id is not None:
        assert state.client_decision == ClientDecision.ACCEPTED
        assert state.execution_consent_for_proposal_id == state.active_proposal_id


def test_full_lifecycle_question_acceptance_consent_and_goal_change():
    state = attach_proposal(_empty_state(), "SYNTHETIC-PROPOSAL-MATRIX-1")
    _assert_valid(state)

    accepted = accept_proposal(state, "SYNTHETIC-PROPOSAL-MATRIX-1")
    _assert_valid(accepted)
    assert accepted.client_decision == ClientDecision.ACCEPTED
    assert accepted.execution_consent_for_proposal_id is None

    consented = record_execution_consent(
        accepted, "SYNTHETIC-PROPOSAL-MATRIX-1", explicit_consent=True
    )
    _assert_valid(consented)

    reply = answer_question(
        consented,
        question="سؤال مصنوعی درباره وضعیت",
        answer="پاسخ اطلاعاتی مصنوعی",
    )
    assert reply.state is consented
    assert reply.decision_changed is False
    _assert_valid(reply.state)

    changed = change_goal(reply.state, "goal-v2")
    _assert_valid(changed)
    assert changed.goal_version == "goal-v2"
    assert changed.active_proposal_id is None
    assert changed.client_decision == ClientDecision.NONE
    assert changed.execution_consent_for_proposal_id is None


def test_rejection_is_terminal_across_later_proposals_and_goal_versions():
    rejected = reject_proposal(
        attach_proposal(_empty_state(), "SYNTHETIC-PROPOSAL-REJECTED-1"),
        "SYNTHETIC-PROPOSAL-REJECTED-1",
    )
    _assert_valid(rejected)
    assert rejected.rejected_proposal_ids == ("SYNTHETIC-PROPOSAL-REJECTED-1",)

    with pytest.raises(ValueError, match="cannot be reactivated"):
        attach_proposal(rejected, "SYNTHETIC-PROPOSAL-REJECTED-1")

    alternative = attach_proposal(rejected, "SYNTHETIC-PROPOSAL-ALTERNATIVE-1")
    _assert_valid(alternative)
    changed = change_goal(alternative, "goal-v2")
    _assert_valid(changed)
    assert changed.rejected_proposal_ids == ("SYNTHETIC-PROPOSAL-REJECTED-1",)

    with pytest.raises(ValueError, match="cannot be reactivated"):
        attach_proposal(changed, "SYNTHETIC-PROPOSAL-REJECTED-1")


@pytest.mark.parametrize(
    ("outcome", "expected_status"),
    [
        ("INVALIDATE", "INVALIDATED"),
        ("UNRESOLVED", "REASSESSMENT_REQUIRED"),
        ("PRESERVE", "ENGINE_FAIL_CLOSED"),
        ("UNRECOGNIZED", "ENGINE_FAIL_CLOSED"),
        (None, "ENGINE_FAIL_CLOSED"),
    ],
)
def test_reassessment_outcomes_never_retain_prior_acceptance_or_consent(
    outcome, expected_status
):
    state = record_execution_consent(
        accept_proposal(
            attach_proposal(_empty_state(), "SYNTHETIC-PROPOSAL-REASSESS-1"),
            "SYNTHETIC-PROPOSAL-REASSESS-1",
        ),
        "SYNTHETIC-PROPOSAL-REASSESS-1",
        explicit_consent=True,
    )
    result = apply_dependency_reassessment(state, outcome)
    _assert_valid(result.state)
    assert result.status == expected_status
    assert result.state.active_proposal_id is None
    assert result.state.client_decision == ClientDecision.NONE
    assert result.state.execution_consent_for_proposal_id is None


def test_each_chained_transition_returns_a_valid_immutable_state():
    state = _empty_state()
    transitions = [
        lambda s: attach_proposal(s, "SYNTHETIC-PROPOSAL-CHAIN-1"),
        lambda s: accept_proposal(s, "SYNTHETIC-PROPOSAL-CHAIN-1"),
        lambda s: record_execution_consent(
            s, "SYNTHETIC-PROPOSAL-CHAIN-1", explicit_consent=True
        ),
        lambda s: apply_dependency_reassessment(s, "UNRESOLVED").state,
        lambda s: attach_proposal(s, "SYNTHETIC-PROPOSAL-CHAIN-2"),
        lambda s: reject_proposal(s, "SYNTHETIC-PROPOSAL-CHAIN-2"),
        lambda s: attach_proposal(s, "SYNTHETIC-PROPOSAL-CHAIN-3"),
        lambda s: change_goal(s, "goal-v2"),
    ]
    snapshots = []
    for transition in transitions:
        previous = state
        state = transition(state)
        _assert_valid(state)
        snapshots.append(previous)

    # Frozen dataclasses prevent a later transition from mutating an earlier snapshot.
    assert snapshots[0].active_proposal_id is None
    assert snapshots[1].client_decision == ClientDecision.NONE
    assert snapshots[2].client_decision == ClientDecision.ACCEPTED
    assert snapshots[2].execution_consent_for_proposal_id is None
    assert snapshots[3].execution_consent_for_proposal_id == "SYNTHETIC-PROPOSAL-CHAIN-1"
