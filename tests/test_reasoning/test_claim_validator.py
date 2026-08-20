"""
Unit tests for ClaimValidator (Framework 4)
TEST EVIDENCE — NOT YET QA APPROVED
"""
import pytest
from app.reasoning.claim_validator import ClaimValidator


@pytest.fixture
def validator():
    return ClaimValidator()


def test_unknown_to_fact_forbidden(validator):
    result = validator.validate_promotion("UNKNOWN", "FACT")
    assert result["allowed"] is False
    assert "Framework 4" in result["reason"]


def test_unknown_to_evidence_supported_forbidden(validator):
    result = validator.validate_promotion("UNKNOWN", "EVIDENCE_SUPPORTED")
    assert result["allowed"] is False


def test_unknown_to_manufacturer_claim_forbidden(validator):
    result = validator.validate_promotion("UNKNOWN", "MANUFACTURER_CLAIM")
    assert result["allowed"] is False


def test_unknown_to_inference_forbidden(validator):
    result = validator.validate_promotion("UNKNOWN", "INFERENCE")
    assert result["allowed"] is False


def test_inference_to_fact_forbidden(validator):
    result = validator.validate_promotion("INFERENCE", "FACT")
    assert result["allowed"] is False
    assert "Framework 4" in result["reason"]


def test_manufacturer_claim_to_fact_forbidden(validator):
    result = validator.validate_promotion("MANUFACTURER_CLAIM", "FACT")
    assert result["allowed"] is False
    assert "Framework 4" in result["reason"]


def test_evidence_supported_to_fact_with_less_than_2_strong_forbidden(validator):
    result = validator.validate_promotion(
        "EVIDENCE_SUPPORTED", "FACT", evidence_strengths=["STRONG"]
    )
    assert result["allowed"] is False
    assert "multiple STRONG" in result["reason"]


def test_evidence_supported_to_fact_with_zero_strong_forbidden(validator):
    result = validator.validate_promotion(
        "EVIDENCE_SUPPORTED", "FACT", evidence_strengths=["MODERATE", "WEAK"]
    )
    assert result["allowed"] is False


def test_evidence_supported_to_fact_with_2_strong_allowed(validator):
    result = validator.validate_promotion(
        "EVIDENCE_SUPPORTED", "FACT", evidence_strengths=["STRONG", "STRONG"]
    )
    assert result["allowed"] is True
    assert result["reason"] is None


def test_evidence_supported_to_fact_with_3_strong_allowed(validator):
    result = validator.validate_promotion(
        "EVIDENCE_SUPPORTED",
        "FACT",
        evidence_strengths=["STRONG", "STRONG", "MODERATE"],
    )
    assert result["allowed"] is True


def test_fact_to_fact_allowed(validator):
    result = validator.validate_promotion("FACT", "FACT")
    assert result["allowed"] is True


def test_manufacturer_claim_to_evidence_supported_allowed(validator):
    result = validator.validate_promotion("MANUFACTURER_CLAIM", "EVIDENCE_SUPPORTED")
    assert result["allowed"] is True


def test_none_input_treated_as_unknown(validator):
    result = validator.validate_promotion(None, "FACT")
    assert result["allowed"] is False
    assert result["from_type"] == "UNKNOWN"


def test_check_list_returns_only_violations(validator):
    claims = [
        {"claim_type": "UNKNOWN", "target_type": "FACT"},
        {"claim_type": "FACT", "target_type": "FACT"},
        {"claim_type": "INFERENCE", "target_type": "FACT"},
    ]
    violations = validator.check_list(claims)
    assert len(violations) == 2
    for v in violations:
        assert v["allowed"] is False


def test_check_list_empty(validator):
    assert validator.check_list([]) == []
