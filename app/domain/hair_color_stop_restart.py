"""Client-requested consultation stop and explicit fresh restart gate."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class StopRecord:
    stop_request_id: str
    case_version: str
    suggestion_id: str
    performed_steps: tuple[str,...]
    status: str
    auto_resume: bool
    prior_decisions_invalidated: bool
    message: str

@dataclass(frozen=True)
class RestartGate:
    allowed: bool
    old_version: str
    new_version: str
    missing_checks: tuple[str,...]
    message: str

def record_stop_request(request_id: object,case_version: object,suggestion_id: object,
                        performed_steps: object)->StopRecord|None:
    if not all(isinstance(x,str) and x.strip() for x in (request_id,case_version,suggestion_id)):
        return None
    if not isinstance(performed_steps,(tuple,list)) or any(not isinstance(x,str) or not x.strip() for x in performed_steps):
        return None
    steps=tuple(dict.fromkeys(x.strip() for x in performed_steps))
    return StopRecord(request_id.strip(),case_version.strip(),suggestion_id.strip(),steps,
        "consultation_stopped_by_client",False,True,
        "Stop request recorded. Only supplied performed steps are recorded; no automatic resume. Dependent prior decisions are invalidated.")

def assess_restart_after_stop(old_version: object,new_version: object,fresh_hair_state: object,
                             fresh_data: object,fresh_safety: object,fresh_rules: object,
                             fresh_evidence: object,restart_authorized: object)->RestartGate:
    if not isinstance(old_version,str) or not old_version.strip() or not isinstance(new_version,str) or not new_version.strip() or old_version==new_version:
        return RestartGate(False,"","",(),"A distinct new case version is required; old path is not resumed.")
    checks={"fresh_hair_state":fresh_hair_state,"fresh_data":fresh_data,"fresh_safety":fresh_safety,
            "fresh_rules":fresh_rules,"fresh_evidence":fresh_evidence,"restart_authorized":restart_authorized}
    missing=tuple(k for k,v in checks.items() if v is not True)
    if missing:
        return RestartGate(False,old_version,new_version,missing,
            "Restart blocked; all fresh evaluation inputs and explicit authorization are required.")
    return RestartGate(True,old_version,new_version,(),
        "Fresh evaluation may start under the new version. Old path, acceptance, consent, and specialist review are not resumed.")
