import pytest
from app.reasoning.claim_validator import ClaimValidator
from app.reasoning.conflict_analyzer import ConflictAnalyzer, ConflictSeverity
from app.reasoning.reasoning_engine import ReasoningEngine

# ---------- ClaimValidator ----------
def test_claim_validator_forbid_unknown_to_fact():
    validator = ClaimValidator()
    result = validator.validate_promotion("UNKNOWN", "FACT")
    assert result["allowed"] is False

def test_claim_validator_forbid_inference_to_fact():
    validator = ClaimValidator()
    result = validator.validate_promotion("INFERENCE", "FACT")
    assert result["allowed"] is False

def test_claim_validator_evidence_supported_needs_two_strong():
    validator = ClaimValidator()
    result = validator.validate_promotion("EVIDENCE_SUPPORTED", "FACT", evidence_strengths=["STRONG"])
    assert result["allowed"] is False

def test_claim_validator_evidence_supported_two_strong_allowed():
    validator = ClaimValidator()
    result = validator.validate_promotion(
        "EVIDENCE_SUPPORTED", "FACT", evidence_strengths=["STRONG", "STRONG"]
    )
    assert result["allowed"] is True

def test_claim_validator_check_list_returns_violations():
    validator = ClaimValidator()
    violations = validator.check_list([
        {"claim_type": "INFERENCE", "target_type": "FACT", "evidence_strengths": []}
    ])
    assert len(violations) == 1
    assert violations[0]["reason"] is not None

# ---------- ConflictAnalyzer ----------
def test_conflict_analyzer_determine_severity_critical():
    analyzer = ConflictAnalyzer()
    assert analyzer.determine_severity("brand") == ConflictSeverity.CRITICAL

def test_conflict_analyzer_determine_severity_high():
    analyzer = ConflictAnalyzer()
    assert analyzer.determine_severity("variant") == ConflictSeverity.HIGH

def test_conflict_analyzer_auto_resolve_policy():
    analyzer = ConflictAnalyzer()
    assert analyzer.can_auto_resolve(ConflictSeverity.CRITICAL.value) is False
    assert analyzer.can_auto_resolve(ConflictSeverity.HIGH.value) is False
    assert analyzer.can_auto_resolve(ConflictSeverity.MEDIUM.value) is True
    assert analyzer.can_auto_resolve(ConflictSeverity.LOW.value) is True

def test_conflict_analyzer_analyze_returns_structure():
    analyzer = ConflictAnalyzer()
    result = analyzer.analyze(
        product_id="P1",
        field="brand",
        conflicting_values=["A", "B"],
        evidence_refs=[{"evidence_id": "e1"}],
        sources=["S1"],
    )
    assert result["severity"] == ConflictSeverity.CRITICAL.value
    assert result["auto_resolution_allowed"] is False
    assert result["resolution_state"] == "UNRESOLVED"

def test_conflict_analyzer_manual_resolution_for_high():
    analyzer = ConflictAnalyzer()
    conflict = analyzer.analyze(
        product_id="P1",
        field="brand",
        conflicting_values=["A", "B"],
    )
    resolved = analyzer.attempt_resolution(
        conflict,
        resolution_rationale="Manual review by PO",
        force_manual=True,
    )
    assert resolved["resolution_state"] == "RESOLVED"
    assert resolved["resolution_rationale"] == "Manual review by PO"

def test_conflict_analyzer_auto_resolution_forbidden_for_high():
    analyzer = ConflictAnalyzer()
    conflict = analyzer.analyze(
        product_id="P1",
        field="brand",
        conflicting_values=["A", "B"],
    )
    with pytest.raises(ValueError):
        analyzer.attempt_resolution(
            conflict,
            resolution_rationale="auto",
            force_manual=False,
        )

# ---------- ReasoningEngine ----------
def test_reasoning_engine_basic_result_computed_only():
    engine = ReasoningEngine()
    result = engine.run(product_id="P1")
    assert result["product_id"] == "P1"
    assert "claim_boundary_violations" in result
    assert "conflicts" in result
    assert result["persistence"] == "COMPUTED_ONLY"

def test_reasoning_engine_detects_claim_boundary_violation():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="P1",
        evidence_list=[
            {
                "evidence_id": "e1",
                "claim_type": "INFERENCE",
                "target_type": "FACT",
            }
        ],
    )
    assert len(result["claim_boundary_violations"]) > 0

def test_reasoning_engine_detects_critical_conflict():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="P1",
        existing_conflicts=[{"field": "brand", "values": ["A", "B"]}],
    )
    assert any(c["severity"] == "CRITICAL" for c in result["conflicts"])

def test_reasoning_engine_surfaces_unknown():
    engine = ReasoningEngine()
    result = engine.run(
        product_id="P1",
        evidence_list=[{"evidence_id": "e1", "claim_type": "UNKNOWN", "field": "brand"}],
    )
    assert any(u["action"] == "ESCALATE_PO" for u in result["unknowns"])
