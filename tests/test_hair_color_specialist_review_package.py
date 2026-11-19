from app.domain.hair_color_specialist_review_package import prepare_review_package, review_package_topics
from app.domain.hair_color_specialist_review_inventory import review_inventory

def test_package_covers_all_inventory_topics():
    p=prepare_review_package()
    assert p.status=="package_prepared"
    assert set(p.topic_ids)=={x.topic_id for x in review_inventory()}

def test_package_not_claimed_sent():
    assert prepare_review_package().delivery_status=="prepared_not_sent"

def test_every_topic_has_document_references_and_review_questions():
    assert all(t.document_refs and t.review_questions for t in review_package_topics())

def test_topic_ids_unique():
    ids=[x.topic_id for x in review_package_topics()]
    assert len(ids)==len(set(ids))==15

def test_package_evidence_requests_are_defined():
    assert all(x.evidence_request for x in review_package_topics())

def test_specialist_package_has_scope_review_for_owner_rule():
    t=next(x for x in review_package_topics() if x.topic_id=="SR09")
    assert "Owner rule" in t.evidence_request
