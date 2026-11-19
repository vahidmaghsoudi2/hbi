"""Hair/service history capture. Unknown history is not inferred or defaulted."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ServiceType(str,Enum):
    COLOR="color"
    LIGHTENING="lightening"
    BLEACH="bleach"
    TONER="toner"
    DIRECT_DYE="direct_dye"
    PLANT_DYE="plant_dye"
    PERM_OR_RELAXER="perm_or_relaxer"
    KERATIN_OR_SMOOTHING="keratin_or_smoothing"
    OTHER_CHEMICAL="other_chemical"
    HOME_APPLICATION="home_application"
    NONE_REPORTED="none_reported"
    UNKNOWN="unknown"

class HistorySource(str,Enum):
    CLIENT="client_reported"
    DOCUMENT="documented"
    PROFESSIONAL="professional_observed"
    UNKNOWN="unknown"

@dataclass(frozen=True)
class ServiceHistoryEntry:
    service_type:ServiceType
    date_or_period:str|None
    product_brand:str|None
    product_name_or_shade:str|None
    market_or_version:str|None
    source:HistorySource
    certainty:str
    affected_regions:tuple[str,...]
    notes:str

@dataclass(frozen=True)
class HistoryAssessment:
    status:str
    unknown_fields:tuple[str,...]
    conflicts:tuple[str,...]
    message:str

def assess_history(entries:object, declared_history:str|None, conflicts:tuple[str,...]=())->HistoryAssessment:
    if declared_history not in ("known_history","none_reported","unknown_history"):
        return HistoryAssessment("needs_clarification",("declared_history",),tuple(conflicts),"Clarify whether history is known, none reported, or unknown.")
    if declared_history=="unknown_history":
        return HistoryAssessment("history_unknown",("history",),tuple(conflicts),"History is unknown; do not infer or treat as no prior services.")
    if declared_history=="none_reported":
        if entries not in ((),[],None):
            return HistoryAssessment("conflict_review",(),("entries_present_with_none_reported",),"Conflict between no-history statement and recorded entries; reconcile before dependent evaluation.")
        if conflicts:
            return HistoryAssessment("conflict_review",(),tuple(conflicts),"Reported history has unresolved conflicts; reconcile.")
        return HistoryAssessment("no_history_reported",(),(),"No prior services reported; this is client history, not independent verification.")
    if not isinstance(entries,(tuple,list)) or not entries:
        return HistoryAssessment("history_incomplete",("service_entries",),tuple(conflicts),"Known history declared but entries are missing; request details.")
    if conflicts:
        return HistoryAssessment("conflict_review",(),tuple(conflicts),"History conflicts are unresolved; dependent assessment requires reconciliation.")
    if any(not isinstance(e,ServiceHistoryEntry) for e in entries):
        return HistoryAssessment("invalid_entries",("service_entries",),(),"Invalid history entry structure; do not use.")
    incomplete=tuple(f"entry_{i}" for i,e in enumerate(entries) if not e.service_type or not e.source or e.certainty not in ("confirmed","approximate","uncertain"))
    if incomplete:
        return HistoryAssessment("history_incomplete",incomplete,(),"Some service records lack valid source/certainty; clarify before using dependent claims.")
    return HistoryAssessment("history_recorded",(),(),"History captured with source and certainty; not chemical compatibility or outcome evidence.")

def make_history_entry(service_type:object,date_or_period:object=None,product_brand:object=None,product_name_or_shade:object=None,market_or_version:object=None,source:object="unknown",certainty:object="uncertain",affected_regions:object=(),notes:object="")->ServiceHistoryEntry|None:
    try:
        kind=ServiceType(service_type); src=HistorySource(source)
    except (ValueError,TypeError):
        return None
    def text_or_none(v): return v if isinstance(v,str) else None
    regions=tuple(v for v in affected_regions if isinstance(v,str)) if isinstance(affected_regions,(tuple,list)) else ()
    return ServiceHistoryEntry(kind,text_or_none(date_or_period),text_or_none(product_brand),text_or_none(product_name_or_shade),text_or_none(market_or_version),src,certainty if certainty in ("confirmed","approximate","uncertain") else "uncertain",regions,text_or_none(notes) or "")
