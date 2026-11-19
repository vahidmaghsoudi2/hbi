"""Specialist hair-color scenario coverage templates; no chemical outcome oracles invented."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SpecialistScenario:
    scenario_id: str
    title: str
    required_fields: tuple[str,...]
    expected_gate: str
    technical_oracle_status: str = "specialist_review_pending"

SCENARIOS=(
    SpecialistScenario("HC-S01","Regional unevenness",("regional_state","image_quality"),"Keep regions separate; request missing region data."),
    SpecialistScenario("HC-S02","Unknown service history",("service_history",),"History remains unknown; no compatibility inference."),
    SpecialistScenario("HC-S03","Known lightening history",("service_history","product_identity"),"Capture provenance; do not infer exact chemistry or outcome."),
    SpecialistScenario("HC-S04","Plant-dye or henna product uncertainty",("service_history","product_identity"),"Unknown product chemistry remains knowledge gap; stop dependent claim."),
    SpecialistScenario("HC-S05","Chemical smoothing or structure service",("service_history","safety"),"Capture service and safety context; no compatibility assumption."),
    SpecialistScenario("HC-S06","Ambitious or multi-session target",("target","current_base","regional_state"),"Record target and current state separately; no guaranteed outcome."),
    SpecialistScenario("HC-S07","Unidentified product/catalog item",("product_identity","product_evidence"),"No product-specific claim without exact identity and evidence."),
    SpecialistScenario("HC-S08","Safety reaction or required test concern",("safety","product_evidence"),"Safety stop; no execution-oriented recommendation."),
    SpecialistScenario("HC-S09","Conflicting client and observation data",("conflict","regional_state"),"Conflict review; dependent evaluation blocked."),
    SpecialistScenario("HC-S10","Reference photo only",("target","image_quality"),"Image is preference reference, not proof of current base or result."),
    SpecialistScenario("HC-S11","Ambiguous target-family wording",("target",),"Clarify; no fuzzy family mapping."),
    SpecialistScenario("HC-S12","Image quality insufficient",("image_quality","regional_state"),"Mark image non-evaluable; request new capture or in-person review."),
)

@dataclass(frozen=True)
class ScenarioReadiness:
    scenario_id: str
    status: str
    missing_fields: tuple[str,...]
    evidence_refs: tuple[str,...]
    message: str

def scenario_catalog()->tuple[SpecialistScenario,...]:
    return SCENARIOS

def assess_scenario(scenario_id: object,supplied_fields: object,
                    specialist_oracle_approved: object=False,evidence_refs: object=())->ScenarioReadiness:
    scenario=next((s for s in SCENARIOS if s.scenario_id==scenario_id),None)
    if scenario is None:
        return ScenarioReadiness(str(scenario_id),"unknown_scenario",(),(),"Unknown scenario; no technical assumption.")
    if not isinstance(supplied_fields,(tuple,list)) or any(not isinstance(x,str) for x in supplied_fields):
        return ScenarioReadiness(scenario.scenario_id,"invalid_fields",scenario.required_fields,(), "Scenario fields invalid; fail closed.")
    missing=tuple(x for x in scenario.required_fields if x not in supplied_fields)
    refs=tuple(x.strip() for x in evidence_refs if isinstance(x,str) and x.strip()) if isinstance(evidence_refs,(tuple,list)) else ()
    if missing:
        return ScenarioReadiness(scenario.scenario_id,"needs_case_data",missing,refs,"Required scenario facts missing; request only those facts.")
    if specialist_oracle_approved is not True:
        return ScenarioReadiness(scenario.scenario_id,"specialist_oracle_pending",(),refs,"Scenario behavior is a control expectation only; specialist oracle remains pending.")
    if not refs:
        return ScenarioReadiness(scenario.scenario_id,"evidence_missing",(),(),"Specialist approval must be traceable to evidence; no test oracle is accepted without references.")
    return ScenarioReadiness(scenario.scenario_id,"ready_for_specialist_test",(),refs,"Ready to be evaluated against a specialist-approved, evidence-backed oracle; no oracle content is invented.")
