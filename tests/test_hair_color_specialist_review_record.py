from app.domain.hair_color_specialist_review_record import create_specialist_review_record, REVIEW_STATUSES
from app.domain.hair_color_specialist_review_inventory import review_inventory

def record(**overrides):
    values=dict(topic_id="SR12",status="reviewed_with_comments",reviewer_ref="specialist-ref",
      review_date="2026-11-19",evidence_refs=("source-1",),reviewed_scope="compatibility rules only",
      findings="Needs source alignment",limitations="No formula recommendation",record_ref="review-001")
    values.update(overrides)
    return create_specialist_review_record(**values)

def test_review_outcome_statuses_are_explicit():
    assert set(REVIEW_STATUSES)=={"reviewed_with_comments","revision_requested","accepted_within_scope","not_applicable"}

def test_review_record_requires_real_trace_fields():
    a=record()
    assert a.status=="review_record_created" and a.record.reviewer_ref=="specialist-ref"

def test_review_records_cannot_be_created_with_blank_reviewer():
    assert record(reviewer_ref="").status=="record_incomplete"

def test_evidence_refs_required():
    assert record(evidence_refs=()).status=="record_incomplete"

def test_scope_findings_limitations_recorded():
    a=record()
    assert a.record.reviewed_scope and a.record.findings and a.record.limitations

def test_invalid_iso_date_rejected():
    assert record(review_date="19-11-2026").status=="invalid_date"

def test_unknown_topic_rejected():
    assert record(topic_id="SR99").status=="invalid_topic"

def test_unknown_outcome_rejected():
    assert record(status="approved").status=="invalid_status"

def test_specialist_cannot_accept_owner_authority():
    a=record(topic_id="SR09",status="accepted_within_scope")
    assert a.status=="owner_defined_topic"

def test_review_not_automatic_po_acceptance():
    a=record(status="accepted_within_scope")
    assert a.status=="review_record_created"
    assert "PO acceptance" in a.message

def test_inventory_has_pending_topics_until_records_exist():
    assert all(x.status=="pending_specialist_review" for x in review_inventory())

def test_not_applicable_requires_reason_fields():
    assert record(status="not_applicable",findings="",limitations="").status=="record_incomplete"
