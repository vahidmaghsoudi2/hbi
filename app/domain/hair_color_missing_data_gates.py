"""Required-data matrix with source/confidence/conflict gates."""
from __future__ import annotations
from dataclasses import dataclass

GENERIC_REQUIRED=("goal.target_color","goal.priority","current.base_level","current.color_condition",
    "history.color_services","history.chemical_services","regional.map","safety.screen","context.constraints")
PRODUCT_SPECIFIC_REQUIRED=("product.identity","product.evidence")

@dataclass(frozen=True)
class DataEntry:
    field_id: str
    value: str
    source: str
    confidence: str
    conflicts: tuple[str,...]=()

@dataclass(frozen=True)
class DataCompleteness:
    status: str
    missing_required: tuple[str,...]
    uncertain_fields: tuple[str,...]
    conflict_fields: tuple[str,...]
    required_fields: tuple[str,...]
    message: str

def make_data_entry(field_id: object,value: object,source: object,confidence: object,conflicts: object=())->DataEntry|None:
    allowed_sources=("client_reported","professional_observed","documented","image_only","unknown")
    allowed_confidence=("high","medium","low","unknown")
    if not isinstance(field_id,str) or not field_id.strip() or not isinstance(value,str) or not isinstance(source,str) or source not in allowed_sources or not isinstance(confidence,str) or confidence not in allowed_confidence:return None
    if not value.strip():return None
    c=tuple(x.strip() for x in conflicts if isinstance(x,str) and x.strip()) if isinstance(conflicts,(tuple,list)) else ()
    return DataEntry(field_id.strip(),value.strip(),source,confidence,c)

def assess_data_completeness(entries: object,claim_type: object="generic")->DataCompleteness:
    if claim_type not in ("generic","product_specific"):
        return DataCompleteness("invalid_claim_type",(),(),(),(),"Claim type invalid; fail closed.")
    required=GENERIC_REQUIRED+(PRODUCT_SPECIFIC_REQUIRED if claim_type=="product_specific" else ())
    if not isinstance(entries,(tuple,list)) or any(not isinstance(e,DataEntry) for e in entries):
        return DataCompleteness("invalid_entries",required,(),(),required,"Data-entry structure invalid; no dependent advice.")
    by_id={}
    for e in entries:
        if e.field_id in by_id:
            return DataCompleteness("duplicate_fields",(),(),(e.field_id,),required,"Duplicate field records; reconcile.")
        by_id[e.field_id]=e
    missing=tuple(f for f in required if f not in by_id or by_id[f].value.lower() in ("unknown","not known","n/a"))
    uncertain=tuple(f for f in required if f in by_id and (by_id[f].source in ("unknown","image_only") or by_id[f].confidence in ("low","unknown")))
    conflicts=tuple(f for f in required if f in by_id and by_id[f].conflicts)
    if conflicts:
        return DataCompleteness("conflict_review",missing,uncertain,conflicts,required,"Conflicts in required data must be reconciled before dependent review.")
    if missing:
        return DataCompleteness("needs_more_information",missing,uncertain,(),required,"Required information missing/unknown; no definitive personalized advice.")
    if uncertain:
        return DataCompleteness("limited_review",(),uncertain,(),required,"Data recorded but uncertain; limited review only and confirm decision-relevant fields.")
    return DataCompleteness("data_complete_for_review",(),(),(),required,"Completeness only; technical feasibility and recommendation validity remain unevaluated.")
