"""Owner acceptance report status; PO decision deliberately remains unset."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AcceptanceCriterion:
    criterion_id: str
    title: str
    evidence_status: str
    recommendation: str
    acceptance_blocker: bool

CRITERIA=(
    AcceptanceCriterion("AC01","Architecture and state contracts","documented_not_merged","Reviewable documentation baseline",False),
    AcceptanceCriterion("AC02","Owner-defined rules and boundaries","recorded_scope_only","Confirm owner wording/scope; no scientific interpretation",False),
    AcceptanceCriterion("AC03","Catalog identity and labels","documented_identity_only","No chemistry/performance claims",False),
    AcceptanceCriterion("AC04","Specialist review","not_received","Pending real review records",True),
    AcceptanceCriterion("AC05","Evidence audit","classification_gate_written_not_run","No claims upgraded without source validation",True),
    AcceptanceCriterion("AC06","Tests and CI","not_executed_in_this_work_sequence","Execute tests/CI before implementation acceptance",True),
    AcceptanceCriterion("AC07","Runtime integration","not_verified","No runtime/DB/integration evidence",True),
    AcceptanceCriterion("AC08","Customer use and execution","not_authorized","Do not use as customer advice or execution authority",True),
    AcceptanceCriterion("AC09","Approved corrections","none_applied","No correction applied without specialist+PO approvals",False),
    AcceptanceCriterion("AC10","Draft PR chain","open_unmerged_drafts","Owner review and dependency strategy required",False),
)

@dataclass(frozen=True)
class OwnerAcceptanceReport:
    report_status: str
    criteria: tuple[AcceptanceCriterion,...]
    recommended_decision: str
    po_decision: str
    po_decision_ref: str
    blockers: tuple[str,...]
    message: str

def acceptance_criteria()->tuple[AcceptanceCriterion,...]:
    return CRITERIA

def owner_acceptance_report()->OwnerAcceptanceReport:
    blockers=tuple(c.criterion_id for c in CRITERIA if c.acceptance_blocker)
    return OwnerAcceptanceReport(
        "prepared_pending_PO_decision",
        CRITERIA,
        "accept_documentation_baseline_only_with_conditions",
        "pending",
        "",
        blockers,
        "Report prepared as decision support; no PO acceptance, production readiness, specialist validation, or customer-use approval is claimed.",
    )
