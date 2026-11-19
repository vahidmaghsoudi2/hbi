from app.domain.hair_color_missing_data_gates import GENERIC_REQUIRED, PRODUCT_SPECIFIC_REQUIRED, make_data_entry, assess_data_completeness

def complete_entries():
    return [make_data_entry(f,"recorded","professional_observed","high") for f in GENERIC_REQUIRED]

def test_generic_required_fields_matrix():
    assert len(GENERIC_REQUIRED)==9
    a=assess_data_completeness([])
    assert a.status=="needs_more_information" and len(a.missing_required)==9

def test_complete_generic_inputs_only_for_review():
    a=assess_data_completeness(complete_entries())
    assert a.status=="data_complete_for_review"

def test_product_specific_claim_requires_exact_product_identity_and_evidence():
    a=assess_data_completeness(complete_entries(),"product_specific")
    assert set(a.missing_required)==set(PRODUCT_SPECIFIC_REQUIRED)

def test_unknown_required_data_is_missing_not_assumed():
    entries=complete_entries()
    entries[0]=make_data_entry(GENERIC_REQUIRED[0],"unknown","client_reported","unknown")
    a=assess_data_completeness(entries)
    assert GENERIC_REQUIRED[0] in a.missing_required

def test_image_only_is_uncertain_limited_review():
    entries=complete_entries()
    entries[2]=make_data_entry(GENERIC_REQUIRED[2],"approximate description","image_only","low")
    a=assess_data_completeness(entries)
    assert a.status=="limited_review"
    assert GENERIC_REQUIRED[2] in a.uncertain_fields

def test_conflicting_required_data_blocks_review():
    entries=complete_entries()
    entries[3]=make_data_entry(GENERIC_REQUIRED[3],"reported state","client_reported","medium",("report_vs_observation",))
    assert assess_data_completeness(entries).status=="conflict_review"

def test_duplicate_field_fail_closed():
    entries=complete_entries()+[complete_entries()[0]]
    assert assess_data_completeness(entries).status=="duplicate_fields"

def test_invalid_entry_type_fail_closed():
    assert assess_data_completeness(["bad"]).status=="invalid_entries"

def test_invalid_claim_type_fail_closed():
    assert assess_data_completeness(complete_entries(),"chemical_formula").status=="invalid_claim_type"

def test_unknown_source_requires_limited_review():
    entries=complete_entries()
    entries[-1]=make_data_entry(GENERIC_REQUIRED[-1],"recorded","unknown","unknown")
    assert assess_data_completeness(entries).status=="limited_review"

def test_missing_context_field_detected():
    entries=[e for e in complete_entries() if e.field_id!="context.constraints"]
    assert "context.constraints" in assess_data_completeness(entries).missing_required
