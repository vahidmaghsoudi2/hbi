"""Canonical four-state decision motor; no extra response/workflow states."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class MotorState(str, Enum):
    SUGGESTION_REVIEWABLE = "suggestion_reviewable"
    CONDITIONAL_SUGGESTION = "conditional_suggestion"
    REQUEST_MORE_INFORMATION = "request_more_information"
    STOP_OR_REFERRAL = "stop_or_referral"

@dataclass(frozen=True)
class DecisionSignals:
    engine_fail: bool = False
    safety_stop: bool = False
    scope_exclusion: bool = False
    knowledge_gap: bool = False
    data_gap: bool = False
    condition_pending: bool = False
    valid_candidate: bool = False

@dataclass(frozen=True)
class MotorDecision:
    state: MotorState
    reason_code: str
    message: str

def decide_motor_state(signals: object) -> MotorDecision:
    if not isinstance(signals, DecisionSignals):
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"invalid_input",
            "Decision signals invalid; fail closed and stop output.")
    if signals.engine_fail:
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"engine_fail",
            "Internal failure: stop this run; no output.")
    if signals.safety_stop:
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"safety_stop",
            "Safety stop; no execution-oriented suggestion.")
    if signals.scope_exclusion:
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"scope_exclusion",
            "Outside permitted scope; stop or refer.")
    if signals.knowledge_gap:
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"knowledge_gap",
            "Reliable knowledge/evidence is unavailable; do not guess.")
    if signals.data_gap:
        return MotorDecision(MotorState.REQUEST_MORE_INFORMATION,"data_gap",
            "Required data is missing; request it before dependent advice.")
    if not signals.valid_candidate:
        return MotorDecision(MotorState.STOP_OR_REFERRAL,"no_valid_candidate",
            "No valid evidence-backed candidate; do not fabricate an option.")
    if signals.condition_pending:
        return MotorDecision(MotorState.CONDITIONAL_SUGGESTION,"condition_pending",
            "Candidate is conditional; prerequisite must not be assumed satisfied.")
    return MotorDecision(MotorState.SUGGESTION_REVIEWABLE,"candidate_reviewable",
        "Candidate may be reviewed; this state is not client acceptance or execution consent.")
