"""Distinct gap categories and fail-closed output controls."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class GapKind(str,Enum):
    DATA_GAP="data_gap"
    KNOWLEDGE_GAP="knowledge_gap"
    ENGINE_FAIL="engine_fail"

@dataclass(frozen=True)
class GapRecord:
    gap_id: str
    kind: GapKind
    affected_claim: str
    detail: str
    required_input: str = ""

@dataclass(frozen=True)
class GapHandling:
    status: str
    output_policy: str
    gap_ids: tuple[str,...]
    data_gap_ids: tuple[str,...]
    knowledge_gap_ids: tuple[str,...]
    engine_fail_ids: tuple[str,...]
    request_inputs: tuple[str,...]
    message: str

def make_gap(gap_id: object,kind: object,affected_claim: object,detail: object,required_input: object="")->GapRecord|None:
    try:k=GapKind(kind)
    except (ValueError,TypeError):return None
    if not all(isinstance(x,str) and x.strip() for x in (gap_id,affected_claim,detail)):return None
    req=required_input.strip() if isinstance(required_input,str) else ""
    if k==GapKind.DATA_GAP and not req:return None
    if k!=GapKind.DATA_GAP and req:return None
    return GapRecord(gap_id.strip(),k,affected_claim.strip(),detail.strip(),req)

def handle_gaps(gaps: object)->GapHandling:
    if not isinstance(gaps,(tuple,list)) or any(not isinstance(g,GapRecord) for g in gaps):
        return GapHandling("invalid_gaps","suppress_run_output",(),(),(),(),(),"Invalid gap record; fail closed.")
    ids=tuple(g.gap_id for g in gaps)
    if len(set(ids))!=len(ids):
        return GapHandling("duplicate_gap_ids","suppress_run_output",ids,(),(),(),(),"Duplicate gap IDs; reconcile.")
    data=tuple(g.gap_id for g in gaps if g.kind==GapKind.DATA_GAP)
    knowledge=tuple(g.gap_id for g in gaps if g.kind==GapKind.KNOWLEDGE_GAP)
    engine=tuple(g.gap_id for g in gaps if g.kind==GapKind.ENGINE_FAIL)
    inputs=tuple(dict.fromkeys(g.required_input for g in gaps if g.kind==GapKind.DATA_GAP))
    if engine:
        return GapHandling("engine_fail","suppress_run_output",ids,data,knowledge,engine,inputs,
            "Internal error; suppress all output for this run. Do not retry by guessing.")
    if data and knowledge:
        return GapHandling("mixed_gaps","suppress_affected_claims_and_request_data",ids,data,knowledge,engine,inputs,
            "Request only listed missing inputs; knowledge-gap claims remain unanswered without reliable evidence.")
    if knowledge:
        return GapHandling("knowledge_gap","suppress_affected_claims",ids,data,knowledge,engine,inputs,
            "Reliable evidence unavailable for affected claims; no answer or formula guess.")
    if data:
        return GapHandling("data_gap","request_missing_inputs",ids,data,knowledge,engine,inputs,
            "Required data missing; request the listed specific input before dependent advice.")
    return GapHandling("no_gap","normal_claim_gates",(),(),(),(),(),
        "No gap record; other safety, scope, and validation gates still apply.")
