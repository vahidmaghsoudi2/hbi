from app.domain.hair_color_specialist_scenarios import scenario_catalog, assess_scenario

def test_catalog_has_twelve_scenarios_with_unique_ids():
    c=scenario_catalog()
    assert len(c)==12 and len({x.scenario_id for x in c})==12

def test_all_scenarios_pending_specialist_oracle_by_default():
    assert all(x.technical_oracle_status=="specialist_review_pending" for x in scenario_catalog())

def test_regional_unevenness_requires_regional_state_and_image_quality():
    a=assess_scenario("HC-S01",[])
    assert a.status=="needs_case_data"
    assert set(a.missing_fields)=={"regional_state","image_quality"}

def test_unknown_history_does_not_infer_history():
    a=assess_scenario("HC-S02",["service_history"])
    assert a.status=="specialist_oracle_pending"

def test_product_uncertainty_scenario_requires_product_identity_and_evidence():
    a=assess_scenario("HC-S07",["product_identity"])
    assert a.status=="needs_case_data" and "product_evidence" in a.missing_fields

def test_safety_scenario_requires_safety_and_product_evidence():
    a=assess_scenario("HC-S08",["safety"])
    assert a.status=="needs_case_data"

def test_conflict_scenario_requires_conflict_record():
    a=assess_scenario("HC-S09",["regional_state"])
    assert a.status=="needs_case_data" and "conflict" in a.missing_fields

def test_reference_photo_scenario_does_not_supply_current_base():
    a=assess_scenario("HC-S10",["target","image_quality"])
    assert a.status=="specialist_oracle_pending"

def test_ambiguous_family_requires_target_clarification_field():
    assert assess_scenario("HC-S11",[]).status=="needs_case_data"

def test_approved_oracle_without_evidence_not_ready():
    a=assess_scenario("HC-S12",["image_quality","regional_state"],True,())
    assert a.status=="evidence_missing"

def test_approved_oracle_with_refs_ready_for_specialist_test():
    a=assess_scenario("HC-S05",["service_history","safety"],True,("expert-review-1",))
    assert a.status=="ready_for_specialist_test"

def test_unknown_scenario_fails_closed():
    assert assess_scenario("HC-S99",[]).status=="unknown_scenario"
