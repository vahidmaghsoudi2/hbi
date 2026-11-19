"""Structured intake for real specialist review records; no reviews fabricated."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from app.domain.hair_color_specialist_review_inventory import review_inventory

REVIEW_STATUSES=("reviewed_with_comments","revision_requested","accepted_within_scope","not_applicable")

@dataclass(frozen=True)
class SpecialistReviewRecord:
    topic_id: str
    status: str
    reviewer_ref: str
    review_date: str
    evidence_refs: tuple[str,...]
    reviewed_scope: str
    findings: str
    limitations: str
    record_ref: str

@dataclass(frozen=True)
class ReviewRecordResult:
    status: str
    record: SpecialistReviewRecord|None
    message: str

def create_specialist_review_record(topic_id: object,status: object,reviewer_ref: object,
                                   review_date: object,evidence_refs: object,
                                   reviewed_scope: object,findings: object,
                                   limitations: object,record_ref: object)->ReviewRecordResult:
    topic=next((x for x in review_inventory() if x.topic_id==topic_id),None)
    if topic is None:
        return ReviewRecordResult("invalid_topic",None,"Topic not in inventory; record rejected.")
    if status not in REVIEW_STATUSES:
        return ReviewRecordResult("invalid_status",None,"Only explicit review outcomes are accepted.")
    if status=="accepted_within_scope" and not topic.specialist_required:
        return ReviewRecordResult("owner_defined_topic",None,"Owner-defined topic cannot be accepted as owner authority by specialist.")
    reviewer=reviewer_ref.strip() if isinstance(reviewer_ref,str) else ""
    date_value=review_date.strip() if isinstance(review_date,str) else ""
    refs=tuple(x.strip() for x in evidence_refs if isinstance(x,str) and x.strip()) if isinstance(evidence_refs,(tuple,list)) else ()
    scope=reviewed_scope.strip() if isinstance(reviewed_scope,str) else ""
    finding=findings.strip() if isinstance(findings,str) else ""
    limit=limitations.strip() if isinstance(limitations,str) else ""
    rid=record_ref.strip() if isinstance(record_ref,str) else ""
    try:
        date.fromisoformat(date_value)
    except (ValueError,TypeError):
        return ReviewRecordResult("invalid_date",None,"Review date must be a valid ISO date.")
    if not reviewer or not refs or not scope or not finding or not limit or not rid:
        return ReviewRecordResult("record_incomplete",None,"Reviewer, evidence refs, scope, findings, limitations, and record ref are required.")
    rec=SpecialistReviewRecord(topic.topic_id,status,reviewer,date_value,refs,scope,finding,limit,rid)
    return ReviewRecordResult("review_record_created",rec,"Record structure validated; this does not independently verify evidence or create PO acceptance.")
