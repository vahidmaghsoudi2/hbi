"""Client target-color preference model; not feasibility or formula advice."""
from __future__ import annotations
from dataclasses import dataclass

TARGET_DIMENSIONS=("depth","color_family","tone_direction","intensity","warmth_coolness","maintenance")
PRIORITIES=("goal_match","hair_condition","low_maintenance","time","cost","avoid_damage","uniformity","contrast")
@dataclass(frozen=True)
class TargetColorPreference:
    target_description:str
    preferred_dimensions:dict[str,str]
    priorities:tuple[str,...]
    unacceptable_outcomes:tuple[str,...]
    reference_description:str|None
    maintenance_expectation:str|None
    source:str="client_reported"
    status:str="clear_for_review"

@dataclass(frozen=True)
class TargetAssessment:
    missing:tuple[str,...]
    unknown_dimensions:tuple[str,...]
    invalid_priorities:tuple[str,...]
    status:str
    message:str

def assess_target(target_description:object, preferred_dimensions:object=None, priorities:object=None, unacceptable_outcomes:object=(), reference_description:object=None, maintenance_expectation:object=None)->TargetAssessment:
    missing=[]
    if not isinstance(target_description,str) or not target_description.strip():
        missing.append("target_description")
    if not isinstance(priorities,(tuple,list)) or not priorities:
        missing.append("priorities")
    dims=preferred_dimensions if isinstance(preferred_dimensions,dict) else {}
    unknown=tuple(k for k in TARGET_DIMENSIONS if not isinstance(dims.get(k),str) or not dims.get(k).strip())
    invalid=tuple(p for p in (priorities if isinstance(priorities,(tuple,list)) else ()) if p not in PRIORITIES)
    if invalid:
        return TargetAssessment(tuple(missing),unknown,invalid,"needs_clarification","Priority entries are invalid; clarify rather than reinterpret.")
    if missing:
        return TargetAssessment(tuple(missing),unknown,invalid,"needs_clarification","Target or priorities are missing; ask the client to clarify.")
    if unknown:
        return TargetAssessment(tuple(missing),unknown,invalid,"partial_target","Target is described but some dimensions remain unspecified; do not fill them by assumption.")
    return TargetAssessment(tuple(missing),unknown,invalid,"target_recorded_for_review","Client preference is captured only; technical feasibility and outcome remain unevaluated.")
