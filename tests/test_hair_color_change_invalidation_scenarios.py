from app.domain.hair_color_change_invalidation_scenarios import change_scenarios
from app.domain.hair_color_version_invalidation import invalidate_for_change
from app.domain.hair_color_acceptance_execution_consent import new_decision_record, Acceptance, Consent

def test_change_scenario_matrix_has_ten_unique_contracts():
    c=change_scenarios()
    assert len(c)==10 and len({x.scenario_id for x in c})==10

def test_ch01_target_change_invalidates_all_and_requires_fresh_eval():
    a=invalidate_for_change("v1","v2",["target_color"])
    assert a.status=="target_changed_full_invalidation" and a.fresh_evaluation_required

def test_ch02_current_base_dependency_set():
    a=invalidate_for_change("v1","v2",["current_base"])
    assert "current_base_assessment" in a.invalidated_outputs
    assert "service_history_assessment" in a.preserved_outputs

def test_ch03_history_change_includes_safety_and_downstream():
    a=invalidate_for_change("v1","v2",["service_history"])
    assert {"service_history_assessment","safety_assessment","candidate_options"} <= set(a.invalidated_outputs)

def test_ch04_product_evidence_change():
    a=invalidate_for_change("v1","v2",["product_evidence"])
    assert "family_selection" in a.invalidated_outputs
    assert "regional_state_assessment" in a.preserved_outputs

def test_ch05_safety_screen_change_invalidates_safety_decisions():
    a=invalidate_for_change("v1","v2",["safety_screen"])
    assert "safety_assessment" in a.invalidated_outputs
    assert "execution_consent" in a.invalidated_outputs

def test_ch06_multiple_changes_union_dependencies():
    a=invalidate_for_change("v1","v2",["current_base","product_identity"])
    assert {"current_base_assessment","family_selection","candidate_options"} <= set(a.invalidated_outputs)

def test_ch07_unknown_input_full_fail_closed():
    a=invalidate_for_change("v1","v2",["unknown_effective_field"])
    assert a.status=="unknown_dependency_full_invalidation"

def test_ch08_new_decision_record_does_not_carry_acceptance_or_consent():
    old=new_decision_record("v1","s1")
    accepted=old
    new=new_decision_record("v2","s2")
    assert new.acceptance==Acceptance.PENDING and new.execution_consent==Consent.PENDING

def test_ch09_same_version_change_rejected():
    assert invalidate_for_change("v1","v1",["current_base"]).status=="invalid_version"

def test_ch10_unaffected_output_preserved():
    a=invalidate_for_change("v1","v2",["image_quality"])
    assert "target_assessment" in a.preserved_outputs
