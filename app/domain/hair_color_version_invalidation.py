"""Versioning and dependency-based invalidation for changed consultation inputs."""
from __future__ import annotations
from dataclasses import dataclass

OUTPUTS=(
    "intake_readiness","target_assessment","current_base_assessment","regional_state_assessment",
    "service_history_assessment","safety_assessment","family_selection","feasibility",
    "candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"
)
DEPENDENCIES={
    "target_color":OUTPUTS,
    "current_base":("current_base_assessment","regional_state_assessment","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "regional_state":("regional_state_assessment","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "service_history":("service_history_assessment","safety_assessment","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "safety_screen":("safety_assessment","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "product_identity":("family_selection","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "product_evidence":("family_selection","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "priorities":("target_assessment","family_selection","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "maintenance_expectation":("target_assessment","family_selection","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
    "image_quality":("current_base_assessment","regional_state_assessment","feasibility","candidate_options","specialist_review","client_acceptance","execution_consent","execution_plan"),
}
@dataclass(frozen=True)
class InvalidationResult:
    status: str
    old_version: str
    new_version: str
    changed_items: tuple[str,...]
    invalidated_outputs: tuple[str,...]
    preserved_outputs: tuple[str,...]
    fresh_evaluation_required: bool
    fresh_specialist_review_required: bool
    decision_records_reset: tuple[str,...]
    message: str

def invalidate_for_change(old_version: object,new_version: object,changed_items: object,existing_outputs: object=OUTPUTS)->InvalidationResult:
    if not isinstance(old_version,str) or not old_version.strip() or not isinstance(new_version,str) or not new_version.strip() or old_version==new_version:
        return InvalidationResult("invalid_version","","",(),(),(),False,False,(),"Version must be explicit, non-empty, and changed.")
    if not isinstance(changed_items,(tuple,list)) or not changed_items or any(not isinstance(x,str) or not x for x in changed_items):
        return InvalidationResult("invalid_change_items",old_version,new_version,(),(),(),False,False,(),"At least one exact changed item is required.")
    if not isinstance(existing_outputs,(tuple,list)) or any(not isinstance(x,str) for x in existing_outputs):
        return InvalidationResult("invalid_outputs",old_version,new_version,tuple(changed_items),(),(),False,False,(),"Output inventory invalid; fail closed.")
    changed=tuple(dict.fromkeys(changed_items))
    unknown=tuple(x for x in changed if x not in DEPENDENCIES)
    target_change="target_color" in changed
    if target_change or unknown:
        invalidated=tuple(x for x in existing_outputs if x in OUTPUTS)
        status="target_changed_full_invalidation" if target_change else "unknown_dependency_full_invalidation"
        message="Target change requires fresh evaluation and invalidates affected prior decisions." if target_change else "Unknown dependency item; conservatively invalidate all known outputs and require fresh evaluation."
    else:
        affected=set()
        for item in changed: affected.update(DEPENDENCIES[item])
        invalidated=tuple(x for x in existing_outputs if x in affected)
        status="dependency_invalidation"
        message="Only dependent outputs invalidated; unaffected outputs preserved. Prior dependent specialist review, acceptance, and consent do not carry over."
    invalidated_set=set(invalidated)
    preserved=tuple(x for x in existing_outputs if x not in invalidated_set)
    decision_reset=tuple(x for x in ("specialist_review","client_acceptance","execution_consent") if x in invalidated_set)
    return InvalidationResult(status,old_version,new_version,changed,invalidated,preserved,
        bool(set(invalidated)&{"target_assessment","current_base_assessment","regional_state_assessment","service_history_assessment","safety_assessment","feasibility","candidate_options"}),
        "specialist_review" in invalidated_set,decision_reset,message)
