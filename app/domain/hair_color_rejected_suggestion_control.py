"""Trace rejected suggestions and prevent their reactivation as active alternatives."""
from __future__ import annotations
from dataclasses import dataclass

MAX_ALTERNATIVES=3

@dataclass(frozen=True)
class AlternativeCandidate:
    suggestion_id: str
    candidate_key: str
    valid: bool
    rank: int
    evidence_refs: tuple[str,...]
    reason: str = ""

@dataclass(frozen=True)
class RejectionSelection:
    rejected_ids: tuple[str,...]
    rejected_keys: tuple[str,...]
    alternatives: tuple[AlternativeCandidate,...]
    excluded: tuple[tuple[str,str],...]
    status: str
    message: str

def make_alternative(suggestion_id: object,candidate_key: object,valid: object,rank: object,
                    evidence_refs: object,reason: object="") -> AlternativeCandidate | None:
    if not isinstance(suggestion_id,str) or not suggestion_id.strip():
        return None
    if not isinstance(candidate_key,str) or not candidate_key.strip():
        return None
    if not isinstance(valid,bool):
        return None
    if not isinstance(rank,int) or isinstance(rank,bool) or rank<1:
        return None
    refs=tuple(x.strip() for x in evidence_refs if isinstance(x,str) and x.strip()) if isinstance(evidence_refs,(tuple,list)) else ()
    why=reason.strip() if isinstance(reason,str) else ""
    return AlternativeCandidate(suggestion_id.strip(),candidate_key.strip(),valid,rank,refs,why)

def reject_and_select_alternatives(current_suggestion_id: object,current_candidate_key: object,
                                  candidates: object,rejected_ids: object=(),
                                  rejected_keys: object=()) -> RejectionSelection:
    if not isinstance(current_suggestion_id,str) or not current_suggestion_id.strip() or not isinstance(current_candidate_key,str) or not current_candidate_key.strip():
        return RejectionSelection((),(),(),(),"invalid_rejection","Current suggestion identity invalid; rejection cannot be recorded.")
    if not isinstance(candidates,(tuple,list)) or any(not isinstance(c,AlternativeCandidate) for c in candidates):
        return RejectionSelection((),(),(),(),"invalid_candidates","Candidate list invalid; fail closed.")
    prior_ids=tuple(x for x in rejected_ids if isinstance(x,str) and x.strip()) if isinstance(rejected_ids,(tuple,list)) else ()
    prior_keys=tuple(x for x in rejected_keys if isinstance(x,str) and x.strip()) if isinstance(rejected_keys,(tuple,list)) else ()
    new_ids=tuple(dict.fromkeys((*prior_ids,current_suggestion_id.strip())))
    new_keys=tuple(dict.fromkeys((*prior_keys,current_candidate_key.strip())))
    excluded=[]
    eligible=[]
    seen_ids=set()
    seen_keys=set()
    for c in candidates:
        if c.suggestion_id in seen_ids or c.candidate_key in seen_keys:
            return RejectionSelection(new_ids,new_keys,(),tuple(excluded),"duplicate_candidate_identity","Duplicate candidate identity/fingerprint; reconcile.")
        seen_ids.add(c.suggestion_id);seen_keys.add(c.candidate_key)
        if c.suggestion_id in new_ids or c.candidate_key in new_keys:
            excluded.append((c.suggestion_id,"Previously rejected suggestion identity or candidate key; cannot be active again."))
        elif not c.valid:
            excluded.append((c.suggestion_id,c.reason or "Candidate not technically valid; excluded."))
        elif not c.evidence_refs:
            excluded.append((c.suggestion_id,"Evidence references missing; excluded."))
        else:
            eligible.append(c)
    eligible.sort(key=lambda c:c.rank)
    if len(eligible)>MAX_ALTERNATIVES:
        return RejectionSelection(new_ids,new_keys,(),tuple(excluded),"too_many_alternatives","More than three valid alternatives; refine criteria rather than truncating.")
    if not eligible:
        return RejectionSelection(new_ids,new_keys,(),tuple(excluded),"no_valid_alternatives","Rejected suggestion stays rejected; no valid alternative is available.")
    return RejectionSelection(new_ids,new_keys,tuple(eligible),tuple(excluded),"alternatives_ready_for_review",
        "Rejected suggestion is traceable and excluded; only evidence-backed valid alternatives are returned. No execution consent implied.")
