"""Synthetic, fail-closed consultation case workflow state machine.

This module models governance transitions only. It contains no hair-color
chemistry, recommendation logic, or execution instructions.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping


class WorkflowState(str, Enum):
    INCOMPLETE_ACCEPTANCE = "INCOMPLETE_ACCEPTANCE"
    AWAITING_EVALUATION = "AWAITING_EVALUATION"
    AWAITING_TEST = "AWAITING_TEST"
    SAFETY_STOPPED = "SAFETY_STOPPED"
    READY_FOR_SPECIALIST_DECISION = "READY_FOR_SPECIALIST_DECISION"
    AWAITING_CLIENT_CONFIRMATION = "AWAITING_CLIENT_CONFIRMATION"
    APPROVED_FOR_EXECUTION = "APPROVED_FOR_EXECUTION"
    IN_EXECUTION = "IN_EXECUTION"
    NEEDS_FOLLOWUP = "NEEDS_FOLLOWUP"
    CLOSED = "CLOSED"


_ALLOWED: Mapping[WorkflowState, frozenset[WorkflowState]] = {
    WorkflowState.INCOMPLETE_ACCEPTANCE: frozenset({WorkflowState.AWAITING_EVALUATION, WorkflowState.CLOSED}),
    WorkflowState.AWAITING_EVALUATION: frozenset({
        WorkflowState.AWAITING_TEST, WorkflowState.SAFETY_STOPPED,
        WorkflowState.READY_FOR_SPECIALIST_DECISION, WorkflowState.CLOSED,
    }),
    WorkflowState.AWAITING_TEST: frozenset({
        WorkflowState.AWAITING_EVALUATION, WorkflowState.SAFETY_STOPPED, WorkflowState.CLOSED,
    }),
    WorkflowState.SAFETY_STOPPED: frozenset({WorkflowState.CLOSED}),
    WorkflowState.READY_FOR_SPECIALIST_DECISION: frozenset({
        WorkflowState.AWAITING_CLIENT_CONFIRMATION, WorkflowState.SAFETY_STOPPED, WorkflowState.CLOSED,
    }),
    WorkflowState.AWAITING_CLIENT_CONFIRMATION: frozenset({
        WorkflowState.APPROVED_FOR_EXECUTION, WorkflowState.SAFETY_STOPPED, WorkflowState.CLOSED,
    }),
    WorkflowState.APPROVED_FOR_EXECUTION: frozenset({
        WorkflowState.IN_EXECUTION, WorkflowState.SAFETY_STOPPED, WorkflowState.CLOSED,
    }),
    WorkflowState.IN_EXECUTION: frozenset({WorkflowState.NEEDS_FOLLOWUP, WorkflowState.SAFETY_STOPPED}),
    WorkflowState.NEEDS_FOLLOWUP: frozenset({WorkflowState.CLOSED}),
    WorkflowState.CLOSED: frozenset(),
}


class WorkflowTransitionError(ValueError):
    """Raised when a workflow transition violates a guarded invariant."""


@dataclass(frozen=True)
class CaseWorkflow:
    case_ref: str
    case_version: int
    target_version: int
    state: WorkflowState
    last_transition_event: str | None = None


def transition(
    case: CaseWorkflow,
    next_state: WorkflowState,
    *,
    event_id: str,
    expected_case_version: int,
    expected_target_version: int,
    client_acceptance: bool = False,
    execution_consent: bool = False,
) -> CaseWorkflow:
    """Perform a guarded transition; acceptance and execution consent are distinct."""
    if not event_id.strip():
        raise WorkflowTransitionError("transition requires a traceable event_id")
    if (case.case_version, case.target_version) != (expected_case_version, expected_target_version):
        raise WorkflowTransitionError("stale case/target version; fresh evaluation required")
    if next_state not in _ALLOWED[case.state]:
        raise WorkflowTransitionError(f"transition not allowed: {case.state.value} -> {next_state.value}")
    if next_state == WorkflowState.APPROVED_FOR_EXECUTION and not (
        client_acceptance and execution_consent
    ):
        raise WorkflowTransitionError("approval requires separate client acceptance and execution consent")
    if case.state == WorkflowState.SAFETY_STOPPED and next_state != WorkflowState.CLOSED:
        raise WorkflowTransitionError("safety-stopped case cannot auto-resume")
    return replace(case, state=next_state, last_transition_event=event_id)


def restart_as_fresh_case_after_stop(case: CaseWorkflow, *, new_case_ref: str) -> CaseWorkflow:
    """Explicitly create a new versioned intake; never resumes the stopped case."""
    if case.state != WorkflowState.SAFETY_STOPPED:
        raise WorkflowTransitionError("fresh restart requires a safety-stopped source case")
    if not new_case_ref.strip() or new_case_ref == case.case_ref:
        raise WorkflowTransitionError("restart must use a distinct non-empty case reference")
    return CaseWorkflow(
        case_ref=new_case_ref,
        case_version=case.case_version + 1,
        target_version=case.target_version + 1,
        state=WorkflowState.INCOMPLETE_ACCEPTANCE,
        last_transition_event="FRESH_RESTART_FROM_STOP",
    )
