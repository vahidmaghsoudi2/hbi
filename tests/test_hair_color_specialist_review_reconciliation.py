from app.domain.hair_color_specialist_review_record import SpecialistReviewRecord
from app.domain.hair_color_specialist_review_reconciliation import reconcile_specialist_reviews
from app.domain.hair_color_specialist_review_inventory import review_inventory

def rec(topic="SR12",status="accepted_within_scope",evidence=("e1",),record="r1"):
    return SpecialistReviewRecord(topic,status,"reviewer","2026-11-19",evidence,"defined scope","finding","limitations",record)

def test_empty_review_set_keeps_all_topics_pending():
    a=reconcile_specialist_reviews([], {})
    assert a.status=="review_pending" and len(a.topics)==15
    assert all(x.status=="pending_specialist_review" for x in a.topics)

def test_review_accepted_with_evidence_ledger_is_pending_po():
    a=reconcile_specialist_reviews([rec()],{"SR12":["e1"]})
    x=next(t for t in a.topics if t.topic_id=="SR12")
    assert x.status=="specialist_accepted_scope_pending_PO"

def test_accepted_review_with_unreconciled_evidence_ref_blocked():
    a=reconcile_specialist_reviews([rec()],{"SR12":[]})
    x=next(t for t in a.topics if t.topic_id=="SR12")
    assert x.status=="evidence_trace_mismatch" and x.missing_evidence_refs==("e1",)

def test_revision_requested_never_marked_accepted():
    x=next(t for t in reconcile_specialist_reviews([rec(status="revision_requested")],{"SR12":["e1"]}).topics if t.topic_id=="SR12")
    assert x.status=="revision_requested"

def test_comments_review_requires_po_acceptance():
    x=next(t for t in reconcile_specialist_reviews([rec(status="reviewed_with_comments")],{"SR12":["e1"]}).topics if t.topic_id=="SR12")
    assert x.status=="reviewed_pending_PO"

def test_owner_defined_rule_specialist_acceptance_does_not_override_owner():
    x=next(t for t in reconcile_specialist_reviews([rec("SR09")],{"SR09":["e1"]}).topics if t.topic_id=="SR09")
    assert x.status=="owner_rule_separate"

def test_not_applicable_requires_po_acceptance():
    x=next(t for t in reconcile_specialist_reviews([rec(status="not_applicable")],{"SR12":["e1"]}).topics if t.topic_id=="SR12")
    assert x.status=="not_applicable_pending_PO"

def test_duplicate_records_flagged():
    a=reconcile_specialist_reviews([rec(record="r1"),rec(record="r2")],{"SR12":["e1"]})
    assert a.duplicate_topic_ids==("SR12",)
    assert next(t for t in a.topics if t.topic_id=="SR12").status=="duplicate_review_records"

def test_unknown_topic_record_flagged():
    a=reconcile_specialist_reviews([rec("SR99")],{})
    assert a.invalid_record_topics==("SR99",) and a.status=="needs_reconciliation"

def test_invalid_records_and_ledger_fail_closed():
    assert reconcile_specialist_reviews(["bad"],{}).status=="invalid_records"
    assert reconcile_specialist_reviews([],None).status=="invalid_evidence_ledger"

def test_all_inventory_topics_are_reported():
    assert {t.topic_id for t in reconcile_specialist_reviews([],{}).topics}=={t.topic_id for t in review_inventory()}

def test_overall_pending_when_reviews_incomplete():
    a=reconcile_specialist_reviews([rec()],{"SR12":["e1"]})
    assert a.status=="review_pending"
