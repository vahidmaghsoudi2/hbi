from app.domain.hair_color_service_history import ServiceType, HistorySource, make_history_entry, assess_history

def test_service_types_include_chemical_and_unknown_categories():
    assert ServiceType.BLEACH.value=="bleach"
    assert ServiceType.PLANT_DYE.value=="plant_dye"
    assert ServiceType.UNKNOWN.value=="unknown"

def test_unknown_history_is_not_no_history():
    a=assess_history(None,"unknown_history")
    assert a.status=="history_unknown"
    assert "do not infer" in a.message

def test_no_services_reported_is_explicit_status():
    a=assess_history([], "none_reported")
    assert a.status=="no_history_reported"
    assert "not independent verification" in a.message

def test_none_reported_with_entries_conflict():
    entry=make_history_entry("color",source="client_reported",certainty="confirmed")
    a=assess_history([entry],"none_reported")
    assert a.status=="conflict_review"

def test_known_history_without_entries_requests_details():
    a=assess_history([], "known_history")
    assert a.status=="history_incomplete"
    assert "service_entries" in a.unknown_fields

def test_entry_preserves_report_source_region_and_approximate_period():
    entry=make_history_entry("lightening","about 6 months ago","Brand X","product/shade","market unknown","client_reported","approximate",["mid-length","ends"],"User-reported, synthetic test record")
    assert entry is not None
    assert entry.source==HistorySource.CLIENT
    assert entry.certainty=="approximate"
    assert entry.affected_regions==("mid-length","ends")

def test_conflict_requires_reconciliation_before_dependent_review():
    entry=make_history_entry("toner",source="documented",certainty="confirmed")
    a=assess_history([entry],"known_history",("period_disagreement",))
    assert a.status=="conflict_review"

def test_invalid_entry_type_fails_closed():
    a=assess_history(["not an entry"],"known_history")
    assert a.status=="invalid_entries"
