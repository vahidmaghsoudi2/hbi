"""Proposal limitation gate; preserves data/knowledge/safety/engine distinctions."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class LimitationKind(str, Enum):
    DATA_GAP = "data_gap"
    KNOWLEDGE_GAP = "knowledge_gap"
    SAFETY_STOP = "safety_stop"
    SCOPE_EXCLUSION = "scope_exclusion"
    ENGINE_FAIL = "engine_fail"
    CONDITION = "condition"

@dataclass(frozen=True)
class ProposalLimitation:
    limitation_id: str
    kind: LimitationKind
    description: str
    affected_claim: str
    blocking: bool
    required_condition: str = ""

@dataclass(frozen=True)
class LimitationAssessment:
    status: str
    motor_state: str
    response_gate: str
    active_limitation_ids: tuple[str, ...]
    message: str

def make_limitation(limitation_id: object, kind: object, description: object,
                   affected_claim: object = "", blocking: object = True,
                   required_condition: object = "") -> ProposalLimitation | None:
    try:
        k=LimitationKind(kind)
    except (ValueError, TypeError):
        return None
    if not isinstance(limitation_id,str) or not limitation_id.strip():
        return None
    if not isinstance(description,str) or not description.strip():
        return None
    if not isinstance(blocking,bool):
        return None
    claim=affected_claim.strip() if isinstance(affected_claim,str) else ""
    condition=required_condition.strip() if isinstance(required_condition,str) else ""
    if k==LimitationKind.CONDITION and not condition:
        return None
    return ProposalLimitation(limitation_id.strip(),k,description.strip(),claim,blocking,condition)

def assess_proposal_limitations(limits: object) -> LimitationAssessment:
    if not isinstance(limits,(tuple,list)):
        return LimitationAssessment("invalid_limitations","stop_or_referral","invalid_input",(),
            "Limitation records invalid; no proposal output.")
    if any(not isinstance(x,ProposalLimitation) for x in limits):
        return LimitationAssessment("invalid_limitations","stop_or_referral","invalid_input",(),
            "Invalid limitation record; fail closed.")
    ids=[x.limitation_id for x in limits]
    if len(set(ids))!=len(ids):
        return LimitationAssessment("duplicate_limitation_ids","stop_or_referral","invalid_input",(),
            "Duplicate limitation IDs; reconcile before output.")
    active=tuple(x.limitation_id for x in limits if x.blocking or x.kind==LimitationKind.CONDITION)
    kinds={x.kind for x in limits if x.blocking}
    if LimitationKind.ENGINE_FAIL in kinds:
        return LimitationAssessment("engine_fail","stop_or_referral","engine_fail",active,
            "Internal failure; stop output for this run. Do not guess or continue.")
    if LimitationKind.SAFETY_STOP in kinds:
        return LimitationAssessment("safety_stop","stop_or_referral","safety_stop",active,
            "Safety stop: no execution-oriented suggestion; follow the appropriate specialist/safety pathway.")
    if LimitationKind.SCOPE_EXCLUSION in kinds:
        return LimitationAssessment("scope_excluded","stop_or_referral","outside_scope",active,
            "This claim or request is outside the permitted scope; do not output a recommendation.")
    if LimitationKind.KNOWLEDGE_GAP in kinds:
        return LimitationAssessment("knowledge_gap","stop_or_referral","knowledge_gap",active,
            "No reliable knowledge/evidence for the affected claim; do not invent an answer.")
    if LimitationKind.DATA_GAP in kinds:
        return LimitationAssessment("data_gap","request_more_information","data_gap",active,
            "Required information is missing; request the specific missing data before dependent advice.")
    if any(x.kind==LimitationKind.CONDITION for x in limits):
        return LimitationAssessment("conditional","conditional_suggestion","conditional",active,
            "Suggestion remains conditional on the recorded conditions; do not treat conditions as satisfied.")
    return LimitationAssessment("reviewable","suggestion_reviewable","reviewable",(),
        "No blocking limitation recorded; output remains reviewable and is not execution consent.")
