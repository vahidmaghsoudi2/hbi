from app.domain.hair_color_owner_acceptance_report import acceptance_criteria, owner_acceptance_report

def test_report_decision_remains_pending_owner():
    a=owner_acceptance_report()
    assert a.report_status=="prepared_pending_PO_decision"
    assert a.po_decision=="pending" and a.po_decision_ref==""

def test_recommendation_limited_to_documentation_baseline():
    assert owner_acceptance_report().recommended_decision=="accept_documentation_baseline_only_with_conditions"

def test_specialist_review_runtime_tests_customer_use_are_blockers():
    a=owner_acceptance_report()
    assert {"AC04","AC06","AC07","AC08"} <= set(a.blockers)

def test_acceptance_matrix_has_ten_criteria():
    assert len(acceptance_criteria())==10

def test_no_criterion_claims_production_or_customer_readiness():
    assert all(c.evidence_status!="production_ready" for c in acceptance_criteria())
