from app.domain.hair_catalog_families import (
    classify_catalog_family,
    known_catalog_family_labels,
)


EXPECTED_LABELS = (
    "طبیعی", "طبیعی اکسترا", "خاکستری", "دودی", "زیتونی", "طلایی", "بژ",
    "نسکافه ای", "آلبالویی", "شکلاتی", "عسلی", "فندقی", "شرابی", "قرمز",
    "عروسکی", "بیسکویتی", "کاپوچینو", "ترکیبی", "واریاسیون",
)


def test_family_labels_are_exact_catalog_series_labels():
    assert known_catalog_family_labels() == EXPECTED_LABELS


def test_raw_series_label_is_preserved_as_catalog_family():
    result = classify_catalog_family("طبیعی اکسترا")
    assert result is not None
    assert result.series_name_raw == "طبیعی اکسترا"
    assert result.catalog_family_label == "طبیعی اکسترا"
    assert result.classification_source == "catalog_series_label"


def test_provisional_groups_are_explicitly_non_approved_navigation():
    result = classify_catalog_family("خاکستری")
    assert result is not None
    assert result.editorial_group == "cool_named"
    assert result.editorial_group_status == "provisional"


def test_unknown_or_modified_label_fails_closed():
    assert classify_catalog_family("خاکستری ") is None
    assert classify_catalog_family("Ash") is None
    assert classify_catalog_family(None) is None
    assert classify_catalog_family(42) is None


def test_catalog_family_and_editorial_group_are_not_conflated():
    result = classify_catalog_family("طلایی")
    assert result is not None
    assert result.catalog_family_label == "طلایی"
    assert result.editorial_group == "gold_named"
    assert result.catalog_family_label != result.editorial_group
