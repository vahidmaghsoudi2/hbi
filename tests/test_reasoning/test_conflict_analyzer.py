"""
Unit tests for ConflictAnalyzer (Framework 5 + OD-04 + OD-05)
TEST EVIDENCE — NOT YET QA APPROVED
"""
import pytest
from app.reasoning.conflict_analyzer import (
    ConflictAnalyzer,
    ConflictSeverity,
    ResolutionState,
)


@pytest.fixture
def analyzer():
    return ConflictAnalyzer()


def test_critical_fields(analyzer):
    for field in ["brand", "product_name", "barcode_gtin", "market_region"]:
        assert analyzer.determine_severity(field) == ConflictSeverity.CRITICAL


def test_high_fields(analyzer):
    for field in ["variant", "size_value", "size_unit", "country_of_origin"]:
        assert analyzer.determine_severity(field) == ConflictSeverity.HIGH


def test_medium_fields(analyzer):
    for field in ["claim", "general", "notes"]:
        assert analyzer.determine_severity(field) == ConflictSeverity.MEDIUM


def test_low_field_default(analyzer):
    assert analyzer.determine_severity("some_other_field") == ConflictSeverity.LOW


def test_empty_field_is_low(analyzer):
    assert analyzer.determine_severity("") == ConflictSeverity.LOW
    assert analyzer.determine_severity(None) == ConflictSeverity.LOW


def test_analyze_preserves_all_values(analyzer):
    values = ["SPF 30", "SPF 50", "SPF 30+"]
    result = analyzer.analyze(
        product_id="P001",
        field="spf",
        conflicting_values=values,
    )
    assert result["conflicting_values"] == values
    assert result["resolution_state"] == ResolutionState.UNRESOLVED.value
    assert result["product_id"] == "P001"
    assert "detected_at" in result


def test_analyze_critical_sets_auto_resolution_false(analyzer):
    result = analyzer.analyze("P001", "brand", ["A", "B"])
    assert result["severity"] == "CRITICAL"
    assert result["auto_resolution_allowed"] is False


def test_analyze_medium_sets_auto_resolution_true(analyzer):
    result = analyzer.analyze("P001", "claim", ["X", "Y"])
    assert result["severity"] == "MEDIUM"
    assert result["auto_resolution_allowed"] is True


def test_can_auto_resolve_medium_and_low(analyzer):
    assert analyzer.can_auto_resolve("MEDIUM") is True
    assert analyzer.can_auto_resolve("LOW") is True


def test_cannot_auto_resolve_high_and_critical(analyzer):
    assert analyzer.can_auto_resolve("HIGH") is False
    assert analyzer.can_auto_resolve("CRITICAL") is False


def test_manual_resolution_high_allowed(analyzer):
    conflict = analyzer.analyze("P001", "variant", ["V1", "V2"])
    resolved = analyzer.attempt_resolution(
        conflict,
        resolution_rationale="PO decided V1 is correct",
        force_manual=True,
    )
    assert resolved["resolution_state"] == ResolutionState.RESOLVED.value
    assert "PO decided" in resolved["resolution_rationale"]
    assert "resolved_at" in resolved


def test_auto_resolution_high_forbidden(analyzer):
    conflict = analyzer.analyze("P001", "variant", ["V1", "V2"])
    with pytest.raises(ValueError, match="Auto-resolution is forbidden"):
        analyzer.attempt_resolution(
            conflict, resolution_rationale="auto pick", force_manual=False
        )


def test_resolution_requires_rationale(analyzer):
    conflict = analyzer.analyze("P001", "claim", ["A", "B"])
    with pytest.raises(ValueError, match="resolution_rationale is mandatory"):
        analyzer.attempt_resolution(
            conflict, resolution_rationale="   ", force_manual=True
        )


def test_get_unresolved(analyzer):
    analyzer.analyze("P001", "brand", ["A", "B"])
    analyzer.analyze("P002", "claim", ["X", "Y"])
    unresolved = analyzer.get_unresolved()
    assert len(unresolved) == 2
    only_p001 = analyzer.get_unresolved(product_id="P001")
    assert len(only_p001) == 1
    assert only_p001[0]["product_id"] == "P001"
