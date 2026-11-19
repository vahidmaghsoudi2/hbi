"""Reconcile specialist review records against inventory and evidence trace."""
from __future__ import annotations
from dataclasses import dataclass
from app.domain.hair_color_specialist_review_inventory import review_inventory
from app.domain.hair_color_specialist_review_record import SpecialistReviewRecord

@dataclass(frozen=True)
class TopicReconciliation:
    topic_id: str
    status: str
    review_record_refs: tuple[str,...]
    missing_evidence_refs: tuple[str,...]
    message: str

@dataclass(frozen=True)
class ReconciliationReport:
    status: str
    topics: tuple[TopicReconciliation,...]
    invalid_record_topics: tuple[str,...]
    duplicate_topic_ids: tuple[str,...]
    message: str

def reconcile_specialist_reviews(records: object,evidence_ledger: object)->ReconciliationReport:
    if not isinstance(records,(tuple,list)) or any(not isinstance(r,SpecialistReviewRecord) for r in records):
        return ReconciliationReport("invalid_records",(),(),(),"Review records malformed; reconciliation failed closed.")
    if not isinstance(evidence_ledger,dict) or any(not isinstance(k,str) or not isinstance(v,(tuple,list)) for k,v in evidence_ledger.items()):
        return ReconciliationReport("invalid_evidence_ledger",(),(),(),"Evidence ledger malformed; reconciliation failed closed.")
    inventory=review_inventory()
    valid_ids={t.topic_id for t in inventory}
    invalid=tuple(sorted({r.topic_id for r in records if r.topic_id not in valid_ids}))
    by_topic={}
    for r in records:
        if r.topic_id in valid_ids: by_topic.setdefault(r.topic_id,[]).append(r)
    duplicates=tuple(sorted(k for k,v in by_topic.items() if len(v)>1))
    out=[]
    for topic in inventory:
        recs=by_topic.get(topic.topic_id,[])
        if not recs:
            status="pending_specialist_review"
            refs=()
            missing=()
            message="No review record exists; remain pending."
        elif len(recs)>1:
            status="duplicate_review_records"
            refs=tuple(r.record_ref for r in recs)
            missing=()
            message="Multiple records for topic; reconcile chronology/scope before relying on any outcome."
        else:
            r=recs[0]
            refs=(r.record_ref,)
            audited=set(evidence_ledger.get(topic.topic_id,()))
            missing=tuple(ref for ref in r.evidence_refs if ref not in audited)
            if topic.topic_id=="SR09" and r.status=="accepted_within_scope":
                status="owner_rule_separate"
                message="Owner-defined rule cannot be specialist-accepted as owner authority."
            elif r.status=="revision_requested":
                status="revision_requested"
                message="Revision requested; do not treat as accepted."
            elif r.status=="not_applicable":
                status="not_applicable_pending_PO"
                message="Not-applicable rationale requires separate PO acceptance."
            elif r.status=="reviewed_with_comments":
                status="reviewed_pending_PO"
                message="Review recorded with comments; PO acceptance pending."
            elif r.status=="accepted_within_scope" and missing:
                status="evidence_trace_mismatch"
                message="Specialist accepted within stated scope, but some review evidence refs are absent from evidence ledger."
            elif r.status=="accepted_within_scope":
                status="specialist_accepted_scope_pending_PO"
                message="Specialist acceptance within scope reconciled; PO acceptance remains separate."
            else:
                status="unrecognized_review_status"
                message="Review status not recognized; fail closed."
        out.append(TopicReconciliation(topic.topic_id,status,refs,missing,message))
    if invalid or duplicates:
        overall="needs_reconciliation"
    elif any(x.status in ("evidence_trace_mismatch","owner_rule_separate","duplicate_review_records","unrecognized_review_status") for x in out):
        overall="needs_reconciliation"
    elif all(x.status in ("specialist_accepted_scope_pending_PO","not_applicable_pending_PO") for x in out):
        overall="specialist_review_reconciled_pending_PO"
    else:
        overall="review_pending"
    return ReconciliationReport(overall,tuple(out),invalid,duplicates,
        "Reconciliation is a traceability/status check, not scientific validation or execution authorization.")
