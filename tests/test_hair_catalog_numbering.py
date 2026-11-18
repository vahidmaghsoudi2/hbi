from app.domain.hair_catalog_numbering import (
    OWNER_EXCEPTION_CODES,
    analyze_shade_code,
    natural_extra_is_owner_defined_stronger_than_natural_simple,
    validate_owner_defined_series_range,
)


def test_raw_code_is_preserved_and_not_converted_to_number():
    raw = "+۰۵"
    result = analyze_shade_code(raw)
    assert result.raw_code == raw
    assert result.notation == "plus_integer"
    assert result.structural_alias == "۵.۰۰"


def test_only_explicit_extra_aliases_are_returned():
    assert analyze_shade_code("+۰۹").structural_alias == "۹.۰۰"
    assert analyze_shade_code("+10").structural_alias is None
    assert analyze_shade_code("۵").structural_alias is None


def test_decimal_and_alpha_decimal_notation_are_structural_only():
    assert analyze_shade_code("۸.۵۳۱").notation == "decimal"
    assert analyze_shade_code("BI.1").notation == "alpha_decimal"
    assert analyze_shade_code("RE.7").notation == "alpha_decimal"


def test_leading_zeroes_and_decimal_precision_are_preserved():
    assert analyze_shade_code("۰۰۲").raw_code == "۰۰۲"
    assert analyze_shade_code("۸.۵۳۱").raw_code == "۸.۵۳۱"
    assert analyze_shade_code("۰۰۲").notation == "integer"


def test_owner_exceptions_are_flagged_without_semantic_decoding():
    for code in ("۶.۷", "۸.۵۶", "۶.۵۳", "۶.۵۴"):
        result = analyze_shade_code(code)
        assert result.is_owner_exception
        assert result.structural_alias is None
    assert OWNER_EXCEPTION_CODES


def test_unknown_and_whitespace_codes_are_not_silently_normalized():
    assert not analyze_shade_code("").recognized
    assert not analyze_shade_code(" +۰۵").recognized
    assert not analyze_shade_code("+10").structural_alias


def test_natural_series_ranges_are_bounded_and_series_specific():
    assert validate_owner_defined_series_range("طبیعی", "۱۰") is True
    assert validate_owner_defined_series_range("طبیعی", "۱۱") is False
    assert validate_owner_defined_series_range("طبیعی اکسترا", "+۰۹") is True
    assert validate_owner_defined_series_range("طبیعی اکسترا", "+۱۰") is False
    assert validate_owner_defined_series_range("خاکستری", "۱۰.۱") is None


def test_natural_extra_strength_is_an_owner_rule_not_a_chemical_result():
    assert natural_extra_is_owner_defined_stronger_than_natural_simple()
