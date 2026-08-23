"""Controlled EVIDENCE_MISSING — hard-gate behavior (no threshold changes, no invented evidence)."""
from app.reasoning.scoring import MatchScoringEngine
from app.reasoning.scoring_constants import (
    WARNING_EVIDENCE_MISSING,
    WARNING_HARD_GATE_ACTIVE,
    ELIGIBILITY_NEEDS_REVIEW,
)


def test_evidence_score_zero_triggers_hard_gate():
    engine = MatchScoringEngine()
    result = engine.calculate(
        need_match=1.0,
        evidence_score=0.0,
        inventory_score=1.0,
    )
    assert result["hard_gate_triggered"] is True
    assert WARNING_EVIDENCE_MISSING in result["hard_gate_reasons"]
    assert WARNING_HARD_GATE_ACTIVE in result["warnings"]
    assert result["eligibility"] == ELIGIBILITY_NEEDS_REVIEW


def test_positive_evidence_score_clears_evidence_hard_gate():
    engine = MatchScoringEngine()
    result = engine.calculate(
        need_match=1.0,
        evidence_score=0.2,  # SECONDARY weight — not invented clinical strength
        inventory_score=1.0,
    )
    assert result["hard_gate_triggered"] is False
    assert WARNING_EVIDENCE_MISSING not in result["hard_gate_reasons"]
