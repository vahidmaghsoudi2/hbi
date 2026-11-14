"""Negative tests for synthetic proposal identifiers and lifecycle-state integrity."""
import pytest

from app.domain.hair_dialogue_contract import (
    ClientDecision,
    accept_proposal,
    attach_proposal,
    record_execution_consent,
    reject_proposal,
    validate_dialogue_state,
    validate_proposal_id,
)


def _state(**overrides):
    values = {
        "case_id": "SYNTHETIC-CASE-INTEGRITY-01",
        "case_version": "case-v1",
        "goal_version": "goal-v1",
        "active_proposal_id": "SYNTHETIC-PROPOSAL-1",
        "active_proposal_case_version": "case-v1",
        "active_proposal_goal_version": "goal-v1",
        "rejected_proposal_ids": (),
        "client_decision": ClientDecision.NONE,
        "execution_consent_for_proposal_id": None,
    }
    values.update(overrides)
    return DialogueCaseState(**values)


@pytest.mark.parametrize("value", [
    "", " ", "SYNTHETIC-", " SYNTHETIC-PROPOSAL-1",
    "SYNTHETIC-PROPOSAL-1 ", "REAL-PROPOSAL-1",
    "SYNTHETIC-   ", "SYNTHETIC-PROPOSAL/1",
])
def test_proposal_identifier_rejects_blank_padded_or_malformed_values(value):
    with pytest.raises(ValueError):
        validate_proposal_id(value)


@pytest.mark.parametrize("field,value", [
    ("active_proposal_id", ""),
    ("active_proposal_id", "REAL-PROPOSAL-1"),
    ("active_proposal_id", " SYNTHETIC-PROPOSAL-1"),
    ("active_proposal_id", "SYNTHETIC-"),
    ("rejected_proposal_ids", ("SYNTHETIC-GOOD", "REAL-BAD")),
    ("rejected_proposal_ids", ("SYNTHETIC-GOOD", "SYNTHETIC-")),
    ("execution_consent_for_proposal_id", "REAL-PROPOSAL-1"),
    ("execution_consent_for_proposal_id", "SYNTHETIC-"),
])
def test_state_validation_rejects_invalid_proposal_references(field, value):
    with pytest.raises((TypeError, ValueError)):
        validate_dialogue_state(_state(**{field: value}))


def test_state_rejects_mutable_rejected_id_container_even_when_dataclass_is_frozen():
    injected = _state(rejected_proposal_ids=["SYNTHETIC-REJECTED"])
    with pytest.raises(TypeError, match="immutable tuple"):
        validate_dialogue_state(injected)


@pytest.mark.parametrize("overrides", [
    {"active_proposal_id": None},
    {"active_proposal_case_version": None},
    {"active_proposal_goal_version": "goal-v0"},
    {"client_decision": ClientDecision.ACCEPTED, "active_proposal_id": None,
     "active_proposal_case_version": None, "active_proposal_goal_version": None},
    {"client_decision": ClientDecision.REJECTED},
    {"execution_consent_for_proposal_id": "SYNTHETIC-OTHER",
     "client_decision": ClientDecision.ACCEPTED},
    {"execution_consent_for_proposal_id": "SYNTHETIC-PROPOSAL-1"},
    {"active_proposal_id": "SYNTHETIC-PROPOSAL-1",
     "rejected_proposal_ids": ("SYNTHETIC-PROPOSAL-1",)},
    {"client_decision": "ACCEPTED"},
])
def test_state_rejects_inconsistent_proposal_decision_and_consent_combinations(overrides):
    with pytest.raises((TypeError, ValueError)):
        validate_dialogue_state(_state(**overrides))


def test_valid_accepted_and_consented_state_passes_validation():
    accepted = accept_proposal(_state(), "SYNTHETIC-PROPOSAL-1")
    consented = record_execution_consent(
        accepted, "SYNTHETIC-PROPOSAL-1", explicit_consent=True
    )
    validate_dialogue_state(consented)


@pytest.mark.parametrize("bad_id", ["", " ", "SYNTHETIC-", " SYNTHETIC-X", "REAL-X"])
def test_all_proposal_transitions_reject_invalid_request_ids(bad_id):
    with pytest.raises(ValueError):
        attach_proposal(_state(active_proposal_id=None,
                               active_proposal_case_version=None,
                               active_proposal_goal_version=None), bad_id)
    with pytest.raises(ValueError):
        accept_proposal(_state(), bad_id)
    with pytest.raises(ValueError):
        reject_proposal(_state(), bad_id)
    with pytest.raises(ValueError):
        record_execution_consent(
            _state(client_decision=ClientDecision.ACCEPTED),
            bad_id,
            explicit_consent=True,
        )
