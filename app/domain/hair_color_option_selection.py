"""Evidence-gated selection of one to three options; never invent or rank candidates."""
from __future__ import annotations
from dataclasses import dataclass
from app.domain.hair_catalog_families import known_catalog_family_labels

KNOWN_FAMILIES = known_catalog_family_labels()
MAX_OPTIONS = 3

@dataclass(frozen=True)
class EvaluatedOption:
    option_id: str
    family_label: str
    rank: int
    validity: str
    evidence_refs: tuple[str, ...]
    goal_fit_basis: str
    limitations: tuple[str, ...] = ()
    exclusion_reason: str = ""

@dataclass(frozen=True)
class OptionSelection:
    selected: tuple[EvaluatedOption, ...]
    excluded: tuple[tuple[str, str], ...]
    status: str
    message: str

def make_evaluated_option(option_id: object, family_label: object, rank: object,
                          validity: object, evidence_refs: object, goal_fit_basis: object,
                          limitations: object = (), exclusion_reason: object = "") -> EvaluatedOption | None:
    if not isinstance(option_id, str) or not option_id.strip():
        return None
    if not isinstance(family_label, str) or family_label not in KNOWN_FAMILIES:
        return None
    if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
        return None
    if validity not in ("validated", "unvalidated", "rejected"):
        return None
    refs = tuple(x.strip() for x in evidence_refs if isinstance(x, str) and x.strip()) if isinstance(evidence_refs, (tuple, list)) else ()
    lim = tuple(x.strip() for x in limitations if isinstance(x, str) and x.strip()) if isinstance(limitations, (tuple, list)) else ()
    basis = goal_fit_basis.strip() if isinstance(goal_fit_basis, str) else ""
    reason = exclusion_reason.strip() if isinstance(exclusion_reason, str) else ""
    return EvaluatedOption(option_id.strip(), family_label, rank, validity, refs, basis, lim, reason)

def select_reviewable_options(candidates: object) -> OptionSelection:
    if not isinstance(candidates, (tuple, list)):
        return OptionSelection((), (), "invalid_candidates", "Candidates must be an explicit list; no options are emitted.")
    if not candidates:
        return OptionSelection((), (), "no_candidates", "No candidate options supplied; do not fabricate alternatives.")
    if any(not isinstance(c, EvaluatedOption) for c in candidates):
        return OptionSelection((), (), "invalid_candidates", "Candidate structure invalid; fail closed.")
    ids = [c.option_id for c in candidates]
    if len(set(ids)) != len(ids):
        return OptionSelection((), (), "duplicate_option_ids", "Duplicate option IDs detected; resolve before selection.")
    families = [c.family_label for c in candidates]
    if len(set(families)) != len(families):
        return OptionSelection((), (), "duplicate_families", "Duplicate family candidates detected; consolidate before selection.")
    excluded=[]
    valid=[]
    for c in candidates:
        if c.validity == "rejected":
            excluded.append((c.option_id, c.exclusion_reason or "Rejected by evaluation; not offered."))
        elif c.validity != "validated":
            excluded.append((c.option_id, "Not technically validated; not offered as a valid option."))
        elif not c.evidence_refs:
            excluded.append((c.option_id, "Validation lacks traceable evidence references; not offered."))
        elif not c.goal_fit_basis:
            excluded.append((c.option_id, "Goal-fit basis is missing; not ranked or offered."))
        else:
            valid.append(c)
    if not valid:
        return OptionSelection((), tuple(excluded), "no_valid_options", "No evidence-backed valid options remain; request review or additional evidence.")
    ranks=[c.rank for c in valid]
    if len(set(ranks)) != len(ranks):
        return OptionSelection((), tuple(excluded), "ranking_conflict", "Valid candidates have duplicate ranks; resolve ranking before presenting options.")
    valid.sort(key=lambda c:c.rank)
    if len(valid)>MAX_OPTIONS:
        return OptionSelection((), tuple(excluded), "too_many_valid_options", "More than three valid options remain; refine with documented criteria rather than silently truncating.")
    return OptionSelection(tuple(valid), tuple(excluded), "options_ready_for_review",
        "Only evidence-backed, technically validated candidates are selected; ordering uses supplied rank. Specialist review remains required.")
