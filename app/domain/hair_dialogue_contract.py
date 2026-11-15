"""Synthetic-only executable contract for the ten approved Hair dialogue scenarios.

This module models dialogue invariants only. It does not generate hair-colour
advice, chemical parameters, safety conclusions, client records, or persistence.
All state is immutable and must use a SYNTHETIC- case identifier.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from app.domain.hair_data_governance import (
    is_permitted_synthetic_identifier,
    is_permitted_synthetic_version,
    is_permitted_field_name,
)


class ClientDecision(str, Enum):
    NONE = "NONE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class DialogueCaseState:
    case_id: str
    case_version: str
    goal_version: str
    active_proposal_id: str | None = None
    active_proposal_case_version: str | None = None
    active_proposal_goal_version: str | None = None
    rejected_proposal_ids: tuple[str, ...] = ()
    client_decision: ClientDecision = ClientDecision.NONE
    execution_consent_for_proposal_id: str | None = None


@dataclass(frozen=True)
class DialogueReply:
    answer: str
    state: DialogueCaseState
    decision_changed: bool = False


@dataclass(frozen=True)
class RequiredDataResolution:
    known_values: tuple[tuple[str, Any], ...]
    missing_fields: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_fields


@dataclass(frozen=True)
class AdviceGate:
    advice_allowed: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ReassessmentResult:
    state: DialogueCaseState
    status: str


def validate_dialogue_state(state: DialogueCaseState) -> None:
    """Validate the complete synthetic identity envelope before any transition or echo."""
    if not isinstance(state, DialogueCaseState):
        raise TypeError("state must be a DialogueCaseState")
    if (
        not is_permitted_synthetic_identifier(state.case_id)
        or not is_permitted_synthetic_version(state.case_version, kind="case")
        or not is_permitted_synthetic_version(state.goal_version, kind="goal")
    ):
        raise ValueError("Only bounded synthetic case and goal identifiers are permitted")

    optional_identifiers = (
        state.active_proposal_id,
        state.execution_consent_for_proposal_id,
    )
    if any(
        value is not None and not is_permitted_synthetic_identifier(value)
        for value in optional_identifiers
    ):
        raise ValueError("Only bounded synthetic proposal identifiers are permitted")

    if not isinstance(state.rejected_proposal_ids, tuple) or any(
        not is_permitted_synthetic_identifier(value)
        for value in state.rejected_proposal_ids
    ):
        raise ValueError("Rejected proposal identifiers must be synthetic")

    if (
        state.active_proposal_case_version is not None
        and not is_permitted_synthetic_version(state.active_proposal_case_version, kind="case")
    ):
        raise ValueError("Active proposal case version must be a synthetic version token")
    if (
        state.active_proposal_goal_version is not None
        and not is_permitted_synthetic_version(state.active_proposal_goal_version, kind="goal")
    ):
        raise ValueError("Active proposal goal version must be a synthetic version token")


def answer_question(
    state: DialogueCaseState,
    *,
    question: str,
    answer: str,
) -> DialogueReply:
    """Answer a question without changing acceptance, rejection, or consent."""
    validate_dialogue_state(state)
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A non-empty customer question is required")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("A non-empty answer is required")
    return DialogueReply(answer=answer, state=state, decision_changed=False)


def explain_reason(client_safe_summary: str) -> str:
    """Return only an explicitly supplied client-safe explanation."""
    if not isinstance(client_safe_summary, str) or not client_safe_summary.strip():
        raise ValueError("A client-safe reason summary is required")
    return client_safe_summary.strip()


def resolve_required_data(
    recorded_data: Mapping[str, Any],
    required_fields: tuple[str, ...],
) -> RequiredDataResolution:
    """Use recorded values only; report exact missing fields and never infer them."""
    if not isinstance(recorded_data, Mapping):
        raise TypeError("recorded_data must be a mapping")
    if any(not is_permitted_field_name(field) for field in recorded_data):
        raise ValueError("recorded_data keys must be bounded schema field names")
    if not isinstance(required_fields, tuple) or not all(
        is_permitted_field_name(field) for field in required_fields
    ):
        raise ValueError("required_fields must be a tuple of bounded schema field names")
    if len(set(required_fields)) != len(required_fields):
        raise ValueError("required_fields must not contain duplicates")

    known = []
    missing = []
    for field in required_fields:
        value = recorded_data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
        else:
            known.append((field, value))
    return RequiredDataResolution(tuple(known), tuple(missing))


def evaluate_advice_gate(
    *,
    data_complete: bool,
    safety_passed: bool,
    rule_valid: bool,
    evidence_valid: bool,
    engine_ok: bool = True,
) -> AdviceGate:
    """Binary advice gate; any unmet precondition withholds definitive advice."""
    if engine_ok is not True:
        return AdviceGate(False, ("ENGINE_FAIL",))
    if safety_passed is not True:
        return AdviceGate(False, ("SAFETY_STOP",))
    reasons = []
    if data_complete is not True:
        reasons.append("DATA_GAP")
    if rule_valid is not True or evidence_valid is not True:
        reasons.append("KNOWLEDGE_GAP")
    return AdviceGate(not reasons, tuple(reasons))


def attach_proposal(
    state: DialogueCaseState,
    proposal_id: str,
) -> DialogueCaseState:
    """Attach a version-bound synthetic proposal unless its ID was rejected."""
    validate_dialogue_state(state)
    if not is_permitted_synthetic_identifier(proposal_id):
        raise ValueError("Only bounded synthetic proposal identifiers are permitted")
    if proposal_id in state.rejected_proposal_ids:
        raise ValueError("A rejected proposal cannot be reactivated")
    return replace(
        state,
        active_proposal_id=proposal_id,
        active_proposal_case_version=state.case_version,
        active_proposal_goal_version=state.goal_version,
        client_decision=ClientDecision.NONE,
        execution_consent_for_proposal_id=None,
    )


def accept_proposal(
    state: DialogueCaseState,
    proposal_id: str,
) -> DialogueCaseState:
    """Record client acceptance only; execution consent remains independent."""
    validate_dialogue_state(state)
    if (
        proposal_id != state.active_proposal_id
        or state.active_proposal_case_version != state.case_version
        or state.active_proposal_goal_version != state.goal_version
    ):
        raise ValueError("Acceptance must target the active proposal on the current versions")
    return replace(
        state,
        client_decision=ClientDecision.ACCEPTED,
        execution_consent_for_proposal_id=None,
    )


def reject_proposal(
    state: DialogueCaseState,
    proposal_id: str,
) -> DialogueCaseState:
    """Record rejection on the active version and deactivate that proposal."""
    validate_dialogue_state(state)
    if (
        proposal_id != state.active_proposal_id
        or state.active_proposal_case_version != state.case_version
        or state.active_proposal_goal_version != state.goal_version
    ):
        raise ValueError("Rejection must target the active proposal on the current versions")
    rejected = tuple(dict.fromkeys((*state.rejected_proposal_ids, proposal_id)))
    return replace(
        state,
        active_proposal_id=None,
        active_proposal_case_version=None,
        active_proposal_goal_version=None,
        rejected_proposal_ids=rejected,
        client_decision=ClientDecision.REJECTED,
        execution_consent_for_proposal_id=None,
    )


def record_execution_consent(
    state: DialogueCaseState,
    proposal_id: str,
    *,
    explicit_consent: bool,
) -> DialogueCaseState:
    """Record execution consent only after explicit consent for an accepted proposal."""
    validate_dialogue_state(state)
    if (
        explicit_consent is not True
        or state.client_decision != ClientDecision.ACCEPTED
        or proposal_id != state.active_proposal_id
        or state.active_proposal_case_version != state.case_version
        or state.active_proposal_goal_version != state.goal_version
    ):
        raise ValueError("Explicit execution consent for the accepted current proposal is required")
    return replace(state, execution_consent_for_proposal_id=proposal_id)


def change_goal(
    state: DialogueCaseState,
    new_goal_version: str,
) -> DialogueCaseState:
    """Create a fresh goal version and clear only the proposal/decisions it invalidates."""
    validate_dialogue_state(state)
    if not is_permitted_synthetic_version(new_goal_version, kind="goal"):
        raise ValueError("A bounded synthetic goal version token is required")
    if new_goal_version == state.goal_version:
        raise ValueError("A changed goal requires a new goal version")
    return replace(
        state,
        goal_version=new_goal_version,
        active_proposal_id=None,
        active_proposal_case_version=None,
        active_proposal_goal_version=None,
        client_decision=ClientDecision.NONE,
        execution_consent_for_proposal_id=None,
    )


def apply_dependency_reassessment(
    state: DialogueCaseState,
    invalidation_status: str,
) -> ReassessmentResult:
    """Invalidate dependent decisions on effective or unresolved changes."""
    validate_dialogue_state(state)
    if invalidation_status == "PRESERVE":
        return ReassessmentResult(state=state, status="PRESERVED")
    if invalidation_status == "INVALIDATE":
        status = "INVALIDATED"
    elif invalidation_status == "UNRESOLVED":
        status = "REASSESSMENT_REQUIRED"
    else:
        return ReassessmentResult(
            state=replace(
                state,
                active_proposal_id=None,
                active_proposal_case_version=None,
                active_proposal_goal_version=None,
                client_decision=ClientDecision.NONE,
                execution_consent_for_proposal_id=None,
            ),
            status="ENGINE_FAIL_CLOSED",
        )
    return ReassessmentResult(
        state=replace(
            state,
            active_proposal_id=None,
            active_proposal_case_version=None,
            active_proposal_goal_version=None,
            client_decision=ClientDecision.NONE,
            execution_consent_for_proposal_id=None,
        ),
        status=status,
    )


__all__ = [
    "AdviceGate",
    "ClientDecision",
    "DialogueCaseState",
    "DialogueReply",
    "ReassessmentResult",
    "RequiredDataResolution",
    "accept_proposal",
    "answer_question",
    "apply_dependency_reassessment",
    "attach_proposal",
    "change_goal",
    "evaluate_advice_gate",
    "explain_reason",
    "record_execution_consent",
    "reject_proposal",
    "resolve_required_data",
    "validate_dialogue_state",
]
