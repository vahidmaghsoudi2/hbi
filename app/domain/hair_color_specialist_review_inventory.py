"""Inventory of specialist-review topics; no technical rule is pre-approved."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ReviewTopic:
    topic_id: str
    topic: str
    scope: str
    specialist_required: bool
    status: str="pending_specialist_review"

TOPICS=(
    ReviewTopic("SR01","Level/pigment estimation limits","Observed/descriptive estimates and image uncertainty",True),
    ReviewTopic("SR02","Color-wheel and neutralization principles","General theory and limits of application",True),
    ReviewTopic("SR03","Tone-family terminology","Meaning and boundaries of named tone families",True),
    ReviewTopic("SR04","Depth/hue/reflect/intensity distinctions","Terminology and evaluation criteria",True),
    ReviewTopic("SR05","Underlying pigment and tone selection","Decision rules and evidence scope",True),
    ReviewTopic("SR06","Result-influencing factors","Factors and their permitted interpretation",True),
    ReviewTopic("SR07","Catalog family/editorial group boundary","Exact raw labels vs provisional editorial groups",True),
    ReviewTopic("SR08","Numbering aliases and special exceptions","Owner-recorded formats and exceptions; no chemistry inference",True),
    ReviewTopic("SR09","Natural Extra owner-defined rule","Owner-defined comparison; specialist review only for technical claims",False),
    ReviewTopic("SR10","Target/base feasibility","Feasibility claims and limits",True),
    ReviewTopic("SR11","Regional hair-state interpretation","Region differences and observation limits",True),
    ReviewTopic("SR12","Prior-service compatibility","History evidence and compatibility review",True),
    ReviewTopic("SR13","Product-specific claims","Exact identity and official evidence conditions",True),
    ReviewTopic("SR14","Option ranking and alternatives","Goal fit, technical validity, rank criteria",True),
    ReviewTopic("SR15","Safety/testing stop rules","Safety boundaries, manufacturer instructions, referral",True),
)

@dataclass(frozen=True)
class ReviewRecord:
    topic_id: str
    status: str
    reviewer_ref: str
    evidence_refs: tuple[str,...]
    scope_note: str
    message: str

def review_inventory()->tuple[ReviewTopic,...]:
    return TOPICS

def record_topic_review(topic_id: object,status: object,reviewer_ref: object,
                       evidence_refs: object,scope_note: object)->ReviewRecord:
    topic=next((x for x in TOPICS if x.topic_id==topic_id),None)
    if topic is None:
        return ReviewRecord(str(topic_id),"invalid_topic","",(),"","Unknown topic; no status changed.")
    if status not in ("owner_recorded","reviewed_pending_acceptance","specialist_accepted","not_applicable"):
        return ReviewRecord(topic.topic_id,"invalid_status","",(),"","Review status invalid.")
    reviewer=reviewer_ref.strip() if isinstance(reviewer_ref,str) else ""
    refs=tuple(x.strip() for x in evidence_refs if isinstance(x,str) and x.strip()) if isinstance(evidence_refs,(tuple,list)) else ()
    scope=scope_note.strip() if isinstance(scope_note,str) else ""
    if status=="owner_recorded":
        if not reviewer or not refs or not scope:
            return ReviewRecord(topic.topic_id,"evidence_incomplete",reviewer,refs,scope,"Owner record requires decision reference, scope, and evidence trace.")
        if topic.specialist_required:
            return ReviewRecord(topic.topic_id,"owner_recorded_not_specialist_accepted",reviewer,refs,scope,"Owner record captured; specialist review remains pending.")
        return ReviewRecord(topic.topic_id,"owner_recorded",reviewer,refs,scope,"Owner-defined scope recorded; does not support technical claims.")
    if status=="specialist_accepted":
        if not reviewer or not refs or not scope:
            return ReviewRecord(topic.topic_id,"evidence_incomplete",reviewer,refs,scope,"Specialist acceptance requires reviewer reference, evidence, and scope.")
        if not topic.specialist_required:
            return ReviewRecord(topic.topic_id,"owner_defined_topic",reviewer,refs,scope,"This topic is owner-defined; specialist acceptance is not substituted for owner authority.")
        return ReviewRecord(topic.topic_id,"specialist_accepted",reviewer,refs,scope,"Specialist review recorded with evidence and scope; PO acceptance remains separate.")
    if status=="reviewed_pending_acceptance":
        if not reviewer or not refs or not scope:
            return ReviewRecord(topic.topic_id,"evidence_incomplete",reviewer,refs,scope,"Review record requires reviewer reference, evidence, and scope.")
        return ReviewRecord(topic.topic_id,"reviewed_pending_acceptance",reviewer,refs,scope,"Review recorded; acceptance remains pending.")
    if status=="not_applicable":
        if not reviewer or not scope:
            return ReviewRecord(topic.topic_id,"evidence_incomplete",reviewer,refs,scope,"Not-applicable decision requires traceable reviewer/owner and scope.")
        return ReviewRecord(topic.topic_id,"not_applicable",reviewer,refs,scope,"Not-applicable scope recorded; no technical rule implied.")
