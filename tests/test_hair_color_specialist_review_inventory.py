from app.domain.hair_color_specialist_review_inventory import review_inventory, record_topic_review

def test_inventory_has_fifteen_unique_review_topics():
    a=review_inventory()
    assert len(a)==15 and len({x.topic_id for x in a})==15

def test_all_specialist_topics_pending_by_default():
    assert all(x.status=="pending_specialist_review" for x in review_inventory() if x.specialist_required)

def test_owner_defined_natural_extra_not_misclassified_as_specialist_required():
    a=next(x for x in review_inventory() if x.topic_id=="SR09")
    assert not a.specialist_required

def test_owner_record_does_not_replace_specialist_review():
    a=record_topic_review("SR08","owner_recorded","PO-DECISION",("decision-ref",),"numbering scope")
    assert a.status=="owner_recorded_not_specialist_accepted"

def test_specialist_acceptance_requires_trace_and_scope():
    a=record_topic_review("SR12","specialist_accepted","reviewer-ref",("evidence-ref",),"compatibility scope")
    assert a.status=="specialist_accepted"

def test_acceptance_missing_evidence_blocked():
    a=record_topic_review("SR12","specialist_accepted","reviewer-ref",(),"scope")
    assert a.status=="evidence_incomplete"

def test_owner_defined_topic_cannot_be_specialist_accepted_as_owner_authority():
    a=record_topic_review("SR09","specialist_accepted","reviewer",("e1",),"owner rule")
    assert a.status=="owner_defined_topic"

def test_reviewed_pending_acceptance_remains_not_accepted():
    a=record_topic_review("SR05","reviewed_pending_acceptance","reviewer",("source-1",),"scope")
    assert a.status=="reviewed_pending_acceptance"

def test_not_applicable_requires_scope_trace():
    assert record_topic_review("SR13","not_applicable","owner",(),"").status=="evidence_incomplete"

def test_unknown_topic_and_status_fail_closed():
    assert record_topic_review("SR99","specialist_accepted","reviewer",("e1",),"scope").status=="invalid_topic"
    assert record_topic_review("SR12","approved","reviewer",("e1",),"scope").status=="invalid_status"

def test_owner_record_missing_reference_is_incomplete():
    assert record_topic_review("SR09","owner_recorded","PO",(),"scope").status=="evidence_incomplete"
