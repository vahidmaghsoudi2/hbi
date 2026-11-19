"""Intake checklist and completeness gate, not a recommendation engine."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class InputGroup(str, Enum):
    GOAL="goal"; CURRENT="current_hair_state"; HISTORY="service_history"
    REGIONAL="regional_differences"; SAFETY="safety_screen"; CONTEXT="context"; PRODUCT="product_identity"

class EvidenceQuality(str, Enum):
    CLIENT_REPORTED="client_reported"; PROFESSIONAL_OBSERVED="professional_observed"
    DOCUMENTED="documented"; IMAGE_ONLY="image_only"; UNKNOWN="unknown"

@dataclass(frozen=True)
class ConsultationInput:
    input_id: str
    label: str
    group: InputGroup
    required_for_initial_review: bool
    purpose: str
    accepted_sources: tuple[str,...]
    limitation: str

INPUTS=(
 ConsultationInput("goal.target_color","Target color and desired direction",InputGroup.GOAL,True,"Clarify the requested outcome.",("client_reported",),"Reference images express preference, not guaranteed feasibility."),
 ConsultationInput("goal.priority","Priorities and trade-offs",InputGroup.GOAL,True,"Resolve competing goals.",("client_reported",),"Do not assume priorities."),
 ConsultationInput("current.base_level","Current base/depth estimate",InputGroup.CURRENT,True,"Describe current color state.",("professional_observed","client_reported","image_only"),"Image-only estimate is uncertain; no exact pigment inference."),
 ConsultationInput("current.color_condition","Current color condition by region",InputGroup.REGIONAL,True,"Record regional differences.",("professional_observed","client_reported","image_only"),"Image does not establish history, porosity or structure."),
 ConsultationInput("history.color_services","Previous color services/products",InputGroup.HISTORY,True,"Record known history.",("client_reported","documented"),"Unknown history remains unknown."),
 ConsultationInput("history.chemical_services","Other relevant chemical services",InputGroup.HISTORY,True,"Identify compatibility questions.",("client_reported","documented"),"Unresolved compatibility holds dependent advice."),
 ConsultationInput("regional.map","Region-by-region hair map",InputGroup.REGIONAL,True,"Record roots, mid-lengths and ends where different.",("professional_observed","client_reported","image_only"),"Do not collapse distinct regions."),
 ConsultationInput("safety.screen","Safety concerns/reaction history",InputGroup.SAFETY,True,"Identify stop or review needs.",("client_reported","documented"),"Screening, not diagnosis; follow official instructions and professional review."),
 ConsultationInput("context.constraints","Service context and constraints",InputGroup.CONTEXT,True,"Record maintenance, time and scope constraints.",("client_reported",),"Constraints do not override feasibility or safety."),
 ConsultationInput("product.identity","Exact product identity for product-specific claims",InputGroup.PRODUCT,False,"Trace product, shade, market/version and documents.",("documented","client_reported"),"Brand or shade code alone is not chemistry evidence."),
)

@dataclass(frozen=True)
class IntakeAssessment:
    missing_required: tuple[str,...]
    uncertain: tuple[str,...]
    readiness: str
    message: str

def assess_intake(values: dict[str,object]) -> IntakeAssessment:
    missing=tuple(i.input_id for i in INPUTS if i.required_for_initial_review and values.get(i.input_id) in (None,"","unknown"))
    uncertain=tuple(i.input_id for i in INPUTS if values.get(i.input_id)=="image_only")
    if missing:
        return IntakeAssessment(missing,uncertain,"needs_more_information","Required inputs missing; no definitive personalized recommendation.")
    if uncertain:
        return IntakeAssessment(missing,uncertain,"limited_review","Image-only data are uncertain; confirm/observe decision-relevant fields.")
    return IntakeAssessment(missing,uncertain,"intake_complete_for_review","Completeness only; not feasibility, advice approval, or execution authorization.")

def get_input(input_id: str):
    if not isinstance(input_id,str): return None
    return next((i for i in INPUTS if i.input_id==input_id),None)
