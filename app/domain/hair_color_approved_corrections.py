"""Guarded correction application workflow; never invent or apply pending corrections."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CorrectionProposal:
    correction_id: str
    topic_id: str
    description: str
    specialist_record_ref: str
    evidence_refs: tuple[str,...]
    specialist_accepted_within_scope: bool
    po_approved: bool
    po_approval_ref: str
    baseline_version: str
    target_version: str
    scope_note: str
    apply_receipt: str=""

@dataclass(frozen=True)
class CorrectionResult:
    status: str
    correction_id: str
    baseline_version: str
    target_version: str
    message: str

def assess_correction(proposal: object)->CorrectionResult:
    if not isinstance(proposal,CorrectionProposal):
        return CorrectionResult("invalid_proposal","","","","Proposal invalid; no correction applied.")
    if not proposal.correction_id or not proposal.topic_id or not proposal.description or not proposal.specialist_record_ref or not proposal.evidence_refs or not proposal.scope_note:
        return CorrectionResult("incomplete_proposal",proposal.correction_id,proposal.baseline_version,proposal.target_version,"Correction requires topic, description, specialist record, evidence, and scope.")
    if not proposal.specialist_accepted_within_scope:
        return CorrectionResult("pending_specialist_review",proposal.correction_id,proposal.baseline_version,proposal.target_version,"Specialist acceptance within scope missing; correction blocked.")
    if not proposal.po_approved or not proposal.po_approval_ref:
        return CorrectionResult("pending_PO_approval",proposal.correction_id,proposal.baseline_version,proposal.target_version,"PO approval/reference missing; correction blocked.")
    if not proposal.baseline_version or not proposal.target_version or proposal.baseline_version==proposal.target_version:
        return CorrectionResult("invalid_version_change",proposal.correction_id,proposal.baseline_version,proposal.target_version,"Correction must record distinct baseline and target versions.")
    if proposal.apply_receipt:
        return CorrectionResult("applied_with_trace",proposal.correction_id,proposal.baseline_version,proposal.target_version,"Applied state is traceable to receipt; this validator does not independently verify the receipt.")
    return CorrectionResult("approved_ready_to_apply",proposal.correction_id,proposal.baseline_version,proposal.target_version,"Approvals and version scope are present; actual application/receipt remains pending.")
