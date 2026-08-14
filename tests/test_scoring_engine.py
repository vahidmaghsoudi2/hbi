"""test_scoring_engine.py - Unit tests for MatchScoringEngine"""
import sys
from pathlib import Path
PROJECT = Path("E:/HBI")
sys.path.insert(0, str(PROJECT))

from app.reasoning.scoring import MatchScoringEngine
from app.reasoning.scoring_constants import (
    ELIGIBILITY_ELIGIBLE, ELIGIBILITY_NEEDS_REVIEW, ELIGIBILITY_INELIGIBLE,
)
engine = MatchScoringEngine()

def test_normal_eligible():
    r = engine.calculate(0.9, 0.8, 1.0)
    assert r["final_score"] == 0.89
    assert r["eligibility"] == ELIGIBILITY_ELIGIBLE

def test_hard_gate_no_evidence():
    r = engine.calculate(0.9, 0.0, 1.0)
    assert r["final_score"] == 0.65
    assert r["eligibility"] == ELIGIBILITY_NEEDS_REVIEW
    assert r["hard_gate_triggered"] is True

def test_hard_gate_no_inventory():
    r = engine.calculate(0.9, 0.8, 0.0)
    assert r["final_score"] == 0.69
    assert r["eligibility"] == ELIGIBILITY_NEEDS_REVIEW

def test_ineligible():
    r = engine.calculate(0.2, 0.3, 0.5)
    assert r["final_score"] == 0.29
    assert r["eligibility"] == ELIGIBILITY_INELIGIBLE

def test_threshold_boundary():
    r = engine.calculate(0.7, 0.7, 1.0)
    assert r["final_score"] == 0.76
    assert r["eligibility"] == ELIGIBILITY_ELIGIBLE

def test_confidence():
    r = engine.calculate(0.8, 0.7, 1.0)
    assert r["confidence"] == 0.74

def test_clamping():
    r = engine.calculate(1.0, 1.0, 1.0)
    assert r["final_score"] == 1.0
    assert r["confidence"] == 1.0
