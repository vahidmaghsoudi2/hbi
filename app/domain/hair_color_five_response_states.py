"""Five consultation response labels; conditional remains a motor state only."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ConsultationResponseState(str, Enum):
    SUGGESTION_REVIEWABLE_BY_SPECIALIST = "suggestion_reviewable_by_specialist"
    NEEDS_MORE_INFORMATION_OR_TEST = "needs_more_information_or_test"
    NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW = "needs_in_person_or_specialist_review"
    SAFETY_STOP_NO_EXECUTION_SUGGESTION = "safety_stop_no_execution_suggestion"
    OUTSIDE_FIRST_VERSION_SCOPE = "outside_first_version_scope"

@dataclass(frozen=True)
class ResponseMapping:
    state: ConsultationResponseState
    reason_code: str
    message: str

def map_motor_to_response(motor_state: object, reason_code: object = "",
                         condition_type: object = "") -> ResponseMapping:
    if motor_state not in ("suggestion_reviewable","conditional_suggestion",
                           "request_more_information","stop_or_referral"):
        return ResponseMapping(ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW,
            "invalid_motor_state","Unknown motor state; conservative specialist review.")
    reason=reason_code if isinstance(reason_code,str) else ""
    condition=condition_type if isinstance(condition_type,str) else ""
    if motor_state=="suggestion_reviewable":
        return ResponseMapping(ConsultationResponseState.SUGGESTION_REVIEWABLE_BY_SPECIALIST,
            reason or "candidate_reviewable","Suggestion may be reviewed by specialist; no acceptance or execution consent implied.")
    if motor_state=="request_more_information":
        return ResponseMapping(ConsultationResponseState.NEEDS_MORE_INFORMATION_OR_TEST,
            reason or "data_gap","Request the missing information or required test.")
    if motor_state=="conditional_suggestion":
        if condition in ("data","test"):
            return ResponseMapping(ConsultationResponseState.NEEDS_MORE_INFORMATION_OR_TEST,
                reason or "condition_pending","Conditional motor state; obtain the required information/test first.")
        return ResponseMapping(ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW,
            reason or "condition_requires_review","Conditional motor state; specialist review is needed to resolve the condition.")
    if reason in ("scope_exclusion","outside_scope"):
        return ResponseMapping(ConsultationResponseState.OUTSIDE_FIRST_VERSION_SCOPE,
            reason,"Request is outside first-version scope; no recommendation is produced.")
    if reason in ("safety_stop","allergy_or_test_stop"):
        return ResponseMapping(ConsultationResponseState.SAFETY_STOP_NO_EXECUTION_SUGGESTION,
            reason,"Safety stop; no execution-oriented suggestion.")
    return ResponseMapping(ConsultationResponseState.NEEDS_IN_PERSON_OR_SPECIALIST_REVIEW,
        reason or "stop_or_referral","Stop/referral requires in-person or specialist review; do not guess.")

def response_state_labels() -> tuple[str,...]:
    return tuple(s.value for s in ConsultationResponseState)
