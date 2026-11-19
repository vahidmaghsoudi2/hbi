from app.domain.hair_color_version_invalidation import OUTPUTS, invalidate_for_change

def test_target_change_creates_full_fresh_invalidation():
    a=invalidate_for_change("v1","v2",["target_color"])
    assert a.status=="target_changed_full_invalidation"
    assert set(a.invalidated_outputs)==set(OUTPUTS)
    assert a.fresh_evaluation_required
    assert a.decision_records_reset==("specialist_review","client_acceptance","execution_consent")

def test_current_base_change_invalidates_only_dependents():
    a=invalidate_for_change("v1","v2",["current_base"])
    assert "current_base_assessment" in a.invalidated_outputs
    assert "service_history_assessment" in a.preserved_outputs
    assert "specialist_review" in a.decision_records_reset

def test_service_history_change_invalidates_safety_and_downstream():
    a=invalidate_for_change("v1","v2",["service_history"])
    assert {"service_history_assessment","safety_assessment","feasibility","candidate_options"} <= set(a.invalidated_outputs)

def test_product_evidence_change_invalidates_product_dependent_outputs():
    a=invalidate_for_change("v1","v2",["product_evidence"])
    assert "product_evidence" not in a.invalidated_outputs
    assert "candidate_options" in a.invalidated_outputs
    assert "current_base_assessment" in a.preserved_outputs

def test_unknown_changed_item_full_fail_closed_invalidation():
    a=invalidate_for_change("v1","v2",["unregistered_input"])
    assert a.status=="unknown_dependency_full_invalidation"
    assert set(a.invalidated_outputs)==set(OUTPUTS)

def test_multiple_changes_union_dependencies():
    a=invalidate_for_change("v1","v2",["current_base","product_identity"])
    assert "current_base_assessment" in a.invalidated_outputs
    assert "family_selection" in a.invalidated_outputs
    assert "service_history_assessment" in a.preserved_outputs

def test_unaffected_output_preserved():
    a=invalidate_for_change("v1","v2",["image_quality"])
    assert "target_assessment" in a.preserved_outputs
    assert "regional_state_assessment" in a.invalidated_outputs

def test_changed_version_mandatory():
    assert invalidate_for_change("v1","v1",["target_color"]).status=="invalid_version"

def test_change_items_required():
    assert invalidate_for_change("v1","v2",[]).status=="invalid_change_items"

def test_existing_output_inventory_invalid():
    assert invalidate_for_change("v1","v2",["current_base"],None).status=="invalid_outputs"

def test_changed_target_always_resets_acceptance_consent_and_review():
    a=invalidate_for_change("v1","v2",["target_color"])
    assert set(a.decision_records_reset)=={"specialist_review","client_acceptance","execution_consent"}

def test_preserved_outputs_only_outside_dependency_set():
    a=invalidate_for_change("v1","v2",["priorities"])
    assert "target_assessment" in a.invalidated_outputs
    assert "current_base_assessment" in a.preserved_outputs
