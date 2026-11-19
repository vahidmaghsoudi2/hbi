from app.domain.hair_color_current_base import BaseEvidence, LEVEL_LABELS, describe_current_base, level_label

def test_level_scale_labels_are_defined_and_approximate_ordered():
    assert tuple(LEVEL_LABELS)==tuple(range(1,11))
    assert LEVEL_LABELS[1]=="black"
    assert LEVEL_LABELS[10]=="lightest_blonde"

def test_observed_level_is_descriptive_not_predictive():
    result=describe_current_base("mid-length",5,BaseEvidence.OBSERVED,"medium","light brown")
    assert result is not None
    assert result.level==5 and result.label=="light_brown"
    assert result.status=="descriptive_only"

def test_image_only_keeps_uncertain_status_even_with_level_value():
    result=describe_current_base("roots",6,"image_only","high")
    assert result is not None
    assert result.status=="uncertain_review"
    assert result.evidence==BaseEvidence.IMAGE

def test_unknown_level_does_not_guess_or_default():
    result=describe_current_base("ends",None,"unknown")
    assert result is not None
    assert result.level is None and result.label is None
    assert result.status=="uncertain_review"

def test_invalid_levels_and_boolean_rejected_by_label_lookup():
    assert level_label(0) is None
    assert level_label(11) is None
    assert level_label(True) is None
    assert level_label("5") is None

def test_invalid_region_or_source_fails_closed():
    assert describe_current_base("",4,"documented") is None
    assert describe_current_base("roots",4,"bad_source") is None

def test_confidence_unknown_keeps_review_uncertain():
    result=describe_current_base("roots",4,"professional_observed","unknown")
    assert result is not None and result.status=="uncertain_review"
