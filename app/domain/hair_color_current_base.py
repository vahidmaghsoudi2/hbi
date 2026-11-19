"""Conservative current-base description for synthetic hair-color cases.

Depth is a working descriptive scale, not a formula/result predictor. Do not
infer depth, artificial history, pigment, or chemical condition from an image.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class BaseEvidence(str,Enum):
    OBSERVED="professional_observed"
    CLIENT="client_reported"
    IMAGE="image_only"
    DOCUMENTED="documented"
    UNKNOWN="unknown"

LEVEL_LABELS={
 1:"black",
 2:"very_dark_brown",
 3:"dark_brown",
 4:"medium_brown",
 5:"light_brown",
 6:"dark_blonde",
 7:"medium_blonde",
 8:"light_blonde",
 9:"very_light_blonde",
 10:"lightest_blonde",
}

@dataclass(frozen=True)
class CurrentBase:
    region:str
    level:int|None
    label:str|None
    evidence:BaseEvidence
    confidence:str
    raw_description:str|None
    notes:str
    status:str

def describe_current_base(region:str, level:object, evidence:object, confidence:object="unknown", raw_description:object=None, notes:object="")->CurrentBase|None:
    if not isinstance(region,str) or not region.strip():
        return None
    try:
        source=BaseEvidence(evidence)
    except (ValueError,TypeError):
        return None
    valid_level=level if isinstance(level,int) and not isinstance(level,bool) and level in LEVEL_LABELS else None
    valid_confidence=confidence if confidence in ("low","medium","high","unknown") else "unknown"
    desc=raw_description if isinstance(raw_description,str) else None
    note=notes if isinstance(notes,str) else ""
    if source in (BaseEvidence.IMAGE,BaseEvidence.UNKNOWN) or valid_level is None or valid_confidence in ("low","unknown"):
        status="uncertain_review"
    else:
        status="descriptive_only"
    return CurrentBase(region,valid_level,LEVEL_LABELS.get(valid_level),source,valid_confidence,desc,note,status)

def level_label(level:object)->str|None:
    if isinstance(level,bool) or not isinstance(level,int):
        return None
    return LEVEL_LABELS.get(level)
