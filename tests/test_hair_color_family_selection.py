from app.domain.hair_color_family_selection import select_target_families, CATALOG_FAMILY_LABELS

def test_known_catalog_labels_are_exact_and_19():
    assert len(CATALOG_FAMILY_LABELS) == 19
    assert "طبیعی" in CATALOG_FAMILY_LABELS
    assert "طبیعی اکسترا" in CATALOG_FAMILY_LABELS

def test_exact_single_family_captured_for_review():
    a = select_target_families(["طبیعی"])
    assert a.status == "families_recorded_for_review"
    assert a.selected_labels == ("طبیعی",)
    assert "No technical fit" in a.message

def test_client_order_preserved_without_technical_ranking():
    a = select_target_families(["بژ", "طلایی"])
    assert a.selected_labels == ("بژ", "طلایی")
    assert a.ranking_basis == "client_order_only"

def test_empty_selection_asks_clarification():
    assert select_target_families([]).status == "needs_clarification"

def test_unknown_family_not_fuzzy_mapped():
    a = select_target_families(["قهوه‌ای"])
    assert a.status == "family_unrecognized"
    assert a.invalid_labels == ("قهوه‌ای",)

def test_whitespace_variant_not_normalized():
    assert select_target_families([" طبیعی"]).status == "family_unrecognized"

def test_more_than_three_choices_not_truncated():
    a = select_target_families(["طبیعی", "خاکستری", "دودی", "بژ"])
    assert a.status == "too_many_choices"
    assert a.selected_labels == ()

def test_duplicates_rejected():
    assert select_target_families(["بژ", "بژ"]).status == "invalid_labels"

def test_only_explicit_client_selection_source():
    assert select_target_families(["بژ"], source="model_inferred").status == "invalid_source"

def test_non_list_input_fail_closed():
    assert select_target_families("بژ").status == "needs_clarification"
