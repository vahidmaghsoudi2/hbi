"""Claim evidence audit gate; classifies traceability without inventing support."""
from __future__ import annotations
from dataclasses import dataclass

CLAIM_TYPES=("owner_defined","catalog_identity","general_scientific","product_specific","specialist_rule","anecdotal")
SOURCE_TYPES=("owner_decision","catalog_snapshot","official_document","scientific_source","specialist_review","social_observation")

@dataclass(frozen=True)
class EvidenceAuditInput:
    rule_id: str
    claim_type: str
    source_type: str
    evidence_ref: str
    exact_product_identity: bool=False
    specialist_approved: bool=False
    source_quality: str="unknown"

@dataclass(frozen=True)
class EvidenceAuditResult:
    rule_id: str
    status: str
    claim_allowed: bool
    evidence_ref: str
    limitation: str

def audit_rule_evidence(item: object)->EvidenceAuditResult:
    if not isinstance(item,EvidenceAuditInput):
        return EvidenceAuditResult("","invalid_input",False,"","Evidence record invalid; claim blocked.")
    if item.claim_type not in CLAIM_TYPES or item.source_type not in SOURCE_TYPES or not item.rule_id:
        return EvidenceAuditResult(item.rule_id,"invalid_record",False,item.evidence_ref,"Claim type/source invalid; claim blocked.")
    ref=item.evidence_ref.strip() if isinstance(item.evidence_ref,str) else ""
    if not ref:
        return EvidenceAuditResult(item.rule_id,"evidence_pending",False,"","No traceable reference; claim blocked.")
    if item.claim_type=="owner_defined":
        if item.source_type=="owner_decision":
            return EvidenceAuditResult(item.rule_id,"owner_defined_not_scientific",True,ref,"Owner decision only; does not support scientific/chemical claims.")
        return EvidenceAuditResult(item.rule_id,"source_mismatch",False,ref,"Owner-defined rule requires owner decision trace.")
    if item.claim_type=="catalog_identity":
        if item.source_type=="catalog_snapshot":
            return EvidenceAuditResult(item.rule_id,"identity_only",True,ref,"Catalog identity/label only; no chemistry or performance claim.")
        return EvidenceAuditResult(item.rule_id,"source_mismatch",False,ref,"Catalog identity requires catalog evidence.")
    if item.claim_type=="anecdotal":
        return EvidenceAuditResult(item.rule_id,"anecdotal_signal_only",False,ref,"Anecdote is a signal only, not a generalized rule.")
    if item.claim_type=="product_specific":
        if not item.exact_product_identity or item.source_type!="official_document":
            return EvidenceAuditResult(item.rule_id,"product_evidence_pending",False,ref,"Exact product identity and official evidence are required; claim blocked.")
        if item.source_quality!="high":
            return EvidenceAuditResult(item.rule_id,"product_evidence_quality_unverified",False,ref,"Official source quality/identity is not established; claim blocked.")
        if not item.specialist_approved:
            return EvidenceAuditResult(item.rule_id,"awaiting_specialist_review",False,ref,"Evidence is traceable but specialist review is pending.")
        return EvidenceAuditResult(item.rule_id,"supported_for_review",True,ref,"Product-specific claim is evidence-backed for review, not execution authorization.")
    if item.claim_type=="general_scientific":
        if item.source_type not in ("scientific_source","official_document") or item.source_quality!="high":
            return EvidenceAuditResult(item.rule_id,"evidence_quality_unverified",False,ref,"Credible scientific/official source quality is not established; claim blocked.")
        if not item.specialist_approved:
            return EvidenceAuditResult(item.rule_id,"awaiting_specialist_review",False,ref,"Source is traceable; specialist review pending.")
        return EvidenceAuditResult(item.rule_id,"supported_for_review",True,ref,"General scientific claim supported for specialist review; scope limits remain.")
    if item.claim_type=="specialist_rule":
        if item.source_type!="specialist_review" or not item.specialist_approved:
            return EvidenceAuditResult(item.rule_id,"awaiting_specialist_review",False,ref,"Specialist rule requires explicit review record and approval.")
        if item.source_quality!="high":
            return EvidenceAuditResult(item.rule_id,"evidence_quality_unverified",False,ref,"Evidence quality not established; claim blocked.")
        return EvidenceAuditResult(item.rule_id,"supported_for_review",True,ref,"Specialist rule traceable and reviewed; owner/product acceptance still separate.")
    return EvidenceAuditResult(item.rule_id,"evidence_pending",False,ref,"Claim blocked pending appropriate evidence.")
