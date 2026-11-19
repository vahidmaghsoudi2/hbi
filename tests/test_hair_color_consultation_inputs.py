from app.domain.hair_color_consultation_inputs import INPUTS, EvidenceQuality, InputGroup, assess_intake, get_input

def test_input_ids_are_unique_and_groups_defined():
    ids=[i.input_id for i in INPUTS]
    assert len(ids)==len(set(ids))
    assert all(isinstance(i.group,InputGroup) for i in INPUTS)

def test_required_initial_inputs_cover_goal_state_history_regions_and_safety():
    required={i.input_id for i in INPUTS if i.required_for_initial_review}
    for field in ("goal.target_color","current.base_level","history.color_services","regional.map","safety.screen"):
        assert field in required
    assert "product.identity" not in required

def test_missing_required_fields_stop_definitive_advice():
    a=assess_intake({})
    assert a.readiness=="needs_more_information"
    assert "goal.target_color" in a.missing_required
    assert "no definitive" in a.message

def test_image_only_is_uncertain():
    values={i.input_id:"known" for i in INPUTS if i.required_for_initial_review}
    values["current.base_level"]="image_only"
    a=assess_intake(values)
    assert a.readiness=="limited_review"
    assert "current.base_level" in a.uncertain
    assert "uncertain" in a.message

def test_complete_inputs_mean_ready_for_review_not_execution():
    values={i.input_id:"known" for i in INPUTS if i.required_for_initial_review}
    a=assess_intake(values)
    assert a.readiness=="intake_complete_for_review"
    assert "not feasibility" in a.message

def test_product_specific_claim_requires_exact_identity_contract():
    item=get_input("product.identity")
    assert item is not None and not item.required_for_initial_review
    assert "product" in item.purpose
    assert "not chemistry evidence" in item.limitation

def test_unknown_field_lookup_fails_closed():
    assert get_input("bad-field") is None
    assert get_input(None) is None

def test_quality_values_include_unknown_and_image_only():
    assert EvidenceQuality.IMAGE_ONLY.value=="image_only"
    assert EvidenceQuality.UNKNOWN.value=="unknown"
