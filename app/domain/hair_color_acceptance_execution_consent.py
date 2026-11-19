"""Separate client acceptance from explicit execution consent; version-scoped."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Acceptance(str,Enum):
    PENDING="pending"
    ACCEPTED="accepted"
    REJECTED="rejected"

class Consent(str,Enum):
    PENDING="pending"
    GRANTED="granted"
    WITHHELD="withheld"

@dataclass(frozen=True)
class DecisionRecord:
    case_version: str
    suggestion_id: str
    acceptance: Acceptance = Acceptance.PENDING
    execution_consent: Consent = Consent.PENDING

@dataclass(frozen=True)
class DecisionResult:
    record: DecisionRecord | None
    status: str
    message: str

@dataclass(frozen=True)
class ExecutionGate:
    authorized: bool
    reason: str

def new_decision_record(case_version: object,suggestion_id: object)->DecisionRecord|None:
    if not isinstance(case_version,str) or not case_version.strip() or not isinstance(suggestion_id,str) or not suggestion_id.strip():
        return None
    return DecisionRecord(case_version.strip(),suggestion_id.strip())

def record_acceptance(record: object,decision: object,case_version: object,suggestion_id: object)->DecisionResult:
    if not isinstance(record,DecisionRecord):
        return DecisionResult(None,"invalid_record","Decision record invalid.")
    if record.case_version!=case_version or record.suggestion_id!=suggestion_id:
        return DecisionResult(None,"stale_version_or_suggestion","Acceptance is bound to a different case version/suggestion.")
    if decision not in ("accepted","rejected"):
        return DecisionResult(None,"invalid_acceptance","Explicit accepted/rejected event required.")
    updated=DecisionRecord(record.case_version,record.suggestion_id,Acceptance(decision),Consent.PENDING)
    return DecisionResult(updated,decision,"Acceptance recorded separately; execution consent remains pending.")

def record_execution_consent(record: object,consent: object,case_version: object,suggestion_id: object)->DecisionResult:
    if not isinstance(record,DecisionRecord):
        return DecisionResult(None,"invalid_record","Decision record invalid.")
    if record.case_version!=case_version or record.suggestion_id!=suggestion_id:
        return DecisionResult(None,"stale_version_or_suggestion","Consent is bound to a different case version/suggestion.")
    if record.acceptance!=Acceptance.ACCEPTED:
        return DecisionResult(None,"acceptance_required","Execution consent cannot be recorded until the specific suggestion is accepted.")
    if consent not in ("granted","withheld"):
        return DecisionResult(None,"invalid_consent","Explicit granted/withheld consent event required.")
    updated=DecisionRecord(record.case_version,record.suggestion_id,record.acceptance,Consent(consent))
    return DecisionResult(updated,consent,"Execution consent recorded as a separate event.")

def evaluate_execution_gate(record: object,specialist_approved: object,valid_candidate: object,safety_stop: object)->ExecutionGate:
    if not isinstance(record,DecisionRecord):
        return ExecutionGate(False,"Invalid decision record.")
    if not all(isinstance(x,bool) for x in (specialist_approved,valid_candidate,safety_stop)):
        return ExecutionGate(False,"Invalid authorization facts.")
    if safety_stop:
        return ExecutionGate(False,"Safety stop blocks execution.")
    if not valid_candidate:
        return ExecutionGate(False,"Candidate validity is not established.")
    if not specialist_approved:
        return ExecutionGate(False,"Specialist approval is missing.")
    if record.acceptance!=Acceptance.ACCEPTED:
        return ExecutionGate(False,"Specific suggestion acceptance is missing.")
    if record.execution_consent!=Consent.GRANTED:
        return ExecutionGate(False,"Separate explicit execution consent is missing or withheld.")
    return ExecutionGate(True,"All separate gates satisfied; execution authorization still must be recorded in workflow.")
