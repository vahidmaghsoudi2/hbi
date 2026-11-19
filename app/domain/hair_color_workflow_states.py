"""Canonical ten-case workflow states and guarded transitions."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class CaseWorkflowState(str, Enum):
    INCOMPLETE_ACCEPTANCE = "incomplete_acceptance"
    AWAITING_EVALUATION = "awaiting_evaluation"
    AWAITING_TEST = "awaiting_test"
    SAFETY_STOPPED = "safety_stopped"
    READY_FOR_SPECIALIST_DECISION = "ready_for_specialist_decision"
    AWAITING_CLIENT_CONFIRMATION = "awaiting_client_confirmation"
    APPROVED_FOR_EXECUTION = "approved_for_execution"
    IN_EXECUTION = "in_execution"
    NEEDS_FOLLOW_UP = "needs_follow_up"
    CLOSED = "closed"

@dataclass(frozen=True)
class TransitionFacts:
    intake_complete: bool = False
    evaluation_complete: bool = False
    evidence_ready: bool = False
    test_required: bool = False
    test_completed: bool = False
    safety_stop: bool = False
    specialist_approved: bool = False
    client_acceptance: bool = False
    execution_consent: bool = False
    client_rejected: bool = False
    execution_authorized: bool = False
    completion_recorded: bool = False
    followup_needed: bool = False
    fresh_evaluation: bool = False
    restart_authorized: bool = False
    close_authorized: bool = False

@dataclass(frozen=True)
class TransitionResult:
    allowed: bool
    from_state: str
    to_state: str
    reason: str

def allowed_workflow_transitions() -> dict[CaseWorkflowState, tuple[CaseWorkflowState,...]]:
    return {
        CaseWorkflowState.INCOMPLETE_ACCEPTANCE: (CaseWorkflowState.AWAITING_EVALUATION,),
        CaseWorkflowState.AWAITING_EVALUATION: (CaseWorkflowState.AWAITING_TEST,CaseWorkflowState.SAFETY_STOPPED,CaseWorkflowState.READY_FOR_SPECIALIST_DECISION,CaseWorkflowState.NEEDS_FOLLOW_UP),
        CaseWorkflowState.AWAITING_TEST: (CaseWorkflowState.AWAITING_EVALUATION,CaseWorkflowState.SAFETY_STOPPED,CaseWorkflowState.NEEDS_FOLLOW_UP),
        CaseWorkflowState.SAFETY_STOPPED: (CaseWorkflowState.AWAITING_EVALUATION,CaseWorkflowState.CLOSED),
        CaseWorkflowState.READY_FOR_SPECIALIST_DECISION: (CaseWorkflowState.AWAITING_TEST,CaseWorkflowState.SAFETY_STOPPED,CaseWorkflowState.AWAITING_CLIENT_CONFIRMATION,CaseWorkflowState.NEEDS_FOLLOW_UP),
        CaseWorkflowState.AWAITING_CLIENT_CONFIRMATION: (CaseWorkflowState.APPROVED_FOR_EXECUTION,CaseWorkflowState.SAFETY_STOPPED,CaseWorkflowState.NEEDS_FOLLOW_UP,CaseWorkflowState.CLOSED),
        CaseWorkflowState.APPROVED_FOR_EXECUTION: (CaseWorkflowState.IN_EXECUTION,),
        CaseWorkflowState.IN_EXECUTION: (CaseWorkflowState.NEEDS_FOLLOW_UP,CaseWorkflowState.CLOSED),
        CaseWorkflowState.NEEDS_FOLLOW_UP: (CaseWorkflowState.AWAITING_EVALUATION,CaseWorkflowState.CLOSED),
        CaseWorkflowState.CLOSED: (),
    }

def transition_case(current: object, target: object, facts: object) -> TransitionResult:
    try:
        src,dst=CaseWorkflowState(current),CaseWorkflowState(target)
    except (ValueError,TypeError):
        return TransitionResult(False,str(current),str(target),"Invalid workflow state; reject transition.")
    if not isinstance(facts,TransitionFacts):
        return TransitionResult(False,src.value,dst.value,"Transition facts invalid; reject transition.")
    if dst not in allowed_workflow_transitions()[src]:
        return TransitionResult(False,src.value,dst.value,"Transition is not in the allowed workflow map.")
    if dst==CaseWorkflowState.AWAITING_EVALUATION and src==CaseWorkflowState.INCOMPLETE_ACCEPTANCE:
        ok=facts.intake_complete
        why="Intake must be complete before evaluation."
    elif dst==CaseWorkflowState.AWAITING_EVALUATION and src in (CaseWorkflowState.AWAITING_TEST,CaseWorkflowState.NEEDS_FOLLOW_UP):
        ok=facts.fresh_evaluation and (src!=CaseWorkflowState.AWAITING_TEST or facts.test_completed)
        why="A completed test (if required) and fresh evaluation are required; do not resume automatically."
    elif dst==CaseWorkflowState.AWAITING_EVALUATION and src==CaseWorkflowState.SAFETY_STOPPED:
        ok=facts.fresh_evaluation and facts.restart_authorized
        why="Restart after safety stop requires explicit authorization and fresh evaluation."
    elif dst==CaseWorkflowState.AWAITING_TEST:
        ok=facts.test_required
        why="A documented test requirement must be present."
    elif dst==CaseWorkflowState.SAFETY_STOPPED:
        ok=facts.safety_stop
        why="A recorded safety-stop condition is required."
    elif dst==CaseWorkflowState.READY_FOR_SPECIALIST_DECISION:
        ok=facts.evaluation_complete and facts.evidence_ready and not facts.safety_stop and not facts.test_required
        why="Evaluation and evidence readiness are required; no safety stop or outstanding test."
    elif dst==CaseWorkflowState.AWAITING_CLIENT_CONFIRMATION:
        ok=facts.specialist_approved
        why="Specialist decision must be recorded before client confirmation."
    elif dst==CaseWorkflowState.APPROVED_FOR_EXECUTION:
        ok=facts.specialist_approved and facts.client_acceptance and facts.execution_consent
        why="Specialist approval, client acceptance, and separate explicit execution consent are required."
    elif dst==CaseWorkflowState.IN_EXECUTION:
        ok=facts.execution_authorized
        why="Execution authorization must be recorded."
    elif dst==CaseWorkflowState.NEEDS_FOLLOW_UP:
        ok=facts.followup_needed
        why="A follow-up requirement must be recorded."
    elif dst==CaseWorkflowState.CLOSED:
        ok=facts.completion_recorded if src==CaseWorkflowState.IN_EXECUTION else facts.close_authorized
        why="Completion or authorized administrative closure must be recorded."
    else:
        ok=False
        why="No transition rule defined; reject."
    return TransitionResult(bool(ok),src.value,dst.value,
        "Transition allowed." if ok else why)
