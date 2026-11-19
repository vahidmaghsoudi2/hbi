from app.domain.hair_color_regional_state import (
    HairRegion, ObservationSource, Confidence, make_regional_state, assess_regional_state
)

def record(region, source="professional_observed", confidence="high", conflicts=()):
    return make_regional_state(region, color_description="recorded description",
        condition_description="recorded condition", texture_description="recorded texture",
        source=source, confidence=confidence, conflicts=conflicts)

def test_regions_include_roots_midlengths_ends_and_patch():
    assert HairRegion.ROOTS.value == "roots"
    assert HairRegion.MID_LENGTHS.value == "mid_lengths"
    assert HairRegion.ENDS.value == "ends"
    assert HairRegion.PATCH.value == "patch_or_zone"

def test_missing_region_requests_more_information():
    a = assess_regional_state([record("roots"), record("ends")])
    assert a.status == "needs_more_information"
    assert "mid_lengths" in a.missing_regions

def test_complete_region_set_is_recorded_without_advice():
    a = assess_regional_state([record("roots"), record("mid_lengths"), record("ends")])
    assert a.status == "regional_state_recorded"
    assert "not feasibility" in a.message

def test_image_only_is_limited_and_low_confidence():
    r = record("roots", "image_only", "high")
    assert r.confidence == Confidence.LOW
    assert any("do not infer porosity" in x for x in r.limitations)
    a = assess_regional_state([r, record("mid_lengths"), record("ends")])
    assert a.status == "limited_review"
    assert "roots" in a.uncertain_regions

def test_unknown_source_is_limited():
    a = assess_regional_state([record("roots", "unknown", "unknown"), record("mid_lengths"), record("ends")])
    assert a.status == "limited_review"

def test_conflict_blocks_dependent_review():
    a = assess_regional_state([record("roots", conflicts=("client_vs_observed",)), record("mid_lengths"), record("ends")])
    assert a.status == "conflict_review"
    assert a.conflict_regions == ("roots",)

def test_invalid_record_fails_closed():
    a = assess_regional_state(["not a regional record"])
    assert a.status == "invalid_records"

def test_invalid_expected_regions_fails_closed():
    a = assess_regional_state([record("roots")], expected_regions=["invented"])
    assert a.status == "invalid_scope"

def test_patch_zone_can_be_added_without_replacing_standard_regions():
    a = assess_regional_state([record("roots"), record("mid_lengths"), record("ends"), record("patch")])
    assert a.status == "regional_state_recorded"

def test_client_report_is_captured_as_distinct_source():
    r = record("ends", "client_reported", "medium")
    assert r.source == ObservationSource.CLIENT
    assert r.confidence == Confidence.MEDIUM
