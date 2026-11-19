from app.domain.hair_color_implementation_handoff import handoff_stages, implementation_authorized

def test_handoff_has_seven_stages():
    assert len(handoff_stages())==7

def test_stages_dependency_order():
    ids=[s.stage_id for s in handoff_stages()]
    assert ids==["H0","H1","H2","H3","H4","H5","H6"]

def test_integration_depends_on_foundation_controls_and_evidence():
    h=next(s for s in handoff_stages() if s.stage_id=="H4")
    assert set(h.dependencies)=={"H1","H2","H3"}

def test_verification_depends_on_integrated_stages():
    h=next(s for s in handoff_stages() if s.stage_id=="H5")
    assert "H4" in h.dependencies

def test_implementation_not_authorized_by_handoff():
    assert implementation_authorized() is False

def test_release_gate_remains_pending_po():
    assert handoff_stages()[-1].status=="pending_PO_decision"
