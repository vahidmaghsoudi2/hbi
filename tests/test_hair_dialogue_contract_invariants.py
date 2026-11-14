"""Pure-domain invariant tests for the synthetic hair-dialogue contract.

These tests isolate the immutable state machine from HTTP/authentication concerns.
They use synthetic identifiers only and cannot produce recommendations or
authorize customer-facing service execution.
"""
import pytest

from app.domain.hair_dialogue_contract import (
    ClientDecision,
    DialogueCaseState,
    accept_proposal,
    apply_dependency_reassessment,
    attach_proposal,
    change_goal,
    record_execution_consent,
    reject_proposal,
)


def _state(**overrides):
    values = {
        "case_id": "SYNTHETIC-CASE-DOMAIN-01",
        "case_version": "case-v4",
        "goal_version": "goal-v3",
        "active_proposal_id": "SYNTHETIC-PROPOSAL-A",
        "active_proposal_case_version": "case-v4",
        "active_proposal_goal_version": "goal-v3",
        "rejected_proposal_ids": (),
        "client_decision": ClientDecision.NONE,
        "execution_consent_for_proposal_id": None,
    }
    values.update(overrides)
    return DialogueCaseState(**values)


def test_goal_change_creates_new_version_and_invalidates_prior_proposal_and_decisions():
    prior = _state(
        client_decision=ClientDecision.ACCEPTED,
        execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-A",
    )

    changed = change_goal(prior, "goal-v4")

    assert changed.goal_version == "goal-v4"
    assert changed.case_version == prior.case_version
    assert changed.active_proposal_id is None
    assert changed.active_proposal_case_version is None
    assert changed.active_proposal_goal_version is None
    assert changed.client_decision is ClientDecision.NONE
    assert changed.execution_consent_for_proposal_id is None
    assert prior.goal_version == "goal-v3"
    assert prior.active_proposal_id == "SYNTHETIC-PROPOSAL-A"


@pytest.mark.parametrize("new_goal_version", ["", "   ", "goal-v3"])
def test_goal_change_rejects_blank_or_unchanged_version(new_goal_version):
    with pytest.raises(ValueError):
        change_goal(_state(), new_goal_version)


def test_attaching_proposal_binds_it_to_both_current_versions_and_resets_decisions():
    prior = _state(
        client_decision=ClientDecision.ACCEPTED,
        execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-OLD",
    )

    attached = attach_proposal(prior, "SYNTHETIC-PROPOSAL-B")

    assert attached.active_proposal_id == "SYNTHETIC-PROPOSAL-B"
    assert attached.active_proposal_case_version == "case-v4"
    assert attached.active_proposal_goal_version == "goal-v3"
    assert attached.client_decision is ClientDecision.NONE
    assert attached.execution_consent_for_proposal_id is None


def test_rejected_proposal_cannot_be_attached_again():
    prior = _state(
        active_proposal_id=None,
        active_proposal_case_version=None,
        active_proposal_goal_version=None,
        rejected_proposal_ids=("SYNTHETIC-PROPOSAL-A",),
        client_decision=ClientDecision.REJECTED,
    )

    with pytest.raises(ValueError, match="cannot be reactivated"):
        attach_proposal(prior, "SYNTHETIC-PROPOSAL-A")


def test_acceptance_is_not_execution_consent():
    accepted = accept_proposal(_state(), "SYNTHETIC-PROPOSAL-A")

    assert accepted.client_decision is ClientDecision.ACCEPTED
    assert accepted.execution_consent_for_proposal_id is None


@pytest.mark.parametrize(
    "state,proposal_id,explicit_consent",
    [
        (_state(), "SYNTHETIC-PROPOSAL-A", True),
        (_state(client_decision=ClientDecision.ACCEPTED), "SYNTHETIC-PROPOSAL-OTHER", True),
        (_state(client_decision=ClientDecision.ACCEPTED), "SYNTHETIC-PROPOSAL-A", False),
        (
            _state(
                client_decision=ClientDecision.ACCEPTED,
                active_proposal_goal_version="goal-v2",
            ),
            "SYNTHETIC-PROPOSAL-A",
            True,
        ),
        (
            _state(
                client_decision=ClientDecision.ACCEPTED,
                active_proposal_case_version="case-v3",
            ),
            "SYNTHETIC-PROPOSAL-A",
            True,
        ),
    ],
)
def test_execution_consent_requires_explicit_consent_for_accepted_current_proposal(
    state, proposal_id, explicit_consent
):
    with pytest.raises(ValueError, match="Explicit execution consent"):
        record_execution_consent(state, proposal_id, explicit_consent=explicit_consent)


def test_explicit_consent_binds_to_exact_accepted_current_proposal():
    accepted = accept_proposal(_state(), "SYNTHETIC-PROPOSAL-A")

    consented = record_execution_consent(
        accepted,
        "SYNTHETIC-PROPOSAL-A",
        explicit_consent=True,
    )

    assert consented.execution_consent_for_proposal_id == "SYNTHETIC-PROPOSAL-A"


def test_rejection_deactivates_proposal_and_preserves_traceable_rejection():
    rejected = reject_proposal(_state(), "SYNTHETIC-PROPOSAL-A")

    assert rejected.active_proposal_id is None
    assert rejected.active_proposal_case_version is None
    assert rejected.active_proposal_goal_version is None
    assert rejected.rejected_proposal_ids == ("SYNTHETIC-PROPOSAL-A",)
    assert rejected.client_decision is ClientDecision.REJECTED
    assert rejected.execution_consent_for_proposal_id is None


@pytest.mark.parametrize(
    "status,expected_status,should_preserve",
    [
        ("PRESERVE", "PRESERVED", True),
        ("INVALIDATE", "INVALIDATED", False),
        ("UNRESOLVED", "REASSESSMENT_REQUIRED", False),
        ("UNKNOWN", "ENGINE_FAIL_CLOSED", False),
        ("", "ENGINE_FAIL_CLOSED", False),
    ],
)
def test_dependency_reassessment_preserves_only_explicit_preserve_status(
    status, expected_status, should_preserve
):
    prior = _state(
        client_decision=ClientDecision.ACCEPTED,
        execution_consent_for_proposal_id="SYNTHETIC-PROPOSAL-A",
    )

    result = apply_dependency_reassessment(prior, status)

    assert result.status == expected_status
    if should_preserve:
        assert result.state == prior
    else:
        assert result.state.active_proposal_id is None
        assert result.state.active_proposal_case_version is None
        assert result.state.active_proposal_goal_version is None
        assert result.state.client_decision is ClientDecision.NONE
        assert result.state.execution_consent_for_proposal_id is None
        assert prior.active_proposal_id == "SYNTHETIC-PROPOSAL-A"
